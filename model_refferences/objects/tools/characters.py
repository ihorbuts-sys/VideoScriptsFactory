"""Editable clay cast draft, based on the approved six-view character references.

Anatomical right is -X for a person facing -Y. The original character images
remain untouched. The new models must pass identity and pose review before use.
"""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P
import real_hands
ROOT=P.ROOT.parent
CAST={
 'creator':dict(skin='D99A64',shirt='yellow',pants='sage',hair='493026'),
 'barista':dict(skin='F0BE97',shirt='white',pants='charcoal',hair='423027'),
 'friend_locs':dict(skin='945635',shirt='white',pants='sage',hair='382B25'),
}

def sweep(name,centers,radii,color):
    """A variable elliptical sweep with closed ends, suitable for moulded forms."""
    verts=[];faces=[];n=24
    for i,(c,r) in enumerate(zip(centers,radii)):
        c=Vector(c);t=Vector(centers[min(i+1,len(centers)-1)])-Vector(centers[max(i-1,0)])
        t.normalize();side=t.cross(Vector((0,1,0)))
        if side.length<.01:side=t.cross(Vector((1,0,0)))
        side.normalize();up=t.cross(side).normalized()
        for j in range(n):
            a=j*math.tau/n;v=c+side*math.cos(a)*r[0]+up*math.sin(a)*r[1];verts.append(v)
    for i in range(len(centers)-1):
        for j in range(n):faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    faces.extend([tuple(range(n-1,-1,-1)),tuple((len(centers)-1)*n+j for j in range(n))])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);P.finish(o,name,color)
    sub=o.modifiers.new('Soft clay surface','SUBSURF');sub.levels=2;sub.render_levels=2
    return o

def loft(name,rows,color):
    # Horizontal elliptical rings: z, x-radius, y-radius, y-offset.
    verts=[];faces=[];n=32
    for z,rx,ry,y in rows:
        for j in range(n):
            a=j*math.tau/n;verts.append((rx*math.cos(a),y+ry*math.sin(a),z))
    for i in range(len(rows)-1):
        for j in range(n):faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    faces.extend([tuple(range(n-1,-1,-1)),tuple((len(rows)-1)*n+j for j in range(n))])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);P.finish(o,name,color)
    sub=o.modifiers.new('Soft fitted clay clothing','SUBSURF');sub.levels=2;sub.render_levels=2
    return o

def assign(o,rig,bone,weights=None):
    if o.type!='MESH':return
    if weights:
        groups={key:o.vertex_groups.new(name=key) for key in weights}
        for v in o.data.vertices:
            vals={key:fn(v.co) for key,fn in weights.items()};total=sum(vals.values()) or 1
            for key,value in vals.items():
                if value>0:groups[key].add([v.index],value/total,'REPLACE')
    else:o.vertex_groups.new(name=bone).add(list(range(len(o.data.vertices))),1,'REPLACE')
    mod=o.modifiers.new('Loca character rig','ARMATURE');mod.object=rig
    o.parent=rig

