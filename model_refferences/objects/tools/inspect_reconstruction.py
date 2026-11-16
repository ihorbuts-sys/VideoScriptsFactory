"""Import a real reconstructed PLY into Blender and render six exact views."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P

def run(folder,width=.17,clean_clay=False):
    out=Path(folder).resolve();P.clear();scene=bpy.context.scene;P.studio(scene)
    scene.name='Local image-driven reconstruction review'
    bpy.ops.wm.ply_import(filepath=str(out/'reconstruction.ply'))
    mesh=bpy.context.object;mesh.name='TripoSR reconstructed croissant / original vertex colors'
    # TripoSR canonical input camera is +X with +Z up. Our front camera is -Y.
    rotation=Matrix.Rotation(-math.pi/2,3,'Z')
    for v in mesh.data.vertices:v.co=rotation@v.co
    lo,hi=P.bounds([mesh]);factor=width/(hi.x-lo.x)
    for v in mesh.data.vertices:v.co=(v.co-Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z)))*factor
    for polygon in mesh.data.polygons:polygon.use_smooth=True
    attrs=list(mesh.data.color_attributes)
    mat=bpy.data.materials.new('Reconstructed image colors / matte clay');mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.64
    bsdf.inputs['Specular IOR Level'].default_value=.20
    if attrs and not clean_clay:
        color=mat.node_tree.nodes.new('ShaderNodeVertexColor');color.layer_name=attrs[0].name
        mat.node_tree.links.new(color.outputs['Color'],bsdf.inputs['Base Color'])
    else:bsdf.inputs['Base Color'].default_value=(.82,.43,.065,1)
    if clean_clay:
        smooth=mesh.modifiers.new('Remove reconstruction surface noise','SMOOTH');smooth.factor=.3;smooth.iterations=6
    mesh.data.materials.clear();mesh.data.materials.append(mat)
    mesh['reconstruction_method']='TripoSR neural image-to-3D; not parametric approximation'
    mesh['input_image']='../croissant/design/front.png'
    mesh['review_status']='unreviewed';mesh['units']='metres'
    mesh.asset_mark();mesh.asset_data.description='Image-driven croissant reconstruction trial, pending comparison'
    lo,hi=P.bounds([mesh]);center=(lo+hi)/2;extent=max(hi-lo);P.lighting(center,extent)
    cd=bpy.data.cameras.new('Orthographic review camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam
    cd.type='ORTHO';cd.ortho_scale=extent*1.28
    cam.location=center+Vector((1,-1.7,1.1)).normalized()*extent*4;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/('clay-cleaned.blend' if clean_clay else 'reconstructed.blend')),compress=True)
    views={'front':(0,-1,0),'back':(0,1,0),'left':(-1,0,0),'right':(1,0,0),'top':(0,0,1),'bottom':(0,0,-1),'preview':(1,-1.7,1.1)}
    rendered=out/('cleaned' if clean_clay else 'rendered');rendered.mkdir(exist_ok=True)
    for name,direction in views.items():
        cam.location=center+Vector(direction).normalized()*extent*4;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(rendered/(name+'.png'));bpy.ops.render.render(write_still=True)
    (out/('cleaned-review.json' if clean_clay else 'blender-review.json')).write_text(json.dumps(dict(status='rendered_pending_visual_review',
        model='clay-cleaned.blend' if clean_clay else 'reconstructed.blend',dimensions_m=list(hi-lo),mesh_vertices=len(mesh.data.vertices),
        color_attributes=[a.name for a in attrs],views=list(views),same_geometry_all_views=True,
        model_driven_by_input_image=True,reference_fidelity_verified=False),indent=2)+'\n')
    print('RECONSTRUCTION_IMPORTED_AND_RENDERED',str(out),flush=True)

if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1],clean_clay='--clean-clay' in sys.argv)
