"""Camera rostrum and cutout animation of immutable AI-painted raster artwork.

No illustrations are drawn here. Camera windows sample a single painting; rigid
layers use deterministic transforms and occlusion, as in a multiplane camera.
The caller applies the final global opacity after the completed composition.
"""
import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

GUIDES=Path(__file__).resolve().parents[1]
ROOT=GUIDES.parent
OUT=GUIDES/'watercolor_motion'
LOCAL=OUT/'local-motion'
ASSETS=LOCAL/'assets'
W,H=405,720


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def progress(entry,t,eased):
    window=entry['rendering'].get('motion_window',entry['windows'][0])
    return eased((t-window['start'])/(window['end']-window['start']),window.get('ease','inOutSine'))


def load(entry):
    result=[]
    for layer in entry['rendering']['layers']:
        assert digest(layer['image'])==layer['sha256'],layer['image']
        result.append(Image.open(layer['image']).convert('RGBA'))
    return result


def transformed(image,layer,p):
    x,y,height,angle=[a+(b-a)*p for a,b in zip(layer['start'],layer['end'])]
    scale=height/image.height
    c=math.cos(math.radians(angle))/scale;s=math.sin(math.radians(angle))/scale
    ax,ay=layer.get('anchor',[.5,.5]);ax*=image.width;ay*=image.height
    return image.transform((W,H),Image.Transform.AFFINE,
                           (c,s,ax-c*x-s*y,-s,c,ay+s*x-c*y),
                           resample=Image.Resampling.BICUBIC)


def frame_at(images,entry,t,eased):
    config=entry['rendering'];p=progress(entry,t,eased)
    result=Image.new('RGBA',(W,H))
    for image,layer in zip(images,config['layers']):
        paint=transformed(image,layer,p)
        if layer.get('occluder'):
            # A painted foreground hides the painting behind it even when its
            # own watercolor alpha is pale. The final clip stays translucent.
            support=paint.getchannel('A').point(lambda a:min(255,a*12))
            result.putalpha(ImageChops.multiply(result.getchannel('A'),ImageOps.invert(support)))
        result=Image.alpha_composite(result,paint)
    if config.get('post_whip') and len(entry['windows'])>1:
        w=entry['windows'][1]
        q=eased((t-w['start'])/(w['end']-w['start']),w['ease'])
        if q==0:return result
        direction=config.get('whip_direction','right')
        dx=W*1.7*q*(1 if direction=='right' else -1) if direction in ('left','right') else 0
        dy=H*1.7*q*(1 if direction=='down' else -1) if direction in ('up','down') else 0
        result=result.transform((W,H),Image.Transform.AFFINE,(1,0,dx,0,1,dy),Image.Resampling.BICUBIC)
    return result


