"""Build a small, source-preserving contour-only copy of the canonical creator rig."""
import json,sys,hashlib
from pathlib import Path
import bpy,bmesh,numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'model_refferences/objects/tools'))
from build_coffee_counter_v2 import add_cast


def prepare():
    source=ROOT/'model_refferences/creator/tripo-rigged/review/asset.blend'
    out=ROOT/'model_refferences/creator/lineart'
    out.mkdir(exist_ok=True)
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    root,arm=add_cast('creator',(0,0,0),0)
    bpy.context.view_layer.update()
    rows=[];skin=[]
    feature_count=0;features=[]
    for obj in list(root.children_recursive):
        obj.animation_data_clear()
        if obj.type!='MESH':continue
        obj.data=obj.data.copy()
        # The cast's eyes/brows are predominantly texture based. Transfer only
        # these existing dark facial marks to thin source-surface patches so
        # contour extraction can retain the reference identity without textures.
        mats=obj.data.materials
        if mats and mats[0].use_nodes and obj.data.uv_layers.active:
            shader=mats[0].node_tree.nodes.get('Principled BSDF')
            links=shader.inputs['Base Color'].links if shader else []
            image=links[0].from_node.image if links and hasattr(links[0].from_node,'image') else None
            if image:
                count=len(obj.data.polygons)
                centers=np.empty(count*3,dtype=np.float32);obj.data.polygons.foreach_get('center',centers)
                m=np.array(obj.matrix_world);world=centers.reshape(-1,3)@m[:3,:3].T+m[:3,3]
                eye_region=((np.abs(world[:,0])-.062)/.047)**2+((world[:,2]-1.493)/.048)**2<1
                region=eye_region&(world[:,2]<1.543)&(world[:,1]<-.065)
                if region.any():
                    starts=np.empty(count,dtype=np.int32);sizes=starts.copy()
                    obj.data.polygons.foreach_get('loop_start',starts);obj.data.polygons.foreach_get('loop_total',sizes)
                    uv=np.empty(len(obj.data.loops)*2,dtype=np.float32)
                    obj.data.uv_layers.active.data.foreach_get('uv',uv)
                    mean=np.add.reduceat(uv.reshape(-1,2),starts,axis=0)/sizes[:,None]
                    pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels)
                    pixels=pixels.reshape(image.size[1],image.size[0],4)
                    rgb=pixels[np.clip((mean[:,1]*image.size[1]).astype(int),0,image.size[1]-1),np.clip((mean[:,0]*image.size[0]).astype(int),0,image.size[0]-1),:3]
                    selected=region&(rgb.max(axis=1)<.34)
                    if selected.sum()>5:
                        patch=obj.copy();patch.data=obj.data.copy();bpy.context.scene.collection.objects.link(patch)
                        patch.parent=root;patch.matrix_world=obj.matrix_world.copy();features.append(patch)
                        bm=bmesh.new();bm.from_mesh(patch.data);bm.faces.ensure_lookup_table()
                        bmesh.ops.delete(bm,geom=[f for f in bm.faces if not selected[f.index]],context='FACES')
                        bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
                        offset=obj.matrix_world.to_3x3().inverted()@__import__('mathutils').Vector((0,-.002,0))
                        for v in bm.verts:v.co+=offset
                        bm.to_mesh(patch.data);bm.free();patch.data.materials.clear()
                        patch.name='Reference eye and brow contours / '+obj.name
                        patch['p0_face_feature']=True;feature_count+=1
                        if not any(m.type=='ARMATURE' for m in patch.modifiers):
                            binding=patch.modifiers.new('Original skeleton / facial patch','ARMATURE');binding.object=arm
        obj.data.materials.clear()
        before=len(obj.data.polygons)
        skin.append(obj);rows.append(dict(name=obj.name,source_faces=before))
    # Tripo partitions one continuous skin into arbitrary submeshes. Weld those
    # boundaries BEFORE simplifying, otherwise they become false diagonal lines.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in skin:obj.select_set(True)
    bpy.context.view_layer.objects.active=skin[0];bpy.ops.object.join()
    obj=bpy.context.object;obj.name='Canonical creator continuous contour skin'
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00002)
    bm.to_mesh(obj.data);bm.free()
    mod=obj.modifiers.new('Contour study simplification','DECIMATE');mod.ratio=min(1,90000/len(obj.data.polygons))
    bpy.ops.object.modifier_move_up(modifier=mod.name);bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=obj.modifiers.new('Quiet clay surface','SMOOTH');mod.factor=.25;mod.iterations=2
    bpy.ops.object.modifier_move_up(modifier=mod.name);bpy.ops.object.modifier_apply(modifier=mod.name)
    for face in obj.data.polygons:face.use_smooth=True
    if not any(m.type=='ARMATURE' for m in obj.modifiers):
        binding=obj.modifiers.new('Original skeleton / preserved vertex weights','ARMATURE');binding.object=arm
    rows.append(dict(name=obj.name,contour_faces=len(obj.data.polygons)))
    for bone in arm.pose.bones:bone.matrix_basis.identity()
    col=bpy.data.collections.new('P0 canonical creator');bpy.context.scene.collection.children.link(col)
    for obj in dict.fromkeys([root,*root.children_recursive,*features]):
        for old in list(obj.users_collection):old.objects.unlink(obj)
        col.objects.link(obj)
    root['p0_character']='creator';root['source_sha256']=digest
    bpy.data.libraries.write(str(out/'asset.blend'),{col},fake_user=True,compress=True)
    (out/'metadata.json').write_text(json.dumps(dict(source=str(source.relative_to(ROOT)),source_sha256=digest,
        source_unchanged=hashlib.sha256(source.read_bytes()).hexdigest()==digest,meshes=rows,
        facial_controls=False,texture_derived_face_patches=feature_count,original_skeleton_and_vertex_weights=True),indent=2)+'\n')
    print('P0_CREATOR_PREPARED',len(obj.data.polygons) if obj.type=='MESH' else 'ready',flush=True)


if __name__=='__main__':prepare()
