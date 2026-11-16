"""One massage stroke in a tight fixed-camera view over an abstract curved back surface."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector,Matrix
import assets as A
import geometry as G
import real_hands as H
from motion_paths import sequence

REVIEW=dict(subject='One anatomical practitioner hand performing a slow back-massage stroke',
    angle='Fixed close-up from above; the broad curved skin surface and forearm extend outside the picture',
    motion='Settle, apply gentle visible pressure, glide forward, then ease back into the same starting pose',
    focal_point='Palm contact and the direction of the stroke; camera remains completely still',
    composition='Fingers lead into open space; body edges are excluded, with one faint towel edge for context',
    golden_ratio='Lead room and readable contact take precedence over a forced geometric ratio',
    lighting='Fixed broad side light; a thin warm contact cue marks pressure without bloom or a moving light',
    contacts='Anatomical palm remains on the deforming curved patch; no floating fingertips or detached forearm end',
    handover='The next creator selfie stays deferred under the people policy',
    mobile='Prop the phone or ask a companion to hold this close-up steady; record only the small treatment area and practitioner hand')


def smooth(x):
    u=max(0,min(1,x));return u*u*(3-2*u)


def surface(x,y):return .865+.040*math.exp(-(x/.25)**2)-.009*(y/.50)**2


def path(u):return Vector((-.023+.035*u+.007*math.sin(math.pi*u),-.055+.13*u,0))


def build(scene,spec):
    duration=6.8;frames=round(duration*15)
    vertices=[];faces=[];nx=35;ny=49
    for j in range(ny):
        y=-.62+j*1.24/(ny-1)
        for i in range(nx):
            x=-.44+i*.88/(nx-1);vertices.append((x,y,surface(x,y)))
    for j in range(ny-1):
        for i in range(nx-1):
            a=j*nx+i;faces.append((a,a+1,a+nx+1,a+nx))
    data=bpy.data.meshes.new('Abstract curved massage area mesh');data.from_pydata(vertices,[],faces);data.update()
    patch=bpy.data.objects.new('Cropped curved massage surface',data);bpy.context.collection.objects.link(patch);G.finish(patch,patch.name)
    A.tag(patch,'background','Only a broad gently curved contact surface; no torso, face or body outline is modelled')
    for polygon in data.polygons:polygon.use_smooth=True
    patch.shape_key_add(name='Basis');keys=[]
    for k in range(9):
        p=path(k/8);key=patch.shape_key_add(name='Palm pressure '+str(k));keys.append(key)
        for vertex,base in zip(key.data,vertices):
            x,y,z=base;vertex.co.z=z-.0035*math.exp(-((x-p.x)/.052)**2-((y-p.y)/.063)**2)
    sub=patch.modifiers.new('Soft continuous contact surface','SUBSURF');sub.levels=1;sub.render_levels=1
    # Sparse blueprint contours reveal curvature without a recognisable torso outline.
    for x in [-.112,.112]:
        points=[]
        for j in range(21):
            y=-.40+j*.76/20;xx=x*(1+.12*math.sin(y*5));points.append((xx,y,surface(xx,y)+.0008))
        A.tag(G.tube('Cropped surface curvature',points,.0005),'structure','Faint open contour describes the curved contact surface; ends stay outside the frame')
    for y in [-.18,.20]:
        A.tag(G.tube('Skin surface cross contour',[(x,y,surface(x,y)+.0007) for x in [-.22,-.15,-.07,0,.07,.15,.22]],.00035),'background','Sparse transverse contour gives depth without a full body model')
    # A cropped towel edge identifies the setting without requiring a body model.
    towel=A.tag(G.block('Peripheral treatment towel',(-.205,-.22,.878),(.11,.40,.028),.016),'background','A small towel corner remains subordinate to the massage action')
    for x in [-.162,-.169]:
        A.tag(G.tube('Towel edge stitching',[(x,-.40,.893),(x,-.04,.893)],.0006),'background','Faint stationary stitching provides an orientation reference')
    library=Path(__file__).resolve().parent/'vendor/para-fps-arms/massage-hand.blend'
    hand=H.place('massage','R',target=(0,0,0),forward=(0,1,0),normal=(0,0,-1),anchor='hand',library=library)
    mesh=next(obj for obj in hand.children_recursive if obj.type=='MESH');A.tag(mesh,'hero','One continuous anatomical hand and forearm perform the stroke; no primitive fingers')
    landmarks=json.loads(mesh['landmarks']);palm=Vector((0,.052,0))
    rotation=hand.rotation_euler.to_matrix();hand.rotation_euler=rotation.to_euler()
    # Align the lowest palm surface with the skin, using the actual palm vertices.
    contact=[rotation@v.co for v in mesh.data.vertices if .015<v.co.y<.095 and abs(v.co.x)<.040]
    palm_low=min(v.z for v in contact)
    cue=A.empty('Massage pressure cue')
    for sign in [-1,1]:
        arc=G.tube('Subtle pressure edge',[(sign*.050,-.025,0),(sign*.057,0,0),(sign*.048,.029,0)],.00045)
        A.tag(arc,'lighting_cue','Thin contact annotation shows the area of pressure, not an animated light fixture');arc.parent=cue
    samples=[]
    for f in range(1,frames+1):
        t=(f-1)/15
        u=smooth((t-.75)/2.65) if t<=3.8 else 1-smooth((t-3.8)/2.55)
        pressure=smooth(t/.75)*(1-.50*smooth((t-3.4)/.6));pressure*=1-smooth((t-6.0)/.7)
        p=path(u);indent=.0035*pressure
        # The palm glides over the same surface; the wrist is not used as a rotation pivot.
        hand.location=(p.x,p.y-palm.y,surface(p.x,p.y)-indent-palm_low+.0004)
        hand.keyframe_insert(data_path='location',frame=f)
        for k,key in enumerate(keys):
            key.value=pressure*max(0,1-abs(u*8-k));key.keyframe_insert(data_path='value',frame=f)
        cue.location=(p.x,p.y,surface(p.x,p.y)+.0008);cue.scale=(.70+.30*pressure,)*3
        cue.keyframe_insert(data_path='location',frame=f);cue.keyframe_insert(data_path='scale',frame=f)
        samples.append(dict(frame=f,stroke_progress=u,pressure=pressure,palm_xy=[p.x,p.y],palm_z=hand.location.z+palm_low))
    A.fixed_side_light((0,.02,.90))
    origin=Vector((.015,-.105,1.29));focus=Vector((0,.025,.90));cam=G.camera('Locked massage detail phone',origin,focus-origin,50)
    result=sequence(cam,duration,actions=['Keep the phone still on a tight view of one hand massaging a small curved back area',
        'Show the palm settling into contact, gliding forward with visible pressure, and easing back smoothly'])
    result.update(static_hold=False,probe_frames=[1,15,40,55,75,95,102],
        mobile_feasibility=dict(visitor_space=True,fixed_phone=True,helper_or_propped_phone=True,max_phone_height_m=1.29),
        source_adaptations=['Owner requests an actual close-up back-massage action using a cropped curved surface instead of a full body model'],
        massage=dict(camera_locked=True,visible_hands=1,full_body_model=False,pressure_depth_m=.0035,stroke_distance_m=.13,samples=samples))
    return result
