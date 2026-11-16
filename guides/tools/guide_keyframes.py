"""Description-first generation plan. Inputs are existing GUIDE assets, never script previews."""
import argparse
import copy
import fcntl
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path
from datetime import datetime, timezone

from PIL import Image, ImageSequence

GUIDES=Path(__file__).resolve().parents[1]
ROOT=GUIDES.parent
OUT=GUIDES/'watercolor_motion'
sys.path.insert(0,str(ROOT.parents[3]/'.claude/skills/shot-overlay/scripts'))
import render as native


def different(a,b):
    return any(abs(x-y)>1e-4 for x,y in zip(a,b))


def plan_motion(scene):
    track=scene.tracks['cam']
    windows=[]
    for (t0,a,_),(t1,b,ease) in zip(track,track[1:]):
        if different(a,b):windows.append(dict(start=t0,end=t1,ease=ease))
    windows=windows[:2]
    if len(windows)==1:
        windows[0]['indices']=[0,1,2,3,4,5]
    elif len(windows)==2:
        windows[0]['indices']=[0,1,2,3]
        windows[1]['indices']=[3,4,5]
    else:
        # A still camera may watch a subject action; no camera motion is invented.
        windows=[dict(start=1.2,end=max(1.6,scene.duration-1.4),ease='inOutSine',indices=[0,1,2,3,4,5],camera_static=True)]
    times={}
    for window in windows:
        for i,index in enumerate(window['indices']):
            times.setdefault(index,window['start']+(window['end']-window['start'])*i/(len(window['indices'])-1))
    return windows,[times[i] for i in range(6)]