def fit(image,size=(W,H)):
    scale=min(size[0]/image.width,size[1]/image.height)
    im=image.resize((round(image.width*scale),round(image.height*scale)),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',size);canvas.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2))
    return canvas


def save_asset(name,image):
    ASSETS.mkdir(parents=True,exist_ok=True)
    path=ASSETS/(name+'.png');image.save(path)
    return path.resolve()


def layer(path,start,end=None,**kwargs):
    return dict(image=str(Path(path).resolve()),sha256=digest(path),start=start,end=end or start,**kwargs)


def plan():
    import guide_motion_render as render
    manifest=render.read_manifest();entries={e['id']:e for e in manifest['guides']}
    baseline=LOCAL/'baseline';baseline.mkdir(parents=True,exist_ok=True)
    for path in (OUT/'manifest.json',ROOT/'catalog/regeneration-report.json',ROOT/'catalog/regeneration-report.md'):
        dest=baseline/path.name
        if not dest.exists():shutil.copy2(path,dest)
    baseline_entries={e['id']:e for e in json.loads((baseline/'manifest.json').read_text())['guides']}
    legacy=json.loads((GUIDES/'watercolor/manifest.json').read_text())
    old_assets={a['id']:a for a in legacy['assets']}
    changed=[]

    def adopt(gid,config,source,review):
        entry=entries[gid]
        previous=ROOT/'catalog/animations'/gid
        backup=ROOT/'catalog/backups/pre-local-motion/animations'/gid
        if previous.exists() and not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(previous,backup)
        entry.setdefault('before_local_motion',dict(original=entry.get('original'),status=entry['status'],review=entry.get('review'),rendering=entry.get('rendering')))
        entry.update(rendering=config,original=str(Path(source).resolve()),single_pose=True,status='keyframes_reviewed',review=review)
        entry.pop('hold_cell',None);entry.pop('frame_sequence',None)
        entry['local_motion_sources']=config.get('sources',[str(source)])
        changed.append(gid)

    def crop(gid,image,mode,start,end=None,source=None,**extra):
        path=save_asset(gid+'-master',image)
        config=dict(method='single_source_crop',master=str(path),master_sha256=digest(path),
                    mode=mode,start_rect=start,end_rect=end or start,sources=[str(source or path)],
                    sensor_scenarios_changed=False,synthetic_subject_motion=False,
                    note='One immutable painted image; deterministic camera window, no generated intermediate frames.',**extra)
        adopt(gid,config,path,'Camera framing/movement stabilized from matching painted artwork. '+extra.get('limitation',''))

    def cells(gid):
        # Always read the original baseline atlas when the planner is rerun.
        return render.atlas_cells(baseline_entries[gid])[0]

    def art(name):return Image.open(LOCAL/'originals'/(name+'.png')).convert('RGBA')
    def old(gid):
        p=Path(old_assets[legacy['guides'][gid]['asset']]['original'])
        return Image.open(p).convert('RGBA'),p
    def camera_pan(gid,image,source,direction='right',distance=85,canvas_width=1000,start_x=None,**extra):
        master=fit(image,(canvas_width,H));x=(canvas_width-W)/2-distance/2 if start_x is None else start_x
        delta=distance if direction=='right' else -distance
        crop(gid,master,'pan',[x,0,W,H],[x+delta,0,W,H],source,**extra)
    def layers(gid,items,mode,sources,**extra):
        config=dict(method='layered_animation',mode=mode,layers=items,sources=[str(p) for p in sources],
                    sensor_scenarios_changed=False,synthetic_subject_motion=True,
                    note='Fixed painted cutouts with rigid local motion; no optical-flow morphing or regenerated poses.',**extra)
        adopt(gid,config,items[0]['image'],'Rigid painted layers and explicit camera/subject motion. '+extra.get('limitation',''))

    # Low bar: continuous, wider public-side view; rightward camera -> leftward art.
    camera_pan('bar_low_truckr_mm',art('bar-panorama'),LOCAL/'originals/bar-panorama.png',distance=75,canvas_width=1800)
    case,case_source=old('shelf_slide_left')
    camera_pan('case_eye_truckr_mm',case,case_source)
    for gid,name in [('room_eye_panr_ww_whipout','cafe-panorama'),('room_crowd_eye_panr_ww_whipout','crowd-panorama')]:
        camera_pan(gid,art(name),LOCAL/'originals'/(name+'.png'),distance=300,canvas_width=1400,start_x=0,
                   limitation='Image-plane panorama approximates camera yaw. The source artwork remains fixed.')
    board,board_source=old('menu_board_low_tiltd_mm')
    crop('menu_board_low_tiltd_mm',fit(board),'tilt',[80,-20,245,435],[80,310,245,435],board_source)
    for gid,index in [('facade_eye_hold',0),('facade_window_pov_hold',3)]:
        crop(gid,cells(gid)[index],'hold',[0,0,W,H],source=entries[gid]['original'],
             limitation='Camera hold is demonstrated; the ordering gesture is not newly animated.' if 'window' in gid else '')
    cup=cells('cup_eye_orbitr_cc')[0]
    crop('cup_eye_hold_whipout',cup,'whip',[0,0,W,H],[W*1.7,0,W,H],entries['cup_eye_orbitr_cc']['original'],
         limitation='Whip exits the shot. The next pastry shot is a separate take; steam is held, not synthesized.')

    # Reusable original paintings and occluders. Foreground and room never morph.
    wall=LOCAL/'originals/foreground-wall.png'
    palm=LOCAL/'originals/foreground-palm.png'
    chair=save_asset('salon-chair-background',cells('chair_reveal_frame')[5])
    face=save_asset('mouthless-face-background',cells('before_front_back')[0])
    changing,changing_source=old('room_changing_pov_reveal_cm')
    changing=save_asset('changing-room-background',fit(changing.crop((600,0,changing.width,changing.height))))
    dining=save_asset('dining-room-background',fit(art('cafe-panorama').crop((800,0,1300,724))))
    brunch=save_asset('brunch-room-background',fit(art('crowd-panorama').crop((1000,0,1500,724))))
    cup_layer=save_asset('foreground-cup',cup)
    cape_source=Image.open(OUT/'masters/hair_work_high_in_cd_through.png').convert('RGBA')
    cape=save_asset('foreground-cape-texture',cape_source.crop((120,430,300,560)))
    specs={
        'chair_reveal_frame':(chair,wall,'wall'),
        'room_changing_pov_reveal_cm':(changing,wall,'wall'),
        'room_dining_eye_reveal_cw':(dining,wall,'wall'),
        'room_dining_eye_reveal_cw_whipout':(dining,wall,'wall'),
        'room_lesson_eye_reveal_cw':(LOCAL/'originals/room-lesson.png',wall,'wall'),
        'room_treatment_eye_reveal_cm':(LOCAL/'originals/room-treatment.png',wall,'wall'),
        'room_waiting_eye_reveal_cw':(LOCAL/'originals/room-waiting.png',wall,'wall'),
        'room_cupreveal_eye_reveal_dw':(brunch,cup_layer,'cup'),
        'selfie_reveal_eye_reveal_cc':(face,palm,'palm'),
        'selfie_reveal_eye_reveal_cm':(face,cape,'cape'),
    }
    for gid,(bg,fg,kind) in specs.items():
        background=save_asset(gid+'-background',fit(Image.open(bg).convert('RGBA')))
        items=[layer(background,[202.5,360,720,0],[184.5,360,720,0])]
        if kind=='wall':items.append(layer(fg,[254,360,900,0],[-350,360,900,0],occluder=True))
        if kind=='palm':items.append(layer(fg,[202,360,2160,0],[-900,360,2160,0],anchor=[.51,.66],occluder=True))
        if kind=='cup':items.append(layer(fg,[202,360,2880,0],[-900,360,2880,0],occluder=True))
        if kind=='cape':items.append(layer(fg,[202,360,900,0],[-1300,360,900,0],occluder=True))
        layers(gid,items,'reveal',[bg,fg],post_whip='whipout' in gid)

    # Three immutable tasting glasses at three speeds demonstrate parallax.
    flight=art('flight-sprites');items=[]
    for i,(x,y,height,travel) in enumerate([(315,315,170,30),(215,365,205,55),(110,425,245,80)]):
        sprite=flight.crop((i*724,0,(i+1)*724,724));sprite=sprite.crop(sprite.getchannel('A').getbbox())
        p=save_asset('flight-glass-'+str(i),sprite)
        items.append(layer(p,[x,y,height,0],[x-travel,y,height,0]))
    layers('glass_flight_high_truckr_cc',items,'parallax',[LOCAL/'originals/flight-sprites.png'])

    clink=art('clink-hand-glass-blue') if (LOCAL/'originals/clink-hand-glass-blue.png').exists() else art('clink-hand-glass')
    right=save_asset('clink-right',clink);left=save_asset('clink-left',ImageOps.mirror(clink))
    # The rims' contact is a geometric target, not an independently drawn pose.
    clink_source=LOCAL/'originals'/('clink-hand-glass-blue.png' if (LOCAL/'originals/clink-hand-glass-blue.png').exists() else 'clink-hand-glass.png')
    layers('glasses_clink_center',[
        layer(left,[65,400,380,0],[137,400,380,8]),
        layer(right,[340,400,380,0],[268,400,380,-8])],
        'clink',[clink_source],motion_window=dict(start=1.2,end=2.7,ease='inOutSine'))
    counter=save_asset('counter-background',fit(art('counter-background')))
    hand=LOCAL/'originals/lowering-hand-glass.png'
    layers('glass_eye_tiltd_cc',[
        layer(counter,[202,360,720,0],[202,270,720,0]),
        layer(hand,[202,260,360,0],[202,280,360,0])],
        'tilt_follow',[counter,hand],limitation='Rigid glass/hand lowers while the camera tilts; no finger articulation.')
    layers('glass_favorite_eye_in_cd',[
        layer(face,[202,360,720,0]),
        layer(hand,[202,1090,620,0],[202,390,760,0])],
        'prop_reveal',[face,hand],limitation='One rigid glass-and-hand cutout rises over the mouthless face.')

    # Reuse only individually audited artwork with matching viewpoint and <=2 hands.
    reuse='''card_label_high_hold_whipout details_salon_high_whip_dd_whipout facade_line_eye_panr_ww_whipout hands_garment_high_hold hands_tool_top_hold_whipout latte_top_in_cd latte_top_in_cd_whipout machine_low_in_mc_whipout menu_board_eye_truckr_mm menu_board_low_truckl_mm menu_desk_high_hold menu_pricelist_eye_in_mc menu_pricelist_eye_out_dm over_shoulder_till_os_in_md person_barber_eye_hold person_full_low_hold person_host_eye_whip_mm person_mirror_eye_hold person_mirror_eye_out_cm person_one_eye_hold person_player_eye_out_dm person_process_pov_in_mc_through plate_bite_top_hold plate_kids_top_hold plate_spread_top_hold plate_spread_top_out_cw plate_spread_top_out_dw rail_bottle_eye_truckr_mm rail_dumbbell_eye_truckr_cc rail_garment_eye_truckr_cc_whipout rail_garment_eye_truckr_mm rail_guitar_pov_truckr_mm rail_shelf_eye_truckr_mm_whipout shelf_slide_left'''.split()
    for gid in reuse:
        image,source=old(gid);entry=entries[gid]
        if gid.startswith('menu_pricelist'):
            # Select the existing board, excluding all bystanders and their hands.
            mask=Image.new('L',image.size);ImageDraw.Draw(mask).polygon([(485,590),(920,622),(870,1255),(928,1295),(910,1315),(330,1223),(324,1180),(348,1157)],fill=255)
            mask=mask.filter(ImageFilter.GaussianBlur(.6));image.putalpha(ImageChops.multiply(image.getchannel('A'),mask))
            image=image.crop(image.getchannel('A').getbbox())
        follows=[s for s in entry['source_live_steps'] if s['kind']=='follow']
        move=next((s for s in follows if s['action']!='whip'),None)
        whip=next((s for s in follows if s['action']=='whip'),None)
        if move and move['action'] in ('truck','pan'):
            camera_pan(gid,image,source,move.get('direction','right'),distance=90,
                       limitation='Fixed painting approximates camera translation; no new perspective is synthesized.')
            continue
        master=fit(image)
        focus=(.5,.5)
        if gid.startswith('person_mirror'):focus=(.64,.3)
        if gid.startswith('person_player'):focus=(.5,.3)
        if gid.startswith('over_shoulder_till'):focus=(.66,.75)
        if gid.startswith('person_process'):focus=(.83,.48)
        amount=float(move.get('amount',1.5)) if move else 1
        extent=max(amount,1/max(.001,amount))
        if gid.startswith('person_process'):extent=6
        if gid.startswith('card_label'):extent=2
        def rect(z):
            if z==1:return [0,0,W,H]
            return [focus[0]*W-W/2/z,focus[1]*H-H/2/z,W/z,H/z]
        mode=move['action'] if move else 'hold'
        start=rect(extent if mode=='dolly_out' or gid.startswith('card_label') else 1)
        end=rect(extent if mode=='dolly_in' else 1)
        if not move:end=start.copy()
        if whip and not move:
            mode='whip';end=start.copy();direction=whip.get('direction','right')
            axis=0 if direction in ('left','right') else 1
            end[axis]+=start[axis+2]*1.7*(1 if direction in ('right','down') else -1)
        if gid=='person_host_eye_whip_mm':
            start=[-W*1.7,0,W,H];end=[0,0,W,H]
        if gid=='details_salon_high_whip_dd_whipout':
            mode='pan';start=[0,340,180,320];end=[190,340,180,320]
        crop(gid,master,mode,start,end,source,
             limitation='Camera movement/hold is illustrated. Independent finger or working actions are not synthesized.')

    # Correct the known window scene and its descriptive down-whip direction.
    gid='facade_window_eye_in_wm_whipout';im=cells(gid)[0]
    crop(gid,im,'dolly_in',[0,0,W,H],[75,110,255,453],entries[gid]['original'],whip_direction='down',
         limitation='Downward exit follows the written shot. Legacy sensor direction is retained unchanged.')

    manifest['local_motion']=dict(method='multiplane raster cutout animation',new_source_images=12,generated_outputs_including_edit=13,
                                  guide_count=len(changed),guide_ids=sorted(changed),alpha_factor=.5)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (LOCAL/'guide-ids.json').write_text(json.dumps(sorted(changed),indent=2)+'\n')
    audit(manifest)
    print(f'Prepared {len(changed)} precise local-motion guides.')


def audit(manifest=None):
    if manifest is None:manifest=json.loads((OUT/'manifest.json').read_text())
    mismatches={
        'cup_pour_eye_hold':'Existing art looks down onto the plate; required resource-height camera is missing.',
        'cup_shot_eye_in_cd_through':'Existing cup angle looks down; requires resource-height master.',
        'hands_dough_top_hold':'Existing art is oblique, not strict overhead; visitor-side access unproven.',
        'hands_top_hold':'Existing art is oblique, not strict overhead; visitor-side access unproven.',
        'hands_wrap_top_hold':'Existing art is oblique, not strict overhead; visitor-side access unproven.',
        'hands_during_top_hold':'Existing patient POV does not establish the required overhead angle.',
        'hands_griddle_high_hold':'Existing art implies restricted staff prep viewpoint.',
        'person_group_eye_hold':'Existing image exceeds two visible hands.',
        'room_game_pov_panl_mm_whipout':'Existing audience and player exceed two visible hands.',
        'tap_pour_glass':'Existing art shows cocktail pouring rather than a beer tap.',
        'plate_sizzle_low_in_cd':'Existing art has the wrong food/action and camera height.',
        'plate_spread_eye_out_dw':'Existing art looks down instead of from resource height.',
        'plate_yolk_high_in_cd':'Existing art is overhead instead of the required oblique high view.',
        'pastry_tear_open':'Needs separate hands/pastry halves over a fixed plate; source has baked-in background.',
        'bag_handoff_low_hold':'Needs isolated tray/hands over the fixed window; holding the whole scene would omit the handoff.',
        'glass_build_eye_hold':'Needs isolated pouring/building layers; holding the finished glass would omit the action.',
    }
    records=[]
    for e in manifest['guides']:
        gid=e['id'];cfg=e.get('rendering',{});method=cfg.get('method')
        if method in ('single_source_crop','layered_animation'):
            status='applied';reason=cfg.get('note','');recipe=cfg['mode']
        else:
            actions=[s.get('action','') for s in e['source_live_steps']]
            genuine=any(a in ('orbit','turn') for a in actions) or 'orbitr' in gid or 'orbitl' in gid or gid in ('before_front_back','person_curtain_low_reveal_dm')
            if genuine:
                status='requires_viewpoints';recipe='consistent perspective/pose keyframes'
                reason='A real orbit or person turn exposes new surfaces; a rigid flat crop/flip would teach the wrong shot.'
            elif gid in mismatches or gid.startswith(('hands_work','plate_low','door_sauna','pov_door_entry')):
                status='needs_matching_layers';recipe='isolated action layers or corrected camera master'
                reason=mismatches.get(gid,'Existing artwork cannot provide the required angle/action without new matching layers.')
            else:
                status='needs_matching_art';recipe='panorama' if any(a in ('pan','truck') for a in actions) else 'single master and camera crop'
                reason='Local mechanics are feasible, but no matching, individually verified source is available in this batch.'
        records.append(dict(id=gid,status=status,recipe=recipe,reason=reason,description=e['description'],sources=cfg.get('sources',[cfg['master']] if cfg.get('master') else []),limitation=cfg.get('limitation','')))
    counts={s:sum(r['status']==s for r in records) for s in sorted({r['status'] for r in records})}
    report=dict(date='2026-10-25',total=len(records),counts=counts,new_generated_source_images=12,generated_outputs_including_edit=13,
                sensor_scenarios_changed=False,previews_changed=False,alpha_factor=.5,guides=records)
    (ROOT/'catalog/local-motion-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['# Local animation audit','','All 178 guides were checked for camera/subject mechanics and matching reusable artwork. Fixed paintings and cutouts preserve linework between frames. Source script previews and sensor scenarios are unchanged.','',
           'New source artwork: 12 immutable AI-painted resources, reused across multiple guides. Global alpha is multiplied by 0.5 once after composition. No artwork is drawn with geometric primitives.','',
           'A crop/pan is an image-plane camera approximation, not a newly reconstructed 3D viewpoint. True orbits and actor turns require consistent perspective/pose artwork. Independent finger, steam, pouring and working actions are not synthesized in camera-only guides.','',
           '| Result | Guides |','|---|---|']
    lines += [f'| {s.replace("_"," ")} | {n} |' for s,n in counts.items()]
    lines += ['', '| Guide | Result / mechanic | Reason / limitation |','|---|---|---|']
    for r in records:lines.append(f'| [{r["id"]}](animations.html#{r["id"]}) | {r["status"].replace("_"," ")} / {r["recipe"]} | {r["limitation"] or r["reason"]} |')
    (ROOT/'catalog/local-motion-audit.md').write_text('\n'.join(lines)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['plan','audit','previews'])
    args=parser.parse_args()
    if args.action=='plan':plan()
    elif args.action=='audit':print(audit()['counts'])
    else:
        import guide_motion_render as render
        render.previews(json.loads((LOCAL/'guide-ids.json').read_text()))
