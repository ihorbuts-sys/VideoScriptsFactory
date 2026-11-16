"""Reusable AI-painted sprites, attachment joints and a small multiplane camera.

Only source artwork is illustrated by image generation. Code extracts atlas cells,
projects fixed sprites, solves joints and supplies invisible occlusion mattes.
The broad scene wash is independent of the unfilled object drawings.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

GUIDES=Path(__file__).resolve().parents[1]
ROOT=GUIDES.parent
OUT=GUIDES/'sprite_motion'
W,H,FPS=405,720,15

ATLAS={
    'style-kit':['kettle','cup_eye','menu_eye','scene_wash'],
    'bar-parts':['bar_backwall','bar_counter','bar_stool','whiskey_glass'],
    'arm-joints':['arm_upper','arm_fore','hand_grip','hand_point'],
    'portrait-heads':['woman_eye','woman_high','man_eye','man_high'],
    'plated-food':['plate_low','pancake_eye','egg_high','lunch_top'],
    'work-hand-parts':['hand_support','hand_pinch','screwdriver','brush'],
    'room-shells':['room_cafe','room_calm','room_shop','room_lesson'],
    'motion-marks':['pour_stream','steam','foam','crumbs'],
    'bakery-props':['bread_loaf','pastry_halves','bread_tray','pastry_box'],
    'furniture-props':['cafe_table','salon_chair','treatment_table','piano'],
    'body-keyposes':['body_stand','body_half_squat','body_squat','body_walk_robe'],
}

ANCHORS={
    'kettle':dict(grip=[.14,.27],spout=[.98,.56]),
    'cup_eye':dict(rim=[.43,.06],base=[.46,.93]),
    'arm_upper':dict(shoulder=[.12,.17],elbow=[.87,.85]),
    'arm_fore':dict(elbow=[.12,.18],wrist=[.88,.86]),
    'hand_grip':dict(wrist=[.08,.58],grip=[.76,.28]),
    'hand_point':dict(wrist=[.08,.70],tip=[.98,.07]),
    'hand_support':dict(wrist=[.12,.88],grip=[.66,.37]),
    'hand_pinch':dict(wrist=[.13,.85],grip=[.7,.32]),
    'pour_stream':dict(start=[.5,.01],end=[.5,.98]),
    'bar_counter':dict(glass_contact=[.61,.265]),
    'whiskey_glass':dict(base=[.5,.955]),
}


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def extract():
    folder=OUT/'assets';folder.mkdir(exist_ok=True)
    records={}
    previous=OUT/'library.json'
    if previous.exists():records=json.loads(previous.read_text())['sprites']
    layouts=[dict(id=k,names=v,columns=2,rows=2) for k,v in ATLAS.items()]
    clean_jobs=OUT/'clean-jobs.json'
    if clean_jobs.exists():layouts+=json.loads(clean_jobs.read_text())['jobs']
    for layout in layouts:
        atlas=layout['id'];names=layout['names'];cols=layout['columns'];rows=layout['rows']
        source=OUT/'originals'/(atlas+'.png')
        if not source.exists():continue
        image=Image.open(source).convert('RGBA')
        boxes=[(round(c*image.width/cols),round(r*image.height/rows),round((c+1)*image.width/cols),round((r+1)*image.height/rows)) for r in range(rows) for c in range(cols)]
        if atlas=='bar-parts':
            cut=round(image.height*.475);mid=image.width//2
            boxes=[(0,0,mid,cut),(mid,0,image.width,cut),(0,cut,mid,image.height),(mid,cut,image.width,image.height)]
        for name,box in zip(names,boxes):
            if not name:continue
            cell=image.crop(box);a=np.asarray(cell.getchannel('A'))
            ys,xs=np.where(a>12)
            if not len(xs):raise RuntimeError('Empty sprite '+name)
            trim=(max(0,int(xs.min())-5),max(0,int(ys.min())-5),min(cell.width,int(xs.max())+6),min(cell.height,int(ys.max())+6))
            if name.startswith('body_'):trim=(0,0,cell.width,cell.height)
            cell=cell.crop(trim);path=folder/(name+'.png');cell.save(path)
            records[name]=dict(file=str(path.resolve()),sha256=digest(path),atlas=str(source.resolve()),atlas_sha256=digest(source),
                               cell=list(box),trim=list(trim),size=list(cell.size),anchors=ANCHORS.get(name,{}),
                               art='Generated open pencil contours; scene color wash is separate.')
    result=dict(version=1,style='open blue sketch with separate broad scene wash',sprites=records)
    previous.write_text(json.dumps(result,indent=2)+'\n');print(f'{len(records)} reusable sprite cells extracted.')


def ease(p):
    p=max(0,min(1,p));return .5-.5*math.cos(math.pi*p)


def value(track,t,default):
    if track is None:return default
    if not isinstance(track,list) or not track or not isinstance(track[0],dict):return track
    if t<=track[0]['t']:return track[0]['v']
    if t>=track[-1]['t']:return track[-1]['v']
    for a,b in zip(track,track[1:]):
        if a['t']<=t<=b['t']:
            p=(t-a['t'])/(b['t']-a['t']);p=p if b.get('ease')=='linear' else ease(p)
            av,bv=a['v'],b['v']
            if isinstance(av,list):return [x+(y-x)*p for x,y in zip(av,bv)]
            return av+(bv-av)*p
    return default


def T(x,y):return np.array([[1.,0,x],[0,1.,y],[0,0,1.]])
def S(x,y=None):return np.diag([x,x if y is None else y,1.])
def R(angle):
    a=math.radians(angle);c,s=math.cos(a),math.sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1.]])


def ik(shoulder,wrist,upper,lower,side=1):
    delta=np.array(wrist)-np.array(shoulder);distance=float(np.linalg.norm(delta));d=max(.01,min(distance,upper+lower-.01))
    direction=math.atan2(delta[1],delta[0]);offset=math.acos(max(-1,min(1,(upper*upper+d*d-lower*lower)/(2*upper*d))))*side
    elbow=np.array(shoulder)+upper*np.array([math.cos(direction+offset),math.sin(direction+offset)])
    return elbow.tolist()


class Scene:
    def __init__(self,spec,library=None):
        self.spec=spec
        self.library=library or json.loads((OUT/'library.json').read_text())['sprites']
        self.images={};self.mattes={}
        for node in spec['nodes']:
            name=node.get('sprite')
            if not name or name in self.images:continue
            record=self.library[name];assert digest(record['file'])==record['sha256'],name
            self.images[name]=Image.open(record['file']).convert('RGBA')
        self.nodes={n['id']:n for n in spec['nodes']}

    def anchor(self,node):
        anchor=node.get('anchor',[.5,.5])
        if isinstance(anchor,str):return self.library[node['sprite']]['anchors'][anchor]
        return anchor

    def joints(self,t):
        result={k:value(v,t,[0,0]) for k,v in self.spec.get('points',{}).items()}
        for rig in self.spec.get('ik',[]):
            result[rig['elbow']]=ik(result[rig['shoulder']],result[rig['wrist']],rig['upper'],rig['lower'],rig.get('side',1))
        return result

    def matrices(self,t):
        points=self.joints(t);frames={};paints={}
        camera=self.spec.get('camera',{});cx=value(camera.get('x'),t,0);cy=value(camera.get('y'),t,0);cz=value(camera.get('forward'),t,0)
        focal=camera.get('focal_px',405)
        def point(name):
            if name in points:return np.array(points[name])
            node_id,anchor=name.split(':',1);node=self.nodes[node_id];image=self.images[node['sprite']]
            uv=self.library[node['sprite']]['anchors'][anchor]
            return (paints[node_id]@np.array([uv[0]*image.width,uv[1]*image.height,1]))[:2]
        def node_frame(name):
            if name in frames:return frames[name]
            n=self.nodes[name];parent=n.get('parent');position=value(n.get('position'),t,[W/2,H/2])
            if n.get('point'):position=points[n['point']]
            if parent:
                parent_frame=node_frame(parent);p=self.nodes[parent]
                attach=n.get('attach')
                if attach:
                    uv=self.library[p['sprite']]['anchors'][attach] if isinstance(attach,str) else attach
                    anchor=self.anchor(p);im=self.images[p['sprite']];base=p.get('height',im.height)
                    position=[(uv[0]-anchor[0])*im.width*base/im.height,(uv[1]-anchor[1])*base]
                frame=parent_frame@T(*position)
            else:
                depth=float(n.get('depth',2));scale=depth/max(.1,depth-cz)
                px=W/2+(position[0]-W/2)*scale-focal*cx/max(.1,depth-cz)
                py=H/2+(position[1]-H/2)*scale-focal*cy/max(.1,depth-cz)
                frame=T(px,py)@S(scale)
            angle=value(n.get('rotation'),t,0)
            frame=frame@R(angle)@S(value(n.get('scale'),t,1))
            frames[name]=frame;return frame
        for n in self.spec['nodes']:
            if not n.get('sprite'):node_frame(n['id']);continue
            image=self.images[n['sprite']];height=n.get('height',image.height)
            if 'segment' in n:
                start,end=[point(x) for x in n['segment']]
                source_joints=n['source_joints'];anchors=self.library[n['sprite']]['anchors']
                a,b=[np.array(anchors[x])*np.array(image.size) for x in source_joints]
                sv=b-a;dv=end-start;scale=np.linalg.norm(dv)/np.linalg.norm(sv)
                angle=math.degrees(math.atan2(dv[1],dv[0])-math.atan2(sv[1],sv[0]))
                parent=node_frame(n['parent']) if n.get('parent') else np.eye(3)
                if n.get('thickness',1)!=1:
                    sa=math.degrees(math.atan2(sv[1],sv[0]));da=math.degrees(math.atan2(dv[1],dv[0]))
                    matrix=parent@T(*start)@R(da)@S(scale,scale*n['thickness'])@R(-sa)@T(*(-a))
                else:matrix=parent@T(*start)@R(angle)@S(scale)@T(*(-a))
                paints[n['id']]=matrix
                # Segments are leaves; explicit wrist nodes parent held props.
                frames[n['id']]=parent@T(*end)@R(angle)
            else:
                ax,ay=self.anchor(n)
                paints[n['id']]=node_frame(n['id'])@S(height/image.height)@T(-ax*image.width,-ay*image.height)
        return paints,frames

    def matte(self,n):
        name=n['sprite'];role=n.get('occlusion')
        if not role:return None
        cache=(name,str(role))
        if cache in self.mattes:return self.mattes[cache]
        image=self.images[name];w,h=image.size;mask=Image.new('L',image.size)
        draw=ImageDraw.Draw(mask)
        if role=='stool':
            # Invisible solid seat/leg masks; the spaces between legs stay open.
            draw.ellipse((.055*w,0,.86*w,.34*h),fill=255)
            for polygon in [((.15,.30),(.25,.33),(.08,.99),(0,.99)),((.43,.31),(.52,.33),(.48,1),(.38,1)),((.70,.28),(.78,.29),(.96,1),(.86,1))]:
                draw.polygon([(x*w,y*h) for x,y in polygon],fill=255)
        elif role=='counter':
            draw.polygon([(.005*w,.22*h),(.144*w,.009*h),(.997*w,.408*h),(.997*w,.462*h),(.978*w,.468*h),(.965*w,.987*h),(.025*w,.995*h),(.025*w,.30*h),(0,.28*h)],fill=255)
        else:
            alpha=np.asarray(image.getchannel('A'))
            binary=(alpha>18).astype(np.uint8)*255
            binary=cv2.morphologyEx(binary,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
            contours,_=cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            filled=np.zeros_like(binary);cv2.drawContours(filled,contours,-1,255,cv2.FILLED)
            mask=Image.fromarray(filled)
        mask=mask.filter(ImageFilter.GaussianBlur(.65));self.mattes[cache]=mask;return mask

    @staticmethod
    def warp(image,matrix):
        inv=np.linalg.inv(matrix)
        return image.transform((W,H),Image.Transform.AFFINE,tuple(inv[:2].reshape(-1)),Image.Resampling.BICUBIC)

    def render(self,t):
        matrices,_=self.matrices(t);wash=Image.new('RGBA',(W,H));ink=Image.new('RGBA',(W,H))
        nodes=sorted(self.spec['nodes'],key=lambda n:(n.get('order',0)))
        for n in nodes:
            if not n.get('sprite') or not n.get('visible',[0,self.spec['duration']])[0]<=t<=n.get('visible',[0,self.spec['duration']])[1]:continue
            image=self.images[n['sprite']];matrix=matrices[n['id']]
            layer=self.warp(image,matrix);alpha=value(n.get('opacity'),t,1)
            if alpha!=1:layer.putalpha(layer.getchannel('A').point(lambda x:round(x*alpha)))
            if n.get('wash'):
                wash=Image.alpha_composite(wash,layer);continue
            matte=self.matte(n)
            if matte:
                cover=self.warp(matte,matrix)
                strength=n.get('occlusion_strength',1)
                if strength!=1:cover=cover.point(lambda x:round(x*strength))
                ink.putalpha(ImageChops.multiply(ink.getchannel('A'),ImageChops.invert(cover)))
            ink=Image.alpha_composite(ink,layer)
        return Image.alpha_composite(wash,ink)


def export(scene,folder):
    import guide_motion_render as old
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
    sights=old.viewfinder();duration=scene.spec['duration']
    # Source composition is complete before the single final opacity pass.
    frames=[scene.render(i/FPS) for i in range(math.ceil(duration*FPS))]
    for name,with_ui in [('guide',False),('guide_with_guides',True)]:
        images=[old.alpha50(Image.alpha_composite(f,sights) if with_ui else f) for f in frames]
        images[0].save(folder/(name+'.png'),save_all=True,append_images=images[1:],duration=1000/FPS,loop=0,disposal=0,blend=0)
    old.alpha50(frames[0]).save(folder/'poster.png')
    old.alpha50(Image.alpha_composite(frames[0],sights)).save(folder/'poster_with_guides.png')
    strip=Image.new('RGB',(1080,320),'#23343e')
    for i,p in enumerate([0,.2,.4,.6,.8,1]):
        frame=frames[min(len(frames)-1,round(p*(len(frames)-1)))]
        strip.paste(old.background(old.alpha50(Image.alpha_composite(frame,sights))).resize((180,320)),(180*i,0))
    strip.save(folder/'strip.png')
    (folder/'scene.json').write_text(json.dumps(scene.spec,indent=2)+'\n')
    (folder/'guide.json').write_text(json.dumps(dict(id=scene.spec['id'],duration=duration,fps=FPS,samples=len(frames),alpha_factor=.5,
            method='Separate reusable raster sprites, attachment joints, perspective depth and invisible occlusion masks',
            style='Open linework over an independent broad scene-wide wash',scene=scene.spec,
            sources={n['sprite']:scene.library[n['sprite']]['sha256'] for n in scene.spec['nodes'] if n.get('sprite')},device_validation=False),indent=2)+'\n')
    print(f'Exported sprite proof {scene.spec["id"]}: {len(frames)} frames.',flush=True)


def bar_spec():
    move=[dict(t=0,v=0),dict(t=1.0,v=0),dict(t=4.2,v=.35),dict(t=6,v=.35)]
    forward=[dict(t=0,v=0),dict(t=1.0,v=0),dict(t=4.2,v=.05),dict(t=6,v=.05)]
    return dict(id='bar_low_truckr_mm',duration=6.,camera=dict(x=move,forward=forward,focal_px=405),
                explanation='Low customer-side rightward truck: all world layers slide left; closer layers slide more and grow slightly more. No object is baked into another.',
                nodes=[
                    dict(id='wash',sprite='scene_wash',position=[220,360],height=620,depth=8,order=0,wash=True,opacity=.18),
                    dict(id='far_bottles',sprite='bar_backwall',position=[230,205],height=235,depth=4.5,order=1,opacity=.75),
                    dict(id='counter',sprite='bar_counter',position=[250,430],height=280,depth=2.7,order=2,occlusion='counter'),
                    dict(id='whiskey',sprite='whiskey_glass',parent='counter',attach='glass_contact',anchor='base',height=95,order=3,occlusion='solid',occlusion_strength=.4),
                    dict(id='near_stool',sprite='bar_stool',position=[110,520],height=400,depth=1.45,order=4,occlusion='stool'),
                ])


def kettle_spec():
    library=json.loads((OUT/'library.json').read_text())['sprites']
    def delta(name,a,b,height):
        r=library[name];w,h=r['size'];av,bv=r['anchors'][a],r['anchors'][b]
        return np.array([(bv[0]-av[0])*w*height/h,(bv[1]-av[1])*height])
    hand_height=85;kettle_height=150
    hand_delta=delta('hand_grip','wrist','grip',hand_height)
    kettle_delta=delta('kettle','grip','spout',kettle_height)
    def wrist(spout,hand_angle):
        return (np.array(spout)-R(hand_angle-5)[:2,:2]@kettle_delta-R(hand_angle)[:2,:2]@hand_delta).tolist()
    first=wrist([275,325],5);pour=wrist([300,365],28)
    return dict(id='reusable_kettle_arm',duration=7.,camera={},
        explanation='One existing kettle sprite rotates at the hand grip. Separate upper arm and forearm follow elbow/wrist joints; cup and menu remain independent.',
        points=dict(shoulder=[-120,150],wrist=[dict(t=0,v=first),dict(t=1,v=first),dict(t=2.6,v=pour),dict(t=4.5,v=pour),dict(t=5.6,v=first)]),
        ik=[dict(shoulder='shoulder',wrist='wrist',elbow='elbow',upper=170,lower=150,side=-1)],
        nodes=[dict(id='wash',sprite='scene_wash',position=[210,360],height=560,depth=8,order=0,wash=True,opacity=.16),
               dict(id='rig',position=[0,0],depth=2,order=0),
               dict(id='upper',sprite='arm_upper',parent='rig',segment=['shoulder','elbow'],source_joints=['shoulder','elbow'],order=1,occlusion='solid'),
               dict(id='fore',sprite='arm_fore',parent='rig',segment=['elbow','wrist'],source_joints=['elbow','wrist'],order=2,occlusion='solid'),
               dict(id='grip',sprite='hand_grip',parent='rig',point='wrist',height=hand_height,anchor='wrist',rotation=[dict(t=0,v=5),dict(t=1,v=5),dict(t=2.6,v=28),dict(t=4.5,v=28),dict(t=5.6,v=5)],order=4,occlusion='solid'),
               dict(id='kettle',sprite='kettle',parent='grip',attach='grip',anchor='grip',height=kettle_height,rotation=-5,order=3,occlusion='solid'),
               dict(id='cup',sprite='cup_eye',position=[315,480],height=105,depth=2,order=5,occlusion='solid'),
               dict(id='stream',sprite='pour_stream',segment=['kettle:spout','cup:rim'],source_joints=['start','end'],thickness=2.5,order=6,visible=[2.4,4.6],opacity=[dict(t=2.4,v=0),dict(t=2.7,v=.9),dict(t=4.3,v=.9),dict(t=4.6,v=0)]),
               ])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['extract','proofs'])
    args=parser.parse_args()
    if args.action=='extract':extract()
    else:
        for spec in [bar_spec(),kettle_spec()]:export(Scene(spec),ROOT/'catalog/sprite-study'/spec['id'])
