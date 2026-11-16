"""Native Grease Pencil contours on alpha; Blender 4.3+ and 5.x, headless.

blender -b --python-exit-code 1 -P lineart_render.py -- --model cup.glb \
    --angle top --size detail --move push-in --out renders/cup

No dependencies outside Blender. Imported mesh materials/animation are discarded.
Native Line Art is baked before hiding source meshes from the render graph.
"""
import argparse
import hashlib
import itertools
import json
import math
import shutil
import sys
import traceback
from pathlib import Path

import bpy
import bmesh
import numpy as np
from mathutils import Matrix, Quaternion, Vector
from bpy_extras.object_utils import world_to_camera_view

WIDTH, HEIGHT, FPS = 1080, 1920, 30
PITCH = dict(top=90., high=45., eye=0., low=-25.)
FILL = dict(wide=.35, medium=.60, detail=.85)
LENS = dict(wide=24., ultrawide=13.)
FORMATS = {'.blend', '.glb', '.gltf', '.obj', '.fbx'}


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--angle', required=True, choices=PITCH)
    parser.add_argument('--size', required=True, choices=FILL)
    parser.add_argument('--lens', default='wide', choices=LENS)
    parser.add_argument('--move', default='none', choices=['none','push-in','pull-out','pan','tilt','orbit'])
    parser.add_argument('--duration', default=3., type=float)
    parser.add_argument('--hidden', action='store_true')
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    args.model = args.model.expanduser().resolve()
    args.out = args.out.expanduser().resolve()
    if not args.model.is_file():parser.error('Missing model: '+str(args.model))
    if args.model.suffix.lower() not in FORMATS:parser.error('Unsupported model format: '+args.model.suffix)
    if not math.isfinite(args.duration) or args.duration <= 0:parser.error('--duration must be a finite positive number')
    if args.move != 'none' and round(args.duration*FPS) <= 15:parser.error('Animated duration must exceed the 0.5 second final hold')
    if bpy.app.version < (4,3,0):parser.error('This renderer requires the modern Grease Pencil API in Blender 4.3 or newer')
    return args


def import_meshes(path, scene):
    if path.suffix.lower() == '.blend':
        with bpy.data.libraries.load(str(path), link=False) as (source, target):
            target.objects = source.objects
        for obj in target.objects:
            if obj is not None:scene.collection.objects.link(obj)
    elif path.suffix.lower() in {'.glb','.gltf'}:
        bpy.ops.import_scene.gltf(filepath=str(path))
    elif path.suffix.lower() == '.obj':
        bpy.ops.wm.obj_import(filepath=str(path))
    else:
        bpy.ops.import_scene.fbx(filepath=str(path))
    scene.frame_set(1)
    for obj in scene.objects:
        obj.hide_viewport = False
        obj.hide_set(False)
    bpy.context.view_layer.update()
    meshes = [o for o in scene.objects if o.type == 'MESH' and len(o.data.vertices)]
    if not meshes:raise ValueError('No mesh found in '+str(path))
    # Realize evaluated geometry in world space before discarding parent transforms.
    # This retains GLTF axis conversions and calibrated .blend asset roots.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    originals=list(bpy.data.objects);copies = []
    for obj in meshes:
        evaluated = obj.evaluated_get(depsgraph)
        data = bpy.data.meshes.new_from_object(evaluated, depsgraph=depsgraph)
        data.transform(evaluated.matrix_world)
        data.materials.clear()
        copy = bpy.data.objects.new('Source / '+obj.name, data)
        copies.append(copy)
    for obj in originals:bpy.data.objects.remove(obj, do_unlink=True)
    collection = bpy.data.collections.new('Line Art source meshes')
    scene.collection.children.link(collection)
    for obj in copies:collection.objects.link(obj)
    bpy.context.view_layer.update()
    return copies, collection


def evaluated_bounds(meshes):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    lo = Vector((math.inf,)*3);hi = Vector((-math.inf,)*3)
    for obj in meshes:
        evaluated = obj.evaluated_get(depsgraph)
        for corner in evaluated.bound_box:
            point = evaluated.matrix_world @ Vector(corner)
            for axis in range(3):lo[axis]=min(lo[axis],point[axis]);hi[axis]=max(hi[axis],point[axis])
    if not all(math.isfinite(v) for v in (*lo,*hi)) or max(hi-lo) <= 1e-8:
        raise ValueError('Model has an empty or degenerate bounding box')
    return lo, hi