def create(id):
    spec=CAST[id];P.PALETTE['skin_'+id]=spec['skin'];P.PALETTE['hair_'+id]=spec['hair']
    skin='skin_'+id;hair='hair_'+id
    before=set(bpy.data.objects)
    data=bpy.data.armatures.new('Loca '+id+' skeleton');rig=bpy.data.objects.new('Rig / '+id,data)
    bpy.context.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bones={
        'root':((0,0,.02),(0,0,.20),None),'pelvis':((0,0,.85),(0,0,.98),'root'),
        'spine':((0,0,.98),(0,0,1.30),'pelvis'),'neck':((0,0,1.30),(0,0,1.40),'spine'),
        'head':((0,0,1.40),(0,0,1.72),'neck')}
    for side,s in [('R',-1),('L',1)]:
        bones.update({
            'upper_arm.'+side:((s*.185,0,1.28),(s*.285,0,1.04),'spine'),
            'forearm.'+side:((s*.285,0,1.04),(s*.365,-.005,.82),'upper_arm.'+side),
            'hand.'+side:((s*.365,-.005,.82),(s*.405,-.008,.70),'forearm.'+side),
            'thigh.'+side:((s*.09,0,.90),(s*.10,-.015,.50),'pelvis'),
            'shin.'+side:((s*.10,-.015,.50),(s*.11,0,.13),'thigh.'+side),
            'foot.'+side:((s*.11,0,.13),(s*.11,-.11,.07),'shin.'+side)})
    for name,(head,tail,parent) in bones.items():
        b=data.edit_bones.new(name);b.head=head;b.tail=tail
        if parent:b.parent=data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT');rig.show_in_front=True
    torso=loft('Clothing / soft tee',[(.92,.14,.085,0),(.94,.16,.096,0),(1.05,.155,.095,0),
        (1.20,.17,.095,0),(1.28,.195,.092,0),(1.32,.16,.08,0),(1.35,.058,.058,0)],spec['shirt'])
    assign(torso,rig,'spine')
    neck=P.lathe('Skin / neck',[(0,1.30),(.053,1.30),(.050,1.43),(0,1.43)],c=skin);assign(neck,rig,'neck')
    for side,s in [('R',-1),('L',1)]:
        centers=[(s*.185,0,1.28),(s*.22,0,1.20),(s*.285,0,1.04),(s*.325,-.002,.94),(s*.365,-.005,.82)]
        arm=sweep('Skin / continuous arm '+side,centers,[(.057,.055),(.054,.052),(.042,.041),(.038,.036),(.028,.027)],skin)
        blend=lambda v:max(0,min(1,(1.10-v.z)/.14))
        assign(arm,rig,None,{'upper_arm.'+side:lambda v:1-blend(v),'forearm.'+side:blend})
        sleeve=sweep('Clothing / short sleeve '+side,centers[:2]+[(s*.245,0,1.14)],[(.070,.066),(.070,.067),(.068,.063)],spec['shirt'])
        assign(sleeve,rig,'upper_arm.'+side)
        P.G.MAT=P.material(skin)
        hand=real_hands.place(pose='relaxed',side=side,target=centers[-1],forward=(s*.08,0,-.22),normal=(0,-1,0),anchor='wrist_origin')
        hand.scale=(.72,)*3;bpy.context.view_layer.update()
        for o in hand.children_recursive:
            if o.type!='MESH':continue
            matrix=o.matrix_world.copy();o.parent=None;o.matrix_world=Matrix.Identity(4)
            for v in o.data.vertices:v.co=matrix@v.co
            P.finish(o,'Anatomical clay hand / '+side,skin);assign(o,rig,'hand.'+side)
        bpy.data.objects.remove(hand,do_unlink=True)
        leg=sweep('Clothing / trouser leg '+side,[(s*.085,0,.94),(s*.09,0,.82),(s*.10,-.014,.52),(s*.11,0,.25),(s*.11,0,.13)],
            [(.09,.095),(.088,.09),(.065,.066),(.058,.058),(.057,.056)],spec['pants'])
        blendleg=lambda v:max(0,min(1,(.57-v.z)/.15))
        assign(leg,rig,None,{'thigh.'+side:lambda v:1-blendleg(v),'shin.'+side:blendleg})
        shoe=P.ball('Shoe / rounded upper',(s*.11,-.047,.075),(.066,.117,.060),'white');assign(shoe,rig,'foot.'+side)
        sole=P.block('Shoe / cream sole',(s*.11,-.047,.025),(.14,.225,.035),'cream',.025);assign(sole,rig,'foot.'+side)
        for y in [-.08,-.04,0]:
            lace=P.tube('Shoe / broad clay lace',[(s*.11-.038,y,.122),(s*.11+.038,y,.122)],.004,'cream');assign(lace,rig,'foot.'+side)
    pelvis=P.ball('Clothing / trouser hips',(0,0,.91),(.166,.10,.105),spec['pants']);assign(pelvis,rig,'pelvis')
    head_before=set(bpy.data.objects)
    head=P.ball('Face / soft sculpted head',(0,0,1.535),(.134,.112,.165),skin)
    for v in head.data.vertices:
        if v.co.z<-.035:v.co.x*=1+.95*(v.co.z+.035)
    for s in [-1,1]:
        P.ball('Face / ear',(s*.137,.002,1.526),(.031,.020,.045),skin)
        P.ball('Face / inner ear',(s*.145,-.014,1.526),(.017,.006,.026),skin)
        # White and pupils are deliberately sculpted, no skin realism.
        P.ball('Face / eye white',(s*.054,-.101,1.560),(.032,.018,.036),'white')
        P.ball('Face / iris',(s*.054,-.117,1.558),(.020,.009,.024),'brown')
        P.ball('Face / pupil',(s*.054,-.124,1.558),(.013,.004,.019),'charcoal')
        P.ball('Face / catchlight',(s*.054-.005,-.128,1.570),(.004,.002,.005),'white')
        P.tube('Face / sculpted eyebrow',[(s*.027,-.109,1.615),(s*.052,-.117,1.621),(s*.080,-.104,1.613)],.008,hair)
    P.ball('Face / rounded nose',(0,-.114,1.514),(.022,.020,.023),skin)
    # No mouth drawing in ghost artwork; a quiet closed clay expression in color.
    mouth=P.tube('Color-only / subtle mouth',[(-.031,-.106,1.473),(0,-.118,1.467),(.031,-.106,1.473)],.0025,'brown');mouth['omit_from_ghost']=True
    P.ball('Hair / moulded scalp',(0,.011,1.632),(.142,.116,.105),hair)
    if id=='friend_locs':
        for i in range(14):
            a=math.tau*i/14;r=.122
            start=(r*math.cos(a),.008+r*.75*math.sin(a),1.649)
            end=(.214*math.cos(a),.013+.16*math.sin(a),1.665+.072*(i%3==0))
            mid=Vector(start).lerp(Vector(end),.52);mid.z+=.021
            sweep('Hair / chunky sculpted loc',[start,mid,end],[(.027,.026),(.026,.024),(.015,.016)],hair)
        for i in range(7):
            x=(i-3)*.033
            sweep('Hair / front clay loc',[(x,-.045,1.705),(x,-.095,1.681),(x*.95,-.112,1.644)],[(.022,.022),(.025,.023),(.014,.013)],hair)
    else:
        for i in range(9):
            x=(i-4)*.027
            sweep('Hair / sculpted swept lock',[(x+.035,.015,1.715),(x+.025,-.065,1.714),(x-.01,-.115,1.650-.010*(i%3))],
                [(.026,.026),(.029,.027),(.009,.010)],hair)
        for s in [-1,1]:
            for i in range(4):
                sweep('Hair / side clay lock',[(s*.115,.055,1.680-i*.022),(s*.138,.014,1.655-i*.022),(s*.128,-.040,1.625-i*.018)],
                    [(.022,.022),(.025,.022),(.009,.009)],hair)
        if id=='creator':
            for i in range(7):
                x=-.085+(i-3)*.020
                sweep('Hair / wavy plasticine ponytail',[(x,.07,1.714),(x-.035,.105,1.60),(x-.015,.15,1.47),(x-.05,.135,1.32),(x-.035,.10,1.25)],
                    [(.029,.030),(.038,.032),(.034,.031),(.030,.025),(.009,.010)],hair)
    for o in set(bpy.data.objects)-head_before:assign(o,rig,'head')
    if id=='barista':
        # Apron remains its own mesh for clothing swaps in non-cafe scenes.
        apron=loft('Clothing / sage apron',[(.48,.165,.100,-.01),(.49,.170,.105,-.01),(.83,.161,.102,-.01),(.99,.146,.105,-.01),
            (1.22,.125,.103,-.01),(1.24,.125,.103,-.01)],'sage');assign(apron,rig,'spine')
        for s in [-1,1]:
            strap=P.tube('Clothing / yellow apron strap',[(s*.115,-.115,1.21),(s*.12,-.091,1.34),(s*.12,.075,1.33),(s*.13,.10,1.05)],.015,'yellow');assign(strap,rig,'spine')
            button=P.ball('Clothing / apron button',(s*.115,-.125,1.21),(.012,.006,.012),'yellow');assign(button,rig,'spine')
        pocket=P.block('Clothing / apron pocket',(0,-.120,1.06),(.13,.012,.10),'teal',.015);assign(pocket,rig,'spine')
    if id=='creator':
        bag=P.block('Accessory / right-hip pink bag',(-.169,-.092,.91),(.19,.08,.20),'pink',.045);assign(bag,rig,'pelvis')
        flap=P.block('Accessory / bag flap',(-.169,-.14,.96),(.19,.025,.11),'pink',.04);assign(flap,rig,'pelvis')
        clasp=P.ball('Accessory / bag clasp',(-.169,-.16,.94),(.012,.005,.012),'yellow');assign(clasp,rig,'pelvis')
        strap=P.tube('Accessory / crossbody strap',[(.11,-.105,1.34),(.055,-.121,1.23),(-.05,-.12,1.08),(-.17,-.10,.98)],.012,'pink');assign(strap,rig,'spine')
    for o in set(bpy.data.objects)-before:
        if o!=rig and o.parent is None:o.parent=rig
    rig['character_id']=id;rig['source_reference']=str(ROOT/id/'front.png')
    rig['status']='draft_identity_and_pose_review_required';rig['front_direction']='-Y'
    rig['anatomical_right']='-X';rig['hand_source']='para / MakeHuman CC0; mesh recolored to clay'
    return rig

