"""Make the required hollow-cylinder + torus test fixture and import-format fixtures."""
import argparse,sys
from pathlib import Path
import bpy,bmesh,math

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);a.out=a.out.expanduser().resolve();a.out.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=.04,depth=.1,location=(0,0,.05))
    body=bpy.context.object;body.name='Cup / hollow cylinder'
    mesh=bmesh.new();mesh.from_mesh(body.data)
    bmesh.ops.delete(mesh,geom=[f for f in mesh.faces if f.normal.z>.9],context='FACES')
    mesh.to_mesh(body.data);mesh.free()
    solid=body.modifiers.new('Cup wall','SOLIDIFY');solid.thickness=.003;solid.offset=-1
    bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=solid.name)
    bpy.ops.mesh.primitive_torus_add(major_segments=96,minor_segments=24,major_radius=.024,minor_radius=.006,
        location=(.055,0,.055),rotation=(math.pi/2,0,0))
    bpy.context.object.name='Cup / torus handle'
    bpy.ops.wm.save_as_mainfile(filepath=str(a.out),compress=True)
    bpy.ops.export_scene.gltf(filepath=str(a.out.with_suffix('.glb')),export_format='GLB')
    bpy.ops.wm.obj_export(filepath=str(a.out.with_suffix('.obj')))
    bpy.ops.export_scene.fbx(filepath=str(a.out.with_suffix('.fbx')),object_types={'MESH'},add_leaf_bones=False)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(a.out.with_name('empty.blend')),compress=True)