def prepare_meshes(meshes):
    lo, hi = evaluated_bounds(meshes)
    shift = Vector((-(lo.x+hi.x)/2, -(lo.y+hi.y)/2, -lo.z))
    for obj in meshes:
        obj.data.transform(Matrix.Translation(shift))
        obj.matrix_world = Matrix.Identity(4)
    width = max(hi-lo)*.002
    for obj in meshes:
        # OBJ/GLTF exporters can duplicate vertices at normal or UV seams. Those
        # disconnected face borders otherwise become unwanted contour wires.
        original_count=len(obj.data.vertices)
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        bmesh.ops.remove_doubles(mesh,verts=list(mesh.verts),dist=max(hi-lo)*1e-6)
        bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces))
        for edge in mesh.edges:edge.smooth=True
        mesh.to_mesh(obj.data);mesh.free()
        obj['coincident_vertices_welded']=original_count-len(obj.data.vertices)
        obj.data.polygons.foreach_set('use_smooth', [True]*len(obj.data.polygons))
        bevel = obj.modifiers.new('Small two-segment contour bevel', 'BEVEL')
        bevel.width=width;bevel.segments=2;bevel.limit_method='ANGLE';bevel.angle_limit=math.radians(30)
        bevel.use_clamp_overlap=True
        normal = obj.modifiers.new('Clean weighted normals', 'WEIGHTED_NORMAL')
        normal.keep_sharp=True;normal.weight=50
        obj.hide_render=False;obj.hide_viewport=False
    bpy.context.view_layer.update()
    lo, hi = evaluated_bounds(meshes)
    return lo, hi, width


def pose(center, distance, pitch):
    angle = math.radians(pitch)
    position = center+Vector((0.,-distance*math.cos(angle),distance*math.sin(angle)))
    rotation = (center-position).to_track_quat('-Z','Y')
    return position, rotation


def framing_distance(center, lo, hi, pitch, fraction, fov_y):
    corners = [Vector(p) for p in itertools.product(*zip(lo,hi))]
    _, rotation = pose(center, 1., pitch)
    up = rotation @ Vector((0,1,0));back = rotation @ Vector((0,0,1))
    values = [(float((p-center).dot(up)),float((p-center).dot(back))) for p in corners]
    tangent = math.tan(fov_y/2)
    def span(distance):
        ys = [y/(2*tangent*(distance-z)) for y,z in values]
        return max(ys)-min(ys)
    near = max(z for _,z in values)+max(1e-7,max(hi-lo)*1e-7)
    far = max(near*2, max(hi-lo))
    while span(far)>fraction:far*=2
    for _ in range(80):
        middle=(near+far)/2
        if span(middle)>fraction:near=middle
        else:far=middle
    return far, corners


