"""Native P0 target-first scene renderer, reusing the verified Grease Pencil setup."""
import argparse,hashlib,itertools,json,math,shutil,sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/'guides/tools'))
sys.path.insert(0,str(ROOT/'model_refferences/objects/tools'))
import p0_catalog
import p0_scenes as P
import lineart_render as L

L.WIDTH,L.HEIGHT,L.FPS=405,720,15


def corners(objects):
    deps=bpy.context.evaluated_depsgraph_get()
    return [obj.matrix_world@Vector(corner) for obj in objects for corner in obj.evaluated_get(deps).bound_box]


def aim(camera,position,target,up=None):
    camera.location=position;camera.rotation_mode='QUATERNION'
    direction=(target-position).normalized()
    if up is None:camera.rotation_quaternion=direction.to_track_quat('-Z','Y')
    else:
        # A fixed screen-up reference avoids the vertical tracking singularity
        # when a continuous shot finishes directly above a tabletop.
        right=direction.cross(Vector(up)).normalized()
        if right.length<.5:raise ValueError('Camera up reference is parallel to the viewing direction')
        screen_up=right.cross(direction).normalized()
        camera.rotation_quaternion=Matrix((right,screen_up,-direction)).transposed().to_quaternion()
    bpy.context.view_layer.update()


def projection(scene,camera,points):
    p=[world_to_camera_view(scene,camera,v) for v in points]
    return dict(x_min=min(v.x for v in p),x_max=max(v.x for v in p),y_min=min(v.y for v in p),y_max=max(v.y for v in p))


def key_objects(scene,frame):
    for obj in scene.objects:
        if obj.type!='MESH' and obj.type!='EMPTY':continue
        # Bake actual object action transforms, retaining parent/contact relationships.
        obj.keyframe_insert('location',frame=frame);obj.keyframe_insert('rotation_euler',frame=frame)


