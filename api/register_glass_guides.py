"""Register reviewed glass assets for their exact template/step contexts."""
import argparse
import hashlib
import json
import os
import math
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE/'catalog/glass-rollout/coffee'
MANIFEST=BASE/'catalog/clay-scenes/active-revisions.json'
LIVE=Path('/Users/ihor.buts/Documents/Development/Scriptwriter/catalog/catalog.json')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path,data):path.write_text(json.dumps(data,indent=2)+'\n')


def scenario(plan,source,phase):
    gid=plan['guide'];capture=plan['capture']
    previous=json.loads((BASE/'guides/scenarios'/(gid+'.json')).read_text())
    moves={
        'cup_shot_eye_in_cd_through':('dolly_in','subject_scale',3.43,None,5),
        'over_shoulder_counter_os_hold':('truck','image_motion',.2,'right',6.3),
        'cup_eye_orbitr_cc':('orbit','orbit',None,'right',4),
        'cup_high_out_dm':('dolly_out','subject_scale',.55,None,4.8),
        'cup_eye_hold_whipout':('dolly_out','subject_scale',.70,None,4),
        'pastry_tear_open':('dolly_in','image_scale',1.5,None,3.4),
        'menu_board_low_tiltd_mm':('tilt','gravity_tilt',.7,'down',3.7),
        'interior_pan':('pan','gyro_yaw',1.0,'left',5),
        'entrance_inside_eye_in_wm':('dolly_in','image_scale',1.5,None,4),
    }
    if 'action' in plan:
        action,channel,amount,direction,move_end=(plan[k] for k in ['action','channel','amount','turn','move_end'])
    else:
        action,channel,amount,direction,move_end=moves[gid]
    samples=source.get('camera',{}).get('samples',[])
    first=phase['source_first_frame']-1 if phase else 0
    def pitch(index,fallback):
        if not samples:return fallback
        row=samples[min(index,len(samples)-1)]
        if 'target' not in row:return fallback
        p,q=row['position'],row['target'];horizontal=math.hypot(p[0]-q[0],p[1]-q[1])
        return round(math.degrees(math.atan2(p[2]-q[2],horizontal)),1)
    start=pitch(first,0);end=pitch(first+round(capture*15),start)
    kind='none' if gid in ['over_shoulder_counter_os_hold','menu_board_low_tiltd_mm','interior_pan','entrance_inside_eye_in_wm'] else 'salient'
    subject='bread' if gid=='pastry_tear_open' else 'window' if gid=='interior_pan' else 'facade' if gid=='entrance_inside_eye_in_wm' else 'menu_board' if gid=='menu_board_low_tiltd_mm' else 'cup'
    if gid.startswith(('room_','table_')):kind,subject='none','table' if gid.startswith('table_') else 'room'
    if plan.get('anchor_type'):
        kind,subject=plan.get('anchor_kind','salient'),plan['anchor_type']
    hold=max(.1,capture-move_end);duration=round(capture-1.2-hold,3)
    follow=dict(kind='follow',action=action,channel=channel,duration=duration,level=4,icon=dict(symbol=action,mods=[]))
    if direction:follow['direction']=direction
    if amount is not None:follow['amount']=amount
    if action=='orbit':follow['arc']=plan.get('arc',55)
    if action=='still':
        follow=dict(kind='still',duration=duration,subject_motion=plan.get('subject_motion',''),
            level=4,tilt=dict(target=start,tolerance=12),icon=dict(symbol='still',mods=[]))
    previous.update(source='native-3d-glass-rollout',anchor=dict(kind=kind,type=subject),
        steps=[dict(kind='frame',lock_after=.6,tilt=dict(target=start,tolerance=16),level=4,icon=dict(symbol='find_face' if kind=='face' else 'find',mods=['eye','level'] if kind=='face' else [])),
               follow,dict(kind='hold',duration=round(hold,3),tilt=dict(target=end,tolerance=16),level=4,icon=dict(symbol='hold',mods=[],seconds=max(1,round(hold))))])
    return previous,action