def camera_setup(scene, args, lo, hi):
    data=bpy.data.cameras.new('Phone / fixed lens');camera=bpy.data.objects.new('Phone camera',data)
    scene.collection.objects.link(camera);scene.camera=camera
    data.type='PERSP';data.lens=LENS[args.lens]
    # Portrait rotation of a 36 mm full-frame gate: the long sensor side is vertical.
    data.sensor_fit='VERTICAL';data.sensor_width=36.;data.sensor_height=36.
    data.clip_start=.001
    center=(lo+hi)/2;fov_y=2*math.atan(data.sensor_height/(2*data.lens))
    ideal,corners=framing_distance(center,lo,hi,PITCH[args.angle],FILL[args.size],fov_y)
    minimum=.15 if args.lens=='wide' else 0.
    distance=max(ideal,minimum)
    data.clip_end=max(100., distance*100, max(hi-lo)*100)
    count=1 if args.move=='none' else round(args.duration*FPS)
    final_hold=0 if count==1 else 15
    motion_end=1 if count==1 else count-final_hold+1
    scene.frame_start=1;scene.frame_end=count
    pivot=None
    if args.move=='orbit':
        pivot=bpy.data.objects.new('Orbit / object center',None);scene.collection.objects.link(pivot)
        pivot.location=center;camera.parent=pivot
        camera.location,camera.rotation_quaternion=pose(Vector(),distance,PITCH[args.angle])
        camera.rotation_mode='QUATERNION'
    previous=None;frames=[]
    for number in range(1,count+1):
        t=0. if count==1 else min(1.,(number-1)/(motion_end-1))
        d=distance*(1.6-.6*t) if args.move=='push-in' else distance*(1.+.6*t) if args.move=='pull-out' else distance
        pitch=20.+(PITCH[args.angle]-20.)*t if args.move=='tilt' else PITCH[args.angle]
        position,rotation=pose(center,d,pitch)
        if pivot:
            pivot.rotation_euler.z=math.radians(90*t);pivot.keyframe_insert('rotation_euler',index=2,frame=number)
        else:
            if args.move=='pan':rotation=rotation @ Quaternion(Vector((0,1,0)),math.radians(-22.5+45*t))
            if previous and previous.dot(rotation)<0:rotation.negate()
            camera.location=position;camera.rotation_mode='QUATERNION';camera.rotation_quaternion=rotation;previous=rotation.copy()
            if count>1:camera.keyframe_insert('location',frame=number);camera.keyframe_insert('rotation_quaternion',frame=number)
        scene.frame_set(number);bpy.context.view_layer.update()
        projected=[world_to_camera_view(scene,camera,p) for p in corners]
        xs=[float(p.x) for p in projected];ys=[float(p.y) for p in projected]
        bounds=dict(x_min=min(xs),x_max=max(xs),y_min=min(ys),y_max=max(ys))
        coords=camera.matrix_world.translation
        frames.append(dict(frame=number,time_s=(number-1)/FPS,camera_position=list(coords),
            camera_rotation_quaternion=list(camera.matrix_world.to_quaternion()),camera_distance=(coords-center).length,
            bbox_frame=bounds,bbox_frame_origin='bottom_left',height_fraction=max(ys)-min(ys),
            bbox_pixels_top_left=[min(xs)*WIDTH,(1-max(ys))*HEIGHT,max(xs)*WIDTH,(1-min(ys))*HEIGHT],
            fits_frame=min(xs)>=0 and max(xs)<=1 and min(ys)>=0 and max(ys)<=1 and min(p.z for p in projected)>0))
    # All inserted keys are linear, including the constant tail; no object animation.
    for obj in [camera,pivot]:
        if not obj or not obj.animation_data:continue
        action=obj.animation_data.action
        curves=getattr(action,'fcurves',None)
        if curves is None:
            slot=obj.animation_data.action_slot
            curves=[fc for layer in action.layers for strip in layer.strips for fc in strip.channelbag(slot).fcurves]
        for curve in curves:
            for key in curve.keyframe_points:key.interpolation='LINEAR'
    return camera,center,distance,ideal,fov_y,frames,motion_end,final_hold


def stroke_material(name,color):
    material=bpy.data.materials.new(name);bpy.data.materials.create_gpencil_data(material)
    material.grease_pencil.color=color;material.grease_pencil.show_stroke=True;material.grease_pencil.show_fill=False
    return material


