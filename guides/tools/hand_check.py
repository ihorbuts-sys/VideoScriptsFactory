"""Per frame: forearm cut end in frame (and its fade distance from the grip); hand penetration into cup, saucer, plate, counter/table."""
import bpy,json,math,sys
import numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene;cam=sc.camera
args=sys.argv[sys.argv.index('--')+1:];frames=range(1,sc.frame_end+1) if args[0]=='all' else [int(a) for a in args]
def interp(x,pts):
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        if x0<=x<=x1:return y0+(y1-y0)*(x-x0)/(x1-x0)
    return None
hands=[o for o in sc.objects if o.get('p0_hand')]
meshes={h.name:next(c for c in h.children_recursive if c.type=='MESH') for h in hands}
cups=[o for o in sc.objects if o.type=='MESH' and o.name.endswith('hollow ceramic body') and abs(o.matrix_world.translation.z-1.06)<.02]
saucers=[o for o in sc.objects if o.type=='MESH' and o.name.startswith('Saucer')]
plates=[o for o in sc.objects if o.type=='MESH' and o.name.startswith('Plate with formed rim')]
counter=any(o.name.startswith('Customer counter top') for o in sc.objects)
worst={};endvis=[]
for f in frames:
    sc.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    for hn,m in meshes.items():
        ev=m.evaluated_get(deps);me=ev.to_mesh();M=ev.matrix_world
        P=np.array([tuple(M@v.co) for v in me.vertices])
        # boundary edges = the opened forearm end
        cnt={}
        for p in me.polygons:
            for k in p.edge_keys:cnt[k]=cnt.get(k,0)+1
        ends=sorted({i for k,c in cnt.items() if c==1 for i in k})
        lm=json.loads(m['landmarks']);grip=M@Vector(lm['f_middle.03'])
        # landmark is pre-reshape; use the nearest vertex instead
        gi=int(np.argmin(np.linalg.norm(P-np.array(grip),axis=1)));g=P[gi]
        inframe=[]
        for i in ends:
            v=world_to_camera_view(sc,cam,Vector(P[i]))
            if v.z>0 and 0<=v.x<=1 and 0<=v.y<=1:inframe.append(i)
        dist=float(np.min(np.linalg.norm(P[ends]-g,axis=1))) if ends else None
        print('ENDS',f,hn,len(ends),[tuple(round(c,2) for c in world_to_camera_view(sc,cam,Vector(P[i])))[:2] for i in ends[:3]]) if f in (1,9) else None
        if inframe:endvis.append((f,hn,len(inframe),round(dist,3)))
        ev.to_mesh_clear()
        def note(k,d):
            if d>worst.get(k,(0,0))[0]:worst[k]=(d,f)
        if counter:
            sel=(P[:,0]>-1.4)&(P[:,0]<1.4)&(P[:,1]>-.155)&(P[:,1]<.75);d=1.05-P[sel,2]
            note('counter',float(d.max()) if len(d) else 0)
        else:
            r=np.hypot(P[:,0]-.22,P[:,1]-.18);sel=r<.70;d=.785-P[sel,2];note('table',float(d.max()) if len(d) else 0)
        for c in cups:
            o=c.matrix_world.translation;h=P[:,2]-o.z;r=np.hypot(P[:,0]-o.x,P[:,1]-o.y)
            prof=np.where(h<.085,.035+(.054-.035)*np.clip(h,0,.085)/.085,.054);sel=(h>0)&(h<.118)
            note('cup',float((prof-r)[sel].max()) if sel.any() else 0)
        for s_ in saucers:
            o=s_.matrix_world.translation;h=P[:,2]-o.z;r=np.hypot(P[:,0]-o.x,P[:,1]-o.y)
            top=np.array([interp(min(x,.088),[(0,.010),(.048,.010),(.080,.017),(.088,.012)]) for x in r]);sel=(r<.088)&(h>0)
            note('saucer',float((top-h)[sel].max()) if sel.any() else 0)
        for pl in plates:
            o=pl.matrix_world.translation;h=P[:,2]-o.z;r=np.hypot(P[:,0]-o.x,P[:,1]-o.y);sel=r<.151
            if sel.any():
                top=np.array([interp(x,[(0,.009),(.09,.009),(.115,.015),(.139,.030),(.151,.029)]) for x in r[sel]])
                bot=np.array([interp(x,[(0,0),(.09,0),(.13,.012),(.151,.022)]) for x in r[sel]])
                hs=h[sel];inside=(hs<top)&(hs>bot);note('plate',float((top-hs)[inside].max()) if inside.any() else 0)
print('HANDCHECK worst penetration (m, frame) all hands:',{k:(round(v[0],4),v[1]) for k,v in worst.items()})
print('HANDCHECK cut end in frame:',endvis[:20],'count',len(endvis))