def run(args):
    data=p0_catalog.registry()
    if args.record:
        # A draft guide renders from its own record and stays out of the registry until it is approved.
        record=json.loads(args.record.read_text());assert record['id']==args.id,(record['id'],args.id)
    else:
        record=next(g for g in data['guides'] if g['id']==args.id)
    if record.get('availability')=='deferred':raise ValueError('Person guide is deferred: '+args.id)
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    if (out/'meta.json').exists() and not args.replace:raise ValueError('Completed output exists; pass --replace to update the same guide in place')
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene
    scene.name='P0 / '+args.id;scene.render.engine='BLENDER_EEVEE'
    scene.render.resolution_x=405;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    scene.render.fps=15;scene.render.film_transparent=True;scene.render.use_compositing=False;scene.render.use_sequencer=False
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.image_settings.color_depth='8'
    scene.eevee.taa_render_samples=16
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.world=None
    state=P.build(args.id,record)
    lens=state.get('lens_mm',24)
    P.lighting_cues(scene,state)
    camera=bpy.data.objects.new('Visitor phone',bpy.data.cameras.new('Fixed 24 mm phone lens'))
    scene.collection.objects.link(camera);scene.camera=camera
    camera.data.lens=lens;camera.data.sensor_fit='VERTICAL';camera.data.sensor_width=camera.data.sensor_height=36
    camera.data.clip_start=.008;camera.data.clip_end=100
    p,t=state['target_position'],state['target_aim'];original=p.copy()
    for action in state['actions']:action(1.)
    bpy.context.view_layer.update();points=corners(state['hero']);distance=(p-t).length
    # Use actual geometry/FOV. Safe band takes priority over incompatible example fills.
    for attempt in range(200):
        aim(camera,p,t,state.get('camera_up'));bounds=projection(scene,camera,points)
        if bounds['y_min']>=.356 and bounds['y_max']<=.714:break
        if args.id in ['entrance_door_low','room_reveal_cup','room_seated_pan']:
            raise ValueError('Prescribed walk/reveal/pan needs a composition correction, not camera relocation: '+str(bounds))
        delta=p-t
        if args.id.split('__')[0]=='plate_tissue_slide':
            p+=Vector((0,-.015,0));t+=Vector((0,-.015,0))
        elif args.id.startswith('entrance_'):
            p.x=t.x+(p.x-t.x)*1.035;p.y=t.y+(p.y-t.y)*1.035
        elif args.id=='pour_upside_down':
            p.x=t.x+(p.x-t.x)*1.035;p.y=t.y+(p.y-t.y)*1.035
        else:p=t+delta*1.035
    else:raise ValueError('Could not fit target hero to P0 safe band')
    if (p-original).length>.01:
        state['adaptations'].append('Target camera framing adjusted from '+str(list(original))+' to '+str(list(p))+f' to keep the hero in the safe band with a fixed {lens} mm lens.')
    if record['camera']=='front' and state['silhouettes'] and (p-t).length>.9:raise ValueError('Selfie camera is beyond ordinary arm reach')
    review=dict(status='reviewed_before_render',subject=record['title'],angle=record['technique'],motion=record['technique'],
        focal_point='Target hero in the protected middle band',composition=record['composition'],
        golden_ratio='Use the prescribed center, thirds or functional three-point arrangement; no decorative spiral',
        lighting='Fixed light; restrained explicit window/fixture cues only',contacts=state['contacts'],
        handover='None: P0 ends on this shot target',source_setup=record['sourceSetup'],adaptations=state['adaptations'])
    (out/'pre-render-review.json').write_text(json.dumps(review,indent=2)+'\n')
    aim(camera,p,t,state.get('camera_up'))
    markers=[]
    if record['composition']=='triangle':
        for point in state.get('triangle_points',[]):
            v=world_to_camera_view(scene,camera,point)
            markers.append([float(v.x*405),float((1-v.y)*720)])
    total=record['durationSec']*15+15+record['setupBeatSeconds']*15
    lead=8;setup=record['setupBeatSeconds']*15;move=record['durationSec']*15;last=lead+setup+move
    timeline=[]
    for f in range(1,total+1):
        if f<=lead:u=1.;phase='target'
        elif f<=lead+setup:u=0.;phase='setup'
        elif f<=last:u=(f-lead-setup-1)/(move-1);phase='demonstration'
        else:u=1.;phase='final'
        timeline.append((f,u,phase))
    if args.probe:
        u={'target':1.,'start':0.,'middle':.5}[args.probe];timeline=[(1,u,args.probe)];last=1
    scene.frame_start=1;scene.frame_end=len(timeline)
    samples=[];hands=[o for o in scene.objects if o.get('p0_hand')]
    assert len(hands)<=2 and state['silhouettes']<=1
    for f,u,phase in timeline:
        scene.frame_set(f)
        for action in state['actions']:action(u)
        key_objects(scene,f)
        pos,target=state['sample'](u,p,t);aim(camera,Vector(pos),Vector(target),state.get('camera_up'))
        camera.keyframe_insert('location',frame=f);camera.keyframe_insert('rotation_quaternion',frame=f)
        samples.append(dict(frame=f,phase=phase,u=u,camera_position=list(pos),camera_rotation_quaternion=list(camera.rotation_quaternion),
            target_bounds=projection(scene,camera,corners(state['hero'])),lens_mm=lens))
    # Linear interpolation through dense samples; smoothness comes from the motion functions.
    for obj in scene.objects:
        if not obj.animation_data or not obj.animation_data.action:continue
        for layer in obj.animation_data.action.layers:
            for strip in layer.strips:
                channels=strip.channelbag(obj.animation_data.action_slot)
                if channels:
                    for curve in channels.fcurves:
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
    role_collections={}
    for obj in list(scene.objects):
        if obj.type!='MESH':continue
        if obj.get('p0_framing_mask'):continue
        name=obj.get('composition_role','support')
        # Optional per-object line colour (RGB): such objects get their own stroke object of the same role.
        color=obj.get('p0_line_color')
        if color is not None:name+=' / colour '+','.join(f'{c:.3f}' for c in color)
        if name not in role_collections:
            collection=bpy.data.collections.new('P0 source / '+name);scene.collection.children.link(collection);role_collections[name]=collection
            collection['p0_role']=obj.get('composition_role','support')
            if color is not None:collection['p0_line_color']=list(color)
        for previous in list(obj.users_collection):previous.objects.unlink(obj)
        role_collections[name].objects.link(obj);obj.data.materials.clear()
    scene.frame_set(1);bpy.context.view_layer.update()
    gp=[];stroke_counts={}
    render_args=argparse.Namespace(hidden=False,contour_only=True)
    fov=2*math.atan(36/(2*lens))
    for key,collection in role_collections.items():
        role_name=collection['p0_role']
        render_args.skip_intersections=role_name=='character'
        before=set(bpy.data.objects)
        clear_shells=[(o,o.lineart.usage) for o in scene.objects if o.type=='MESH' and o.get('clear_vessel_shell')] if role_name in ['drink_contents','hand','lighting_cue'] else []
        for shell,_ in clear_shells:shell.lineart.usage='EXCLUDE'
        try:obj,counts=L.strokes_setup(scene,collection,render_args,max(.15,(p-t).length),fov,last)
        except RuntimeError as error:
            if role_name=='hero' or 'no visible contours' not in str(error):raise
            # An offscreen/fully occluded supporting collection is valid.
            for empty in set(bpy.data.objects)-before:bpy.data.objects.remove(empty,do_unlink=True)
            stroke_counts[key]={'offscreen_or_occluded':True}
            continue
        finally:
            for shell,usage in clear_shells:shell.lineart.usage=usage
        obj.name='P0 strokes / '+key;alpha=P.ROLE_ALPHA[role_name]
        for layer in obj.data.layers:
            layer.opacity=alpha
            if role_name=='character':
                # Keep the instruction a head-and-shoulders ghost. Lower-body
                # clothing and resting hands are not useful framing targets.
                for drawing_frame in layer.frames:
                    drawing=drawing_frame.drawing;position=drawing.attributes.get('position')
                    if position is None:continue
                    points=np.empty((len(position.data),3),dtype=np.float32);position.data.foreach_get('vector',points.ravel())
                    # A forearm resting on the raised table stays drawn down to the tabletop.
                    floor=.88 if any(o.get('p0_supported_right_hand') for o in scene.objects) else 1.00
                    # A seated creator's guide sets its own floor (the tabletop), so hands, fork and cup stay drawn.
                    floor=state.get('character_fade_floor',floor)
                    fade=np.clip((points[:,2]-floor)/.22,0,1);fade=fade*fade*(3-2*fade)
                    opacity=drawing.attributes.get('opacity') or drawing.attributes.new('opacity','FLOAT','POINT')
                    opacity.data.foreach_set('value',fade.astype(np.float32))
            if role_name=='hand':
                for drawing_frame in layer.frames:
                    scene.frame_set(drawing_frame.frame_number);bpy.context.view_layer.update()
                    drawing=drawing_frame.drawing;position=drawing.attributes.get('position')
                    if position is None:continue
                    points=np.empty((len(position.data),3),dtype=np.float32);position.data.foreach_get('vector',points.ravel())
                    grips=[];radii=[]
                    for hand in hands:
                        mesh=next(o for o in hand.children_recursive if o.type=='MESH')
                        marks=json.loads(mesh['landmarks']);anchor=hand.get('contact_landmark','grip')
                        local=Vector(marks[anchor]) if anchor in marks else (Vector(marks['f_index.03'])+Vector(marks['thumb.03']))/2
                        grips.append(np.array(hand.matrix_world@local))
                        # A scene may set its own fade radii (metres from the grip) when a wider camera shows the cut forearm end.
                        radii.append(tuple(hand['p0_grip_fade']) if 'p0_grip_fade' in hand else (.08,.16) if hand.get('p0_cropped_grip') else (.18,.48))
                    fades=[]
                    for g,(inner,outer) in zip(grips,radii):
                        u=np.clip((np.linalg.norm(points-g,axis=1)-inner)/(outer-inner),0,1);fades.append(1-u*u*(3-2*u))
                    fade=np.max(np.stack(fades),axis=0)
                    opacity=drawing.attributes.get('opacity')
                    values=np.ones(len(points),dtype=np.float32)
                    if opacity:opacity.data.foreach_get('value',values)
                    else:opacity=drawing.attributes.new('opacity','FLOAT','POINT')
                    opacity.data.foreach_set('value',(values*fade).astype(np.float32))
            # Preserve identical initial target drawings; no idle extraction jitter.
            if not args.probe:
                for number in [f.frame_number for f in layer.frames if 1<f.frame_number<=lead]:layer.frames.remove(number)
        if role_name=='character' and state.get('character_stroke_opacity'):
            # A guide may fade its character further by world position (factor per point), on top of the height fade.
            to_world=np.array(obj.matrix_world);peak={}
            for layer in obj.data.layers:
                for drawing_frame in layer.frames:
                    drawing=drawing_frame.drawing;position=drawing.attributes.get('position')
                    if position is None:continue
                    points=np.empty((len(position.data),3),dtype=np.float32);position.data.foreach_get('vector',points.ravel())
                    values=np.ones(len(points),dtype=np.float32);opacity=drawing.attributes.get('opacity')
                    if opacity:opacity.data.foreach_get('value',values)
                    else:opacity=drawing.attributes.new('opacity','FLOAT','POINT')
                    values=(values*state['character_stroke_opacity'](points@to_world[:3,:3].T+to_world[:3,3])).astype(np.float32)
                    opacity.data.foreach_set('value',values)
                    number=drawing_frame.frame_number;peak[number]=max(peak.get(number,0.),float(values.max()) if len(values) else 0.)
            for check in state.get('performance_checks',[]):
                if 'frame' not in check:continue
                shown=max((k for k in peak if k<=check['frame']),default=None)
                check['character_peak_opacity']=None if shown is None else round(peak[shown],4)
        if role_name=='lighting_cue':obj.data.materials[1].grease_pencil.color=(1.,.73,.17,1.)
        if 'p0_line_color' in collection:obj.data.materials[1].grease_pencil.color=(*collection['p0_line_color'],1.)
        gp.append(obj);stroke_counts[key]=counts
    for obj in scene.objects:
        if obj.type=='MESH':obj.hide_render=True
    bpy.context.preferences.filepaths.save_version=0;scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    frames=out/'frames';frames.mkdir(exist_ok=True)
    rendered={}
    source_meshes=sorted((o for o in scene.objects if o.type=='MESH'),key=lambda o:o.name)
    for f,u,phase in timeline:
        output=frames/f'frame_{f:04d}.png'
        if not args.probe and (1<f<=lead or f>last):
            shutil.copyfile(frames/('frame_0001.png' if f<=lead else f'frame_{last:04d}.png'),output)
        else:
            scene.frame_set(f);bpy.context.view_layer.update()
            signature=tuple(round(v,7) for row in camera.matrix_world for v in row)
            for obj in source_meshes:
                signature+=tuple(round(v,7) for row in obj.matrix_world for v in row)
                if obj.data.shape_keys:signature+=tuple(round(k.value,7) for k in obj.data.shape_keys.key_blocks)
            for arm in (o for o in scene.objects if o.type=='ARMATURE'):
                signature+=tuple(round(v,7) for b in arm.pose.bones for row in b.matrix for v in row)
            if signature in rendered:shutil.copyfile(rendered[signature],output)
            else:
                scene.render.filepath=str(output);bpy.ops.render.render(write_still=True);rendered[signature]=output
    # Independently prove source surfaces do not leak into the image.
    for obj in gp:obj.hide_render=True
    scene.render.filepath=str(out/'surface-isolation.png');bpy.ops.render.render(write_still=True)
    im=bpy.data.images.load(scene.render.filepath,check_existing=False)
    pixels=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pixels)
    assert float(pixels.reshape(-1,4)[:,3].max())==0
    bpy.data.images.remove(im);(out/'surface-isolation.png').unlink()
    for obj in gp:obj.hide_render=False
    scene.frame_set(1)
    # Hero-only target mask is a separate check artifact, never shipped as a guide.
    if not args.probe:
        for obj in gp:obj.hide_render=not (obj.name=='P0 strokes / hero' or obj.name.startswith('P0 strokes / hero / colour '))
        masks=state.get('framing_masks',[])
        if masks:
            for obj in gp:obj.hide_render=True
            white=bpy.data.materials.new('Validation only / actual face surface')
            white.use_nodes=True;nodes=white.node_tree.nodes;nodes.clear()
            shader=nodes.new('ShaderNodeEmission');shader.inputs[0].default_value=(1,1,1,1)
            output=nodes.new('ShaderNodeOutputMaterial');white.node_tree.links.new(shader.outputs[0],output.inputs[0])
            for obj in masks:obj.data.materials.clear();obj.data.materials.append(white);obj.hide_render=False
        scene.render.filepath=str(out/'hero-target.png');bpy.ops.render.render(write_still=True)
        for obj in masks:obj.hide_render=True
        for obj in gp:obj.hide_render=False
    meta=dict(id=args.id,status='rendered',record=record,frame_count=len(timeline),fps=15,resolution=[405,720],
        expected_seconds=record['durationSec']+record['setupBeatSeconds']+1,clock=timeline and data['clock'],
        target_hold_frames=lead,setup_frames=setup,move_frames=move,final_hold_frames=7,
        source_brief_sha256=data['sourceSHA256'],builder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        scene_builder_sha256=hashlib.sha256((HERE/('p0_people.py' if state.get('detailed_people') else 'p0_scenes.py')).read_bytes()).hexdigest(),
        camera_samples=samples,camera_lens_fixed=True,lighting_fixed=True,
        target_bounds=bounds,pre_render_review=review,maximum_hands=state.get('hand_count',0) if state.get('detailed_people') else len(hands),detailed_people=state.get('detailed_people',0),
        silhouettes=state['silhouettes'],source_surfaces_absent=True,role_opacity=P.ROLE_ALPHA,
        alphaFactor=1,probe=args.probe,strokes=stroke_counts,blender_version=bpy.app.version_string,picture_in_picture=state.get('pip',False))
    meta.update(light_cues=state.get('light_cues',[]),steam_edge_glow=args.id.startswith('steam_'),triangle_markers=markers,
        light_source_positions=[list(o.location) for o in scene.objects if o.type=='LIGHT'],forearm_ends_faded=bool(hands))
    if state.get('detailed_people'):
        meta.update(preview_mirrored=state['preview_mirrored'],performance_checks=state['performance_checks'],
            hero_region='Actual face triangles; hair and shoulders are supporting context',
            facial_animation=False,character='creator',lens_mm=lens)
    (out/'meta.json').write_text(json.dumps(meta,indent=2)+'\n')
    (out/'pre-render-review.json').write_text(json.dumps(review,indent=2)+'\n')
    print('P0_RENDER_READY',args.id,len(timeline),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--probe',choices=['target','start','middle']);p.add_argument('--replace',action='store_true')
    p.add_argument('--record',type=Path,help='a draft guide record (JSON), instead of the registry');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    try:run(a)
    except BaseException as e:print('P0_RENDER_ERROR',a.id,str(e),file=sys.stderr,flush=True);raise