def strokes_setup(scene,collection,args,distance,fov_y,motion_end):
    # Operator creates the appropriate modern GP datablock on 4.3 and 5.x.
    bpy.ops.object.grease_pencil_add(type='LINEART_SCENE')
    obj=bpy.context.object;obj.name='Scene Line Art';obj.show_in_front=True
    for mod in list(obj.modifiers):obj.modifiers.remove(mod)
    for layer in list(obj.data.layers):obj.data.layers.remove(layer)
    obj.data.materials.clear()
    if hasattr(obj.data,'stroke_depth_order'):obj.data.stroke_depth_order='2D'
    black=stroke_material('Black / 55 percent underlay',(0,0,0,.55))
    white=stroke_material('White contours',(1,1,1,1))
    obj.data.materials.append(black);obj.data.materials.append(white)
    styles=[]
    if args.hidden:styles += [('Hidden Underlay',2.5,black,.5,1,2),('Hidden',1.5,white,.5,1,2)]
    styles += [('Underlay',5.,black,1.,0,0),('Contours',3.,white,1.,0,0)]
    for name,width,material,opacity,start,end in styles:
        layer=obj.data.layers.new(name,set_active=True);layer.use_lights=False;layer.opacity=opacity
        mod=obj.modifiers.new(name+' / native visible-edge extraction','LINEART')
        mod.source_type='COLLECTION';mod.source_collection=collection
        mod.target_layer=name;mod.target_material=material
        mod.use_contour=True;mod.use_crease=not getattr(args,'contour_only',False);mod.crease_threshold=math.radians(140)
        mod.use_intersection=not getattr(args,'skip_intersections',False);mod.use_material=False;mod.use_edge_mark=False;mod.use_loose=False
        mod.use_crease_on_smooth=True;mod.use_crease_on_sharp=False
        mod.use_light_contour=False;mod.use_shadow=False
        if hasattr(mod,'fill_strokes'):mod.fill_strokes=False
        mod.use_multiple_levels=end>start;mod.level_start=start;mod.level_end=end
        mod.radius=width*distance*math.tan(fov_y/2)/HEIGHT;mod.opacity=1.
        mod.stroke_depth_offset=0.
    scene.frame_set(1);bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.object.lineart_bake_strokes(bake_all=False)
    if not all(m.is_baked for m in obj.modifiers if m.type=='LINEART'):raise RuntimeError('Native Line Art baking did not complete')
    # Keep one drawing for the stationary tail. Re-extracting identical geometry
    # can reorder curves and alter a noise seed even when the camera is still.
    for layer in obj.data.layers:
        for frame in list(layer.frames):
            if frame.frame_number>motion_end:layer.frames.remove(frame.frame_number)
    # A radius in world units would grow during a push-in. Set a camera-depth
    # dependent radius on every baked point so the requested pixel widths stay fixed.
    widths={name:width for name,width,*_ in styles};counts={}
    for layer in obj.data.layers:
        counts[layer.name]=0
        for frame in layer.frames:
            scene.frame_set(frame.frame_number);bpy.context.view_layer.update()
            drawing=frame.drawing;position=drawing.attributes.get('position')
            if position is None:continue
            coordinates=np.empty((len(position.data),3),dtype=np.float32)
            position.data.foreach_get('vector',coordinates.ravel())
            inverse=np.asarray(scene.camera.matrix_world.inverted(),dtype=np.float64)
            depth=-(coordinates@inverse[2,:3]+inverse[2,3])
            radius=np.maximum(depth,.00001)*widths[layer.name]*math.tan(fov_y/2)/HEIGHT
            attr=drawing.attributes.get('radius') or drawing.attributes.new('radius','FLOAT','POINT')
            attr.data.foreach_set('value',radius.astype(np.float32))
            for stroke in drawing.strokes:
                stroke.start_cap=0;stroke.end_cap=0;stroke.fill_opacity=0
            counts[layer.name]+=len(drawing.strokes)
    if not counts.get('Contours'):raise RuntimeError('Line Art produced no visible contours')
    if args.hidden:
        for name in ['Hidden Underlay','Hidden']:
            mod=obj.modifiers.new(name+' / dashed occluded edges','GREASE_PENCIL_DASH')
            if hasattr(mod,'tree_node_filter'):mod.tree_node_filter=name
            else:mod.layer_filter=name
            segment=mod.segments[0];segment.dash=8;segment.gap=6;segment.radius=1.;segment.opacity=1.
    noise=obj.modifiers.new('Very subtle static pencil variation','GREASE_PENCIL_NOISE')
    noise.factor=distance*2*math.tan(fov_y/2)/HEIGHT*.1
    noise.factor_strength=0.;noise.factor_thickness=0.;noise.factor_uvs=0.;noise.use_random=False;noise.seed=7
    obj.data.update_tag()
    return obj,counts