def source_atlas(path,times,output):
    with Image.open(path) as image:
        frames=[];clock=0
        for frame in ImageSequence.Iterator(image):
            frames.append((clock,frame.convert('RGBA')))
            clock+=frame.info.get('duration',1000/15)/1000
    width,height=405,720
    sheet=Image.new('RGB',(width*2+48,height*3+64),'#1c2931')
    for i,t in enumerate(times):
        frame=max((item for item in frames if item[0]<=t),key=lambda item:item[0],default=frames[0])[1]
        frame=frame.resize((width,height),Image.Resampling.LANCZOS)
        background=Image.new('RGBA',(width,height),'#24343f');background.alpha_composite(frame)
        sheet.paste(background.convert('RGB'),(16+(i%2)*(width+16),16+(i//2)*(height+16)))
    sheet.save(output)


def angle_instruction(elevation,description):
    if 'over-shoulder' in description:
        return 'Over-shoulder viewpoint: shoulder/head edge near the camera, hands/work beyond, viewed from a visitor-accessible position. This must not become a frontal portrait.'
    if elevation>=75:
        return 'Strict near-90-degree TOP-DOWN view. Cup/plate rims are circles, table is seen from directly above. Do not show a side view or oblique 45-degree view.'
    if elevation>=20:
        return f'Camera from ABOVE at about {elevation:g} degrees: clear top surfaces and foreshortening. Do not make it eye-level or straight overhead.'
    if elevation<=-5:
        return 'LOW camera looking UP at the subject. Show undersides/base and appropriate upward perspective. Do not show the top surfaces as if looking down.'
    return 'Horizontal SUBJECT-HEIGHT camera, not a view down from above. For cups/glasses the top rim is a thin ellipse and the liquid surface is hidden by the front wall. For people the lens is at face height. Keep verticals upright.'


def build_plan():
    OUT.mkdir(exist_ok=True)
    for name in ('references','originals','frames','rendered'):(OUT/name).mkdir(exist_ok=True)
    existing={}
    manifest_path=OUT/'manifest.json'
    if manifest_path.exists():existing={entry['id']:entry for entry in json.loads(manifest_path.read_text())['guides']}
    catalog=json.loads((GUIDES/'script_templates.json').read_text())
    ids=sorted({gid for template in catalog['templates'] for step in template['steps'] for gid in step['overlays']})
    style=GUIDES/'shot-proof/cup_eye_orbitr_cc/keyframes-original.png'
    entries=[]
    for gid in ids:
        if gid in existing:
            entries.append(existing[gid]);continue
        data=json.loads((GUIDES/'templates'/f'{gid}.json').read_text())
        spec=json.loads((GUIDES/'overlays/3d'/f'{gid}.json').read_text())
        scene=native.Scene(data,scale=.75,fps=15)
        windows,times=plan_motion(scene)
        reference=OUT/'references'/f'{gid}.png'
        source_atlas(GUIDES/'overlays/schematic'/f'{gid}.png',times,reference)
        elevation=spec['camera'][0].get('elevation_deg',0)
        follows=[step for step in data.get('live',{}).get('steps',[]) if step['kind']=='follow']
        description=data.get('description','')
        camera_spec=dict(model=spec['model'],camera=spec['camera'],subject_turns=spec.get('subject_turns'),
                         live_steps=data.get('live',{}).get('steps',[]),keyframe_times=times)
        prompt=f'''Create ONE six-keyframe artwork atlas for a LIVE SHOT GUIDE. Function and camera geometry come first; watercolor is only the rendering style.

INPUTS:
Image 1 is the existing guide's SIX camera-view keyframes, arranged 2 columns by 3 rows. It defines framing, resource placement, progression, and visible objects. Its dark background is only for legibility, not part of the output.
Image 2 is the guide's 3D camera-reference strip. It defines the viewing height, perspective and path, not the wireframe art style.
Image 3 is the APPROVED watercolor keyframe style. Copy its loose pencil contours, one pale slate-blue watercolor pigment, uneven granulation and wash spilling beyond the lines. Do not copy its cup unless this guide is about a cup.
Do not use script-preview/story illustrations. These are views THROUGH the creator's camera that teach how to frame and move the phone.

GUIDE ID: {gid}
EXISTING DESCRIPTION (the specification): {description}
CAMERA/SCENARIO SPECIFICATION: {json.dumps(camera_spec,separators=(',',':'))}
MANDATORY ANGLE: {angle_instruction(elevation,description)}

The words after "cut to" or "match-cut to" describe the NEXT shot, not another pose inside this guide.
Keep all six cells in this ONE continuous take; never insert a selfie, finished result or another subject
because it is mentioned as the following shot. End on this guide's prescribed final crop.

Make six consistent successive viewpoints of the SAME subject/scene. Keep identities, anatomy, proportions, object design and spatial layout coherent. Respect the starting and ending crop in Image 1; do not recompose every frame as a pretty standalone picture. Where the guide changes size, it must clearly grow/shrink across the six frames. Where it changes angle, show actual new visible surfaces.
Orbit: camera travels around a stationary subject, revealing its far side; keep it centered, upright and at the stated elevation and distance. Never fake orbit by rotating a flat picture.
Pan right: world moves LEFT through the fixed view; pan left: world moves RIGHT. A truck has foreground/background parallax. Tilt down reveals lower parts as the scene moves UP. A push-in makes the subject grow; pull-out starts on detail and reveals context. A whip visibly travels to the destination, not six unrelated stills. A reveal starts behind the foreground blocker and gradually uncovers the subject. Include both start and destination objects when the description requires them.
If the camera is static, keep its angle/framing identical. Show only the subject action actually described (pour, sip, wave, turn, hand-off); otherwise hold the same pose. Do not invent a camera move.
If a push-through fills the ending frame, show its surface/texture filling that cell. For whip-out keep only a faint outgoing edge at the ending cell, so the subject visibly leaves the frame.

OUTPUT: Exactly TWO columns and THREE rows, read left-to-right, top-to-bottom. All cells have the same virtual 9:16 camera frame and equal spacing. Overall portrait atlas about 3:8, with clear transparent gutters and outer margins. No cell borders, labels, timestamps, degree text, arrows, UI or watermark. No solid panel/background rectangles; genuinely transparent background and watercolor fringes.
Only one pale slate-blue pigment. Keep the approved light color; do not darken or saturate it to imitate opacity. Opacity will be applied PROGRAMMATICALLY after ALL generation.
NO MOUTHS, lips, smiles or teeth on any person. Minimal schematic facial features; makeup stays schematic. At most TWO visible hands TOTAL within EACH animation frame, including bystanders and partial hands. Hide other hands. No extra fingers or detached limbs.
Camera must stay in ordinary visitor-accessible space, never inside staff kitchens, behind cash registers or at restricted prep benches. If staff activity is shown, view it from the CUSTOMER side or through a clearly indicated public viewing window. A top-down own-hands task can be at the visitor's own accessible table, with no staff workspace. Do not assume special access. Preserve the described angle; make the public camera position clear.
Do not show a filming phone or operator inside the camera view unless the original guide explicitly contains a setup diagram. A phone that is the actual repair/product subject may be shown.
No text, prices, currency symbols, logos or numbers in the artwork. This is one six-pose guide asset, not six different designs.'''
        entry=dict(id=gid,status='pending',description=description,prompt=prompt,
                   references=[str(reference.resolve()),str((GUIDES/'overlays/3d'/f'{gid}_strip.png').resolve()),str(style.resolve())],
                   source_timeline=data['timeline'],source_live_steps=data.get('live',{}).get('steps',[]),
                   camera_spec=camera_spec,windows=windows,keyframe_times=times,
                   duration=scene.duration,fade=scene.fade,atlas_layout=[2,3])
        if gid=='cup_eye_orbitr_cc':
            destination=OUT/'originals'/f'{gid}.png'
            shutil.copy2(style,destination)
            entry.update(status='approved',original=str(destination.resolve()),review='User approved these six cup-height orbit views. Opacity is a final batch operation.',
                         grid_override={'origins':[[0,60],[470,60],[0,580],[470,580],[0,1100],[470,1100]],'cell_size':[471,535]})
        entries.append(entry)
    manifest=dict(version=2,method='Per-guide descriptions and existing guide views; no script-preview references.',
                  alpha_stage='After all keyframe generation, scale alpha by 0.5 once per output; preserve generated originals.',
                  guides=entries,steps=304,count=len(entries),workflow_status='generation')
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'{len(entries)} guide-specific specifications and motion references ready; approved cup views reused.')


def accept(gid,source):
    with (OUT/'.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        manifest=json.loads((OUT/'manifest.json').read_text())
        entry=next(entry for entry in manifest['guides'] if entry['id']==gid)
        if entry['status']=='approved':raise SystemExit('Do not overwrite approved keyframes.')
        with Image.open(source) as image:
            if image.mode!='RGBA' or image.getchannel('A').getextrema()[0]!=0:raise ValueError('Expected genuine transparency.')
            size=list(image.size)
        destination=OUT/'originals'/f'{gid}.png'
        if destination.exists():
            attempts=OUT/'attempts';attempts.mkdir(exist_ok=True)
            stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            previous=attempts/f'{gid}-{stamp}.png'
            shutil.copy2(destination,previous)
            previous_prompt=OUT/'originals'/f'{gid}-prompt.txt'
            if previous_prompt.exists():shutil.copy2(previous_prompt,previous.with_suffix('.txt'))
            entry.setdefault('attempts',[]).append(dict(original=str(previous.resolve()),source=entry.get('source'),review=entry.get('review')))
        shutil.copy2(source,destination)
        entry.update(status='generated',source=str(source),original=str(destination.resolve()),size=size,
                     sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                     review='Awaiting functional angle/framing/motion review. No opacity modification yet.')
        (OUT/'export-complete.json').unlink(missing_ok=True)
        temporary=OUT/'.accept.tmp';temporary.write_text(json.dumps(manifest,indent=2)+'\n');temporary.replace(OUT/'manifest.json')
        (OUT/'originals'/f'{gid}-prompt.txt').write_text(entry['prompt']+'\n')
    print(f'Saved original keyframes: {gid}. Opacity deferred.')


def refine():
    """Remove following-shot context and describe only this guide's own poses."""
    manifest=json.loads((OUT/'manifest.json').read_text())
    style=OUT/'frames/cup_eye_orbitr_cc/0.png'
    if not style.exists():raise SystemExit('Stage the approved cup first.')
    for entry in manifest['guides']:
        if entry['status'] not in ('pending','needs_revision'):continue
        description=entry['description']
        take=description.split('. ',1)[1] if ': ' in description and '. ' in description else description
        take=take.split(';',1)[0]
        for marker in (', then the frame flicks','; the next shot','; cut','; match-cut'):
            take=take.split(marker,1)[0]
        steps=entry['source_live_steps']
        actions=[s for s in steps if s['kind']=='follow']
        subject_actions=[s.get('subject_motion','') for s in steps if s['kind']=='still']
        static=all(w.get('camera_static') for w in entry['windows'])
        single=static and not subject_actions
        entry['single_pose']=single
        camera=entry['camera_spec']['camera']
        elevation=camera[0]['elevation_deg']
        changes=[]
        previous=camera[0]
        for pose in camera[1:]:
            if any(abs(pose.get(key,0)-previous.get(key,0))>1e-5 for key in ('distance_m','elevation_deg','azimuth_deg','yaw_deg','pitch_deg','lateral_m','subject_turn_deg')):
                changes.append((previous,pose))
            previous=pose
        physical={}
        for wi,window in enumerate(entry['windows']):
            start,end=changes[min(wi,len(changes)-1)] if changes else (camera[0],camera[0])
            for i,index in enumerate(window['indices']):
                progress=i/(len(window['indices'])-1)
                pose={key:round(start.get(key,0)+(end.get(key,0)-start.get(key,0))*progress,3) for key in ('distance_m','elevation_deg','azimuth_deg','yaw_deg','pitch_deg','lateral_m')}
                pose['subject_size_relative_to_first']=round(camera[0]['distance_m']/max(.001,pose['distance_m']),3)
                physical[index]=pose
        special=''
        if entry['id'].startswith('burger_cut'):
            special='The subject is a BURGER CUT INTO TWO HALVES with its CUT CROSS-SECTION facing the camera from the FIRST frame. Show exposed layers of bun, patty, lettuce and cheese. Never start with a whole burger or replace the cross-section with a bite mark.'
        if 'over_shoulder_hands' in entry['id']:
            special+=' End with a closer view of the SAME scissors/tool and SAME hands working on the SAME hair. The tool must remain visible in the LAST cell. Do not show the finished haircut or remove the hands.'
        if entry['id']=='bag_handoff_low_hold':
            special+=' Camera remains LOW and fixed. The staff member lowers the SAME tray toward the customer lens. The LAST frame is still the LOW view of the tray at the window, never a top-down view. Exactly two staff hands; no customer hands.'
        if single:
            output='ONE single 9:16 portrait illustration. Do NOT make a storyboard, atlas or multiple panels. This camera holds still, so this single pose will be held by the player.'
            progression='Choose the specified starting pose/framing. Do not invent a push-in or a viewpoint change.'
        else:
            output='Exactly SIX portrait camera-view keyframes in TWO columns and THREE rows. Each cell is 9:16, tall and narrow. Entire atlas approximately 768 x 2048. Equal cell size, uniform grid, clear transparent gutters. Read across rows. Do NOT use square cells.'
            progression='Six required camera states, numbered only in this prompt (no labels in artwork):\n'+'\n'.join(f'Frame {i+1}: {json.dumps(physical[i],separators=(",",":"))}' for i in range(6))
        movement=[]
        for action in actions:
            kind=action.get('action');direction=action.get('direction','')
            if kind=='orbit':movement.append(f'True {direction} orbit: stationary subject stays centered, upright and equal size while its visible surfaces change. Do not rotate a flat picture.')
            elif kind=='pan':movement.append(f'Camera pans {direction}: the world moves {"LEFT" if direction=="right" else "RIGHT"} through the fixed portrait view. No zoom.')
            elif kind=='truck':movement.append(f'Camera trucks {direction}: foreground and background slide with different parallax. Keep the viewing angle and resource size.')
            elif kind=='tilt':movement.append('Camera tilts DOWN: upper subject travels UP out of view and the lower subject is revealed. Do not turn this into a dolly/zoom.')
            elif kind=='whip':movement.append(f'Finish with a fast whip {direction} OUT of this scene. Outgoing subject streaks {"left" if direction=="right" else "right"} and leaves the last cell mostly transparent. Do not depict the next shot\'s destination.')
            elif kind=='dolly_in':movement.append('Continuous push-in: same subject grows, with its ending detail as shown in the reference. No replacement objects or change in camera elevation.')
            elif kind=='dolly_out':movement.append('Continuous pull-out: start close on the SAME detail, then it shrinks as more of its surroundings are revealed. No replacement objects.')
            else:movement.append(f'Existing action: {json.dumps(action,separators=(",",":"))}')
        if static:movement.append('Camera position, angle, focal length and framing are FIXED throughout. Only the described subject action may change: '+', '.join(subject_actions or ['none; hold the pose'])+'.')
        if entry['id'].endswith('_through'):
            movement.append('The last cell is the SAME subject surface/texture filling the ENTIRE tall portrait view, ready for a push-through transition. No empty band above or below that final texture.')
        entry['references'][2]=str(style.resolve())
        entry['prompt']=f'''Draw a functional live shot guide in the approved watercolor sketch style. Camera geometry and movement are the specification, not a decorative story illustration.
Reference 1: existing guide's six camera-view keyframes. Match its START crop, END crop, subject placement, and motion direction. Its background is only for legibility.
Reference 2: same guide's 3D strip; use its camera elevation and perspective.
Reference 3: a SINGLE approved watercolor pose, STYLE ONLY. Copy the loose pencil contours, pale slate-blue pigment, textured translucent wash extending outside the lines. Do not copy its subject or layout.

GUIDE {entry['id']}
THIS TAKE ONLY: {take}
ANGLE: {angle_instruction(elevation,description)}
{special}
MOVEMENT: {' '.join(movement)}
{progression}

OUTPUT: {output}
All poses show ONE continuous take, the SAME subject and coherent spatial layout. No cut to another angle, no next shot, no new scene, no finished-result insert. Framing should change ONLY as specified above. Draw THROUGH the phone lens, with no filming operator or filming phone in the view.
One pale slate-blue watercolor pigment only; no color accents or darkening. Opacity will be reduced programmatically AFTER all frame generation, so preserve normal generated alpha now. Truly transparent background with irregular watercolor edges; no solid panel rectangle, checkerboard drawing or page background.
NO drawn mouths, lips, teeth or smile lines. Minimal schematic faces and schematic makeup. MAXIMUM TWO visible hands per frame, including background and partial hands; hide all other hands. No detached limbs or extra fingers.
The camera stays in ordinary visitor-accessible space, never behind a staff counter/till, inside a staff kitchen or at a restricted prep bench. View staff from the customer side or through a public viewing window. An own-hands top-down task may be at the visitor's own table.
No labels, text, prices, numbers, arrows, frame borders, viewfinder UI or watermark in the generated artwork.'''
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Refined pending specifications: own take only, explicit poses, static holds and mandatory subject details.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['plan','accept','refine'])
    parser.add_argument('id',nargs='?');parser.add_argument('source',nargs='?')
    args=parser.parse_args()
    if args.action=='plan':build_plan()
    elif args.action=='refine':refine()
    else:accept(args.id,args.source)