def run(first_only):
    catalog=json.loads(LIVE.read_text())
    manifest=json.loads(MANIFEST.read_text())
    plans=[dict(folder=BASE/'catalog/coffee-hologram-study',phase='extraction',
        guide='cup_shot_eye_in_cd_through',template='cafe-before-opening',step='shot',
        capture=5,direction=next(s['direction'] for t in catalog['templates'] if t['id']=='cafe-before-opening' for s in t['steps'] if s['id']=='shot'))]
    if not first_only:
        for folder in sorted(ROOT.iterdir()):
            if not (folder/'scene-spec.json').exists():continue
            review=folder/'review-status.json'
            if review.exists() and json.loads(review.read_text()).get('status')=='rejected':continue
            spec=json.loads((folder/'scene-spec.json').read_text())
            if not (folder/'composite-browser-check.json').exists():continue
            if spec.get('guide_bindings'):
                plans += [dict(binding,folder=folder) for binding in spec['guide_bindings']]
            elif folder.name=='morning-pair':
                plans += [dict(folder=folder,phase='cup',guide='cup_eye_hold_whipout',template='cafe-morning-ritual',step='cup',capture=5,direction=spec['direction']),
                    dict(folder=folder,phase='pastry',guide='pastry_tear_open',template='cafe-morning-ritual',step='pastry',capture=3.4,
                         direction='Continue from the paired cup-and-pastry view. Lean toward the opened pastry, then rise slightly to show both cut faces and the chocolate filling. Keep the pastry on its plate and cut after the detail.')]
            else:
                plans.append(dict(folder=folder,phase=None,guide=spec['guide'],template=spec['template'],step=spec['step'],capture=spec['capture_seconds'],direction=spec['direction']))
    registered=[]
    for plan in plans:
        folder=plan['folder'];source=json.loads((folder/'scene-spec.json').read_text())
        checks=json.loads((folder/'view-overlay-checks.json').read_text())
        browser=json.loads((folder/'composite-browser-check.json').read_text())
        assert checks['status']==browser['status']=='passed'
        assert browser['overlay_sha256']==digest(folder/'view-overlay.png')
        assert checks['image_opacity_baked']==1 and checks['walls_excluded'] and checks['floor_excluded']
        phase=next((p for p in source['exported_phases'] if p['id']==plan['phase']),None)
        target=folder/'phases'/plan['phase'] if phase else folder
        seconds=phase['animation_seconds'] if phase else source['duration_s']
        handover=bool(phase and phase['handover_seconds'])
        scope='shot_and_handover' if handover else 'complete_final_shot'
        status='included' if handover else 'cut_to_next_step'
        dest=BASE/'catalog/glass-rollout/guides'/plan['guide']
        if plan.get('variant_key'):dest=dest/'contexts'/plan['variant_key']
        dest.mkdir(parents=True,exist_ok=True)
        files={}
        for name in ['view-overlay.png','view-overlay-poster.png','view-overlay-strip.jpg','color.mp4']:
            src=target/name;path=dest/name
            temporary=path.with_name(path.name+'.tmp');temporary.unlink(missing_ok=True)
            os.link(src,temporary);os.replace(temporary,path)
            files[name]=digest(path)
        live_scenario,action=scenario(plan,source,phase)
        write(dest/'scenario.json',live_scenario);files['scenario.json']=digest(dest/'scenario.json')
        template=next(t for t in catalog['templates'] if t['id']==plan['template'])
        index=next(i for i,s in enumerate(template['steps']) if s['id']==plan['step'])
        next_guide=template['steps'][index+1]['overlays'][0] if index+1<len(template['steps']) else None
        write(dest/'scene-spec.json',dict(id=plan['guide'],duration_s=seconds,capture_seconds=plan['capture'],
            scope=scope,handover_status=status,next_guide=next_guide,
            transition_method='continuous_same_room' if folder.name=='work-route' and handover else 'continuous_same_table' if handover else 'cut_at_step_boundary',
            source_scene=str(folder.relative_to(BASE)),source_phase=plan['phase'],
            revision=source['revision'],display=source['display'],moves=[action]))
        write(dest/'export-checks.json',dict(status='passed',image_opacity_baked=1,
            max_ghost_alpha=max(p['max_alpha'] for p in checks['phases']),files=files))
        shared=[p for p in plans if p['guide']==plan['guide'] and p['folder']==plan['folder'] and p['phase']==plan['phase'] and p.get('variant_key')==plan.get('variant_key')]
        contexts=[]
        for binding in shared:
            context=dict(template=binding['template'],step=binding['step'],direction=binding['direction'],capture_seconds=binding['capture'])
            if binding.get('update_capture_seconds'):context['update_capture_seconds']=True
            if not any(c['template']==context['template'] and c['step']==context['step'] for c in contexts):contexts.append(context)
        if plan['guide']=='pastry_tear_open':
            step=next(s for t in catalog['templates'] if t['id']=='food-review-sweet' for s in t['steps'] if s['id']=='break')
            contexts.append(dict(template='food-review-sweet',step='break',direction=step['direction'],capture_seconds=step['seconds']))
        for context in contexts:
            owner=next(t for t in catalog['templates'] if t['id']==context['template'])
            position=next(i for i,s in enumerate(owner['steps']) if s['id']==context['step'])
            context['next_guide']=owner['steps'][position+1]['overlays'][0] if position+1<len(owner['steps']) else None
        entry=dict(reviewed=True,
            reviewer='Native camera/prop checks, frame review, encoded-alpha checks and embedded-browser playback',
            scope=scope,handover_status=status,folder=str(dest.relative_to(BASE)),
            context_template=plan['template'],context_step=plan['step'],direction=plan['direction'],
            contexts=contexts,update_global=plan.get('update_global',plan['guide'] not in ['interior_pan','entrance_inside_eye_in_wm']),
            opacity_mode='image_view',revision=source['revision'],
            rendering='native-3d-glass-full-surfaces; image-view-opacity',files=files)
        if plan.get('variant_key'):
            entry['guide_id']=plan['guide']
            manifest.setdefault('guide_variants',{})[plan['variant_key']]=entry
        else:manifest['guides'][plan['guide']]=entry
        registered.append(dict(guide=plan['guide'],contexts=contexts,animation_seconds=seconds))
    write(MANIFEST,manifest)
    report=dict(status='registered',guides=registered)
    ROOT.parent.mkdir(parents=True,exist_ok=True)
    write(ROOT.parent/'registration.json',report)
    print(json.dumps(report))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--first-shot-only',action='store_true');args=p.parse_args();run(args.first_shot_only)