def run(args):
    if args.model==args.out/'scene.blend':raise ValueError('Output scene.blend would overwrite the input model; choose another --out directory')
    if any(args.out.glob('frame_*.png')):raise ValueError('Output directory already contains frames; use a fresh --out directory')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene;scene.name='Transparent native Line Art'
    meshes,collection=import_meshes(args.model,scene)
    lo,hi,bevel=prepare_meshes(meshes)
    engines={item.identifier for item in scene.render.bl_rna.properties['engine'].enum_items}
    scene.render.engine='BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engines else 'BLENDER_EEVEE'
    scene.render.resolution_x=WIDTH;scene.render.resolution_y=HEIGHT;scene.render.resolution_percentage=100
    scene.render.fps=FPS;scene.render.fps_base=1.;scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8'
    scene.render.use_compositing=False;scene.render.use_sequencer=False
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    if hasattr(scene,'eevee'):scene.eevee.taa_render_samples=32
    scene.world=None
    camera,center,distance,ideal,fov_y,frames,motion_end,hold=camera_setup(scene,args,lo,hi)
    obj,counts=strokes_setup(scene,collection,args,distance,fov_y,motion_end)
    for mesh in meshes:mesh.hide_render=True
    args.out.mkdir(parents=True,exist_ok=True)
    scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(args.out/'scene.blend'),compress=True)
    for row in frames:
        scene.frame_set(row['frame']);scene.render.filepath=str(args.out/f'frame_{row["frame"]:04d}.png')
        if row['frame']>motion_end:
            shutil.copyfile(args.out/f'frame_{motion_end:04d}.png',scene.render.filepath)
        else:bpy.ops.render.render(write_still=True)
    # Independent isolation check: hiding strokes must leave a completely empty
    # render, proving that no imported geometry or shaded surface leaked through.
    obj.hide_render=True;scene.render.filepath=str(args.out/'no_strokes_alpha_check.png')
    bpy.ops.render.render(write_still=True)
    image=bpy.data.images.load(scene.render.filepath,check_existing=False)
    pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels)
    maximum=float(pixels.reshape(-1,4)[:,3].max());bpy.data.images.remove(image)
    if maximum!=0:raise RuntimeError('Mesh surface leaked into the alpha render')
    (args.out/'no_strokes_alpha_check.png').unlink();obj.hide_render=False
    final=frames[-1]
    meta=dict(status='complete',model=str(args.model),model_sha256=hashlib.sha256(args.model.read_bytes()).hexdigest(),
        renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        blender_version=bpy.app.version_string,resolution=[WIDTH,HEIGHT],fps=FPS,frame_count=len(frames),
        duration_s=len(frames)/FPS,requested_duration_s=args.duration,angle=args.angle,pitch_degrees=PITCH[args.angle],
        size=args.size,requested_height_fraction=FILL[args.size],lens=args.lens,lens_mm=LENS[args.lens],
        sensor_mm=36.,sensor_fit='VERTICAL',sensor_height_mm=36.,fov_y_degrees=math.degrees(fov_y),
        move=args.move,final_camera_distance=final['camera_distance'],size_camera_distance=distance,
        unconstrained_size_camera_distance=ideal,minimum_focus_distance=.15 if args.lens=='wide' else 0,
        minimum_focus_limited=distance>ideal+1e-7,final_hold_frames=hold,final_hold_s=hold/FPS,motion_end_frame=motion_end,
        hold_reuses_identical_drawing_and_pixels=True,
        object_bbox_world=dict(min=list(lo),max=list(hi),center=list(center)),bbox_frame=final['bbox_frame'],
        bbox_frame_origin='bottom_left',bbox_pixels_top_left=final['bbox_pixels_top_left'],
        actual_final_height_fraction=final['height_fraction'],fits_frame=final['fits_frame'],
        every_frame_fits=all(f['fits_frame'] for f in frames),frames=frames,
        strokes=dict(white_px=3.,underlay_px=5.,underlay_opacity=.55,hidden=args.hidden,hidden_px=1.5,
            hidden_opacity=.5,visible_occlusion=[0,0],hidden_occlusion=[1,2] if args.hidden else None,
            contour=True,crease=True,crease_threshold_degrees=140,intersection=True,material_border=False,
            edge_mark=False,loose=False,round_caps=True,fill=False,noise='static, approximately 0.1 pixel',native_baked_strokes=counts),
        meshes=dict(count=len(meshes),materials=0,render_visible=False,viewport_visible=True,bevel_segments=2,bevel_width=bevel,
            coincident_vertices_welded=sum(o['coincident_vertices_welded'] for o in meshes)),
        surface_isolation_check=dict(status='passed',max_alpha_without_strokes=maximum),
        framing_note='Height fraction is solved from the perspective projection of all eight bounding-box corners; horizontal cropping is reported, not silently reframed. Wide minimum-focus clamp takes priority.')
    (args.out/'meta.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(f'LINEART_OK frames={len(frames)} lens={LENS[args.lens]:g}mm distance={final["camera_distance"]:.6f}m transparent_surfaces=true out={args.out}',flush=True)


if __name__=='__main__':
    try:run(arguments())
    except BaseException as error:
        if isinstance(error,SystemExit) and error.code in (None,0):raise
        print('LINEART_ERROR: '+str(error),file=sys.stderr,flush=True)
        if not isinstance(error,SystemExit):traceback.print_exc()
        # Blender normally exits 0 for Python errors unless --python-exit-code was
        # supplied. Explicit SystemExit preserves the requested failure status.
        raise SystemExit(2)