def export(id):
    P.clear();scene=bpy.context.scene;scene.name='Loca clay cast / '+id;P.studio(scene)
    rig=create(id);bpy.context.view_layer.update();lo,hi=P.bounds(rig.children_recursive);center=(lo+hi)/2;extent=max(hi-lo)
    P.lighting(center,extent)
    cd=bpy.data.cameras.new('Character reference camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam
    cd.type='ORTHO';cd.ortho_scale=extent*1.18
    cam.location=center+Vector((0,-4,0))*extent;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    out=ROOT/id/'blender';out.mkdir(exist_ok=True)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'character.blend'),compress=True)
    checks=[]
    for view,v in {'front':(0,-1,0),'back':(0,1,0),'left':(1,0,0),'right':(-1,0,0),'top':(0,0,1),'bottom':(0,0,-1),'preview':(1,-1.7,.4)}.items():
        cam.location=center+Vector(v).normalized()*extent*4;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(view+'.png'));bpy.ops.render.render(write_still=True)
        checks.append(view)
    (out/'metadata.json').write_text(json.dumps(dict(character=id,status='draft_identity_and_pose_review_required',views=checks,
        model='character.blend',height_m=hi.z-lo.z,bones=len(rig.data.bones),
        limitations=['Clothing and character proportions require visual approval against saved reference art before mass guide replacement.','Hand pose variants and object contact must be checked per action.'],
        license_note='Original authored character geometry; hand geometry para / MakeHuman CC0-1.0'),indent=2)+'\n')
    print('CHARACTER_EXPORTED',id,flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(CAST)
    if '--prototype' not in args:
        raise SystemExit('Archived character prototype: not an approved identity match. Use reference-driven reconstruction.')
    for id in args:
        if not id.startswith('--'):export(id)
