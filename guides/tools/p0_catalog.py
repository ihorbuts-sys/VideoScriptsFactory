"""P0 authoring registry, derived from the executable animation brief."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BRIEF=ROOT/'briefs/p0_animations.md'
PROMOTED=ROOT/'guides/p0/promoted.json'
TYPES=[
 ('entrance','Entrance','motion','center','back','noise'),
 ('menu-board','Menu board','motion','thirds','back','noise'),
 ('menu-card','Menu card','still','thirds','back','noise'),
 ('counter-order','Order at the counter','still','thirds','back','content'),
 ('plate-reveal','Plate reveal','motion','triangle','back','content'),
 ('hand-off','Hand-off','still','center','back','content'),
 ('pour','Pour','still','center','back','content'),
 ('steam','Steam','still','thirds','back','content'),
 ('first-bite','First bite','still','center','front','content'),
 ('sip','First sip','still','center','front','content'),
 ('room-from-table','Room from the table','motion','thirds','back','noise'),
 ('verdict','Verdict','still','center','front','content'),
]
LENS_LOCKED={'menu-card','plate-reveal','pour','steam'}
PROPS={'plate_tissue_slide','pour_upside_down'}
DEFERRED={}
PEOPLE={
 'bite_selfie_eye':("First bite, front camera", "Hold the front camera at eye height. Keep your face clear as you raise a small forkful beside your mouth, pause before the bite, then lower it. Look at the lens."),
 'sip_selfie_eye':("First sip, front camera", "Hold the front camera at eye height. Lift the cup to your lower lip, pause briefly with the rim covering the mouth, then lower it and look into the lens."),
 'sip_high_lean':("First sip, camera slightly above", "Keep the front camera slightly above your eyes, tilted gently down. Raise the cup without hiding your eyes, pause at the lips, then lower it."),
 'verdict_eye_level':("Your verdict, front camera at eye height", "Keep the front lens at eye height and look into it. Leave room around your hair and shoulders. Give one small gesture while holding the phone steady."),
 'verdict_high_plate':("Your verdict with the dish", "Hold the front camera a little above eye height and angle it down. Keep your eyes clear and the supported dish beside you in the lower part of the frame."),
}
REVISED={
 'entrance_sign_tilt':('motion','close downward sign-to-door move','Stay close on the public side. Start on the sign, then lower the phone about 45 cm and tilt smoothly down to the door without pulling back.'),
 'menu_card_top':('motion','short sideways slide into an overhead view','Keep the menu flat. Slide the phone sideways about 12 cm, gently settling into an overhead view.'),
 'menu_card_push':('motion','short curved high-angle approach','Move closer to one menu line along a small diagonal curve; keep the card flat on the table.'),
 'counter_over_shoulder':('motion','left-to-right slide with a gentle push-in','From the customer side, slide the phone about 40 cm left to right while leaning slightly closer, keeping the menu board above the cup.'),
 'plate_tissue_slide':('countdown','napkin-assisted lateral phone slide','Rest the phone bottom edge on a napkin and slide it left to right across the near table edge. Keep the lens facing the dish; do not slide into it.'),
 'steam_low_backlit':('motion','cup-height lateral slider move','With the window behind the steam, slide the phone sideways about 14 cm at cup height, keeping the cup on its saucer.'),
 'steam_push_in_high':('motion','high-angle diagonal approach to steam','Move the phone closer and slightly sideways to reveal the steam and the cup beside its pastry.'),
 'bite_pip_dish':('still','tight fork lift with hanging pasta and a cropped grip','Keep the phone close to the plate as a fork lifts pasta. Frame only the small grip at the edge; keep the full hand, arm and face outside the shot.'),
 'handoff_counter_cup':('motion','customer-side counter-corner reveal','Keep the served cup on its saucer near the counter corner. Slide the phone slightly sideways, keeping the counter lip and cabinet visible below it.'),
 'handoff_plate_lands':('motion','object-only diagonal plate reveal after service','After the plate is set down, keep it at your place setting. Move the phone slightly sideways and up, keeping the rim, glass and cutlery visible.'),
 'pour_side_low':('still','three-quarter rim-height pour','Hold the phone at cup-rim height from a three-quarter side angle. Keep the spout and vertical stream visible as the kettle tilts.'),
 'pour_upside_down':('countdown','inverted-phone counter-level lateral pour','Invert the phone so its lens sits just above the counter. Slide it sideways about 18 cm while looking slightly up at the cup and spout.'),
 'room_seated_pan':('motion','seated left pan that includes the whole cup','Pan slowly left from your seat, finishing with the cup body and handle in the foreground and the tables beyond.'),
}


def preset(trigger,shot_type):
    moving=trigger=='motion'
    return dict(stabilization='cinematicExtendedEnhanced' if moving else 'standard',
        continuousFocus=moving,locksFocusExposureWhiteBalance=not moving,lensLocked=shot_type in LENS_LOCKED,frameRate=30)


METRIC=re.compile(r'(\d+(?:\.\d+)?)(?:-(\d+(?:\.\d+)?))?\s?(cm|m)\b')


def us_units(text):
    """Creator-facing guide text in US units (owner 2026-11-13: no metric anywhere the app shows)."""
    def one(value,unit):
        cm=float(value)*(100 if unit=='m' else 1)
        if 28<=cm<=33:return 'a foot'
        if cm<75:return f'{round(cm/2.54)} inches'
        return f'{round(cm/30.48)} feet'
    def sub(m):
        if m.group(2):
            a,b=one(m.group(1),m.group(3)),one(m.group(2),m.group(3))
            return f"{a.split()[0]}-{b}" if a.split()[1:]==b.split()[1:] else f'{a} to {b}'
        return one(m.group(1),m.group(3))
    return METRIC.sub(sub,text) if text else text


def registry():
    text=BRIEF.read_text();guides=[]
    setups={m.group(1):m.group(2).strip() for m in re.finditer(r'#### \d+ `([^`]+)`[^\n]*\n(.*?)(?=\n#### |\n## 4\.|\Z)',text,re.S)}
    for line in text.splitlines():
        if not re.match(r'\| \d+ \| `',line):continue
        columns=[c.strip().replace('`','') for c in line.strip('|').split('|')]
        if len(columns)!=9:continue
        number,gid,title,kind,technique,seconds,trigger,source,new=columns
        section=setups[gid]
        invariant=re.search(r'\*\*Filming guideline\*\*[^\"]*\"([^\"]+)\"',section)
        assert invariant,gid
        capture=preset(trigger,kind)
        if gid=='plate_tissue_slide':capture.update(stabilization='cinematicExtendedEnhanced',continuousFocus=False,locksFocusExposureWhiteBalance=True)
        guides.append(dict(id=gid,title=title,shotType=kind,technique=technique,durationSec=int(seconds),
            startTrigger=trigger,capturePreset=capture,setupBeatSeconds=1 if gid in PROPS else 0,
            invariant=invariant.group(1).replace('\n  ',' '),sourceScene=source,newObjects=new,
            composition=next(t[3] for t in TYPES if t[0]==kind),camera='both' if gid=='bite_pip_dish' else next(t[4] for t in TYPES if t[0]==kind),
            sourceSetup=section,alphaFactor=1,fps=15,resolution=[405,720],selectorResolution=[120,213],
            targetHoldFrames=8,finalHoldFrames=7,sourceBriefSHA256=hashlib.sha256(text.encode()).hexdigest()))
        if gid=='plate_tissue_slide':
            guides[-1]['sourceInvariant']=guides[-1]['invariant']
            guides[-1]['invariant']="Rest the phone's bottom edge on a napkin, lens toward the plate, and slide it straight in."
        if gid in REVISED:
            trigger,technique,invariant=REVISED[gid]
            guides[-1].update(sourceInvariant=guides[-1]['invariant'],startTrigger=trigger,
                technique=technique,invariant=invariant,capturePreset=preset(trigger,kind))
        if gid in DEFERRED:guides[-1].update(availability='deferred',deferredReason=DEFERRED[gid])
        else:guides[-1]['availability']='active'
        if gid in PEOPLE:
            title,invariant=PEOPLE[gid]
            guides[-1].update(title=title,invariant=invariant,sourceInvariant=guides[-1]['invariant'],
                allowedHands=2,allowedPeople=1,content='canonical-character',camera='front',
                previewMirrored=True,filmingMode='selfie',facialAnimation=False,
                sourceSetup=invariant,technique='steady front-camera framing with a natural subject action')
        if gid=='handoff_counter_cup':guides[-1]['title']='Your cup at the counter'
        if gid=='handoff_plate_lands':guides[-1]['title']='Plate at your place'
        if gid=='bite_pip_dish':guides[-1].update(title='First forkful, close up',allowedHands=1,camera='back')
    assert len({g['id'] for g in guides})==len(guides)
    additions=[
        ('room_reveal_plant','Through the leaves into the room','room-from-table','room_reveal_cup',6,'Film through a floor plant from the clear aisle. Slide the phone about 40 cm right to reveal the tables beyond; keep clear of the leaves.'),
        ('counter_through_cup_handle','Through the cup handle to the counter','counter-order','counter_edge_to_pass',6,'Keep the cup still. Place the phone outside the counter edge and frame the barista through the handle. Tap focus beyond the handle, then drift slightly sideways.'),
        ('steam_slide_pull_out','Slide past the cup and pull back','steam','steam_push_in_high',6,'Start close to the cup on its saucer. Slide sideways about 30 cm while pulling back to reveal the pastry and window-side table.'),
        ('table_spread_orbit','Rise over the shared table spread','plate-reveal','plate_high_orbit',8,'Start at a high three-quarter angle, then raise the phone into an overhead view of the pizza, salad, bread and drinks. Keep the whole spread in frame at the end.'),
        ('glass_slide_close','Slide a cocktail into the close-up','plate-reveal','plate_high_orbit',6,'Keep the glass base on the table. Slide the drink gently into the foreground with one hand while filming close with the other.'),
        ('pancake_clear_path','Clear the foreground to reveal pancakes','plate-reveal','plate_high_orbit',8,'Have a right-side hand pull each drink right and a left-side hand pull the salad left, one by one. Film toward the pancakes at their height; hands stay on their own side.'),
    ]
    for gid,title,kind,base,seconds,invariant in additions:
        original=next(g for g in guides if g['id']==base)
        row=dict(original,id=gid,title=title,shotType=kind,durationSec=seconds,startTrigger='motion',setupBeatSeconds=0,
                 capturePreset=preset('motion',kind),invariant=invariant,sourceInvariant=invariant,sourceScene=base,
                 sourceSetup=invariant,technique=title,newObjects='Existing reusable plant, cup, room and counter assets',
                 composition=next(t[3] for t in TYPES if t[0]==kind),camera='back',availability='active')
        if gid=='counter_through_cup_handle':
            row['allowedSilhouettes']=1;row['capturePreset'].update(continuousFocus=False,locksFocusExposureWhiteBalance=True)
        if gid in ['glass_slide_close','pancake_clear_path']:
            row['allowedHands']=1 if gid=='glass_slide_close' else 2;row['composition']='center'
        if gid in ['table_spread_orbit','glass_slide_close','pancake_clear_path']:
            row['reusableSteps']=['food-review.dish','first-visit.plate'];row['sourceSetup']='Owner tabletop/GIF reference: '+invariant
        guides.append(row)
    for gid,base,title,invariant in [
        ('bite_friend_three_quarter','bite_selfie_eye','First bite, filmed by a friend',
         'Ask a friend to film from about one metre away at eye height, slightly to your side. Raise the forkful beside your mouth. Keep the phone movement small and your face and fork in frame.'),
        ('sip_friend_side','sip_selfie_eye','First sip, friend at a three-quarter angle',
         'Ask a friend to film at eye height from a three-quarter side angle, about one metre away. Lift the cup with your eyes visible above the rim. The friend makes a small, smooth sideways approach.'),
        ('verdict_friend_eye','verdict_eye_level','Your verdict, filmed by a friend',
         'Ask a friend to hold the rear camera at your eye height, about one metre away and slightly to your side. Face the lens and give a small natural gesture. Keep the room faint behind you.'),
    ]:
        original=next(g for g in guides if g['id']==base)
        guides.append(dict(original,id=gid,title=title,invariant=invariant,sourceSetup=invariant,
            camera='back',previewMirrored=False,filmingMode='friend',
            startTrigger='motion',capturePreset=preset('motion',original['shotType']),
            technique='eye-height three-quarter camera with a small curved approach'))
    promote(guides)
    assert len({g['id'] for g in guides})==len(guides)
    types=[]
    for kind,title,trigger,composition,camera,ambient in TYPES:
        rows=[g for g in guides if g['shotType']==kind and g['availability']!='archived']
        types.append(dict(id=kind,title=title,startTrigger=trigger,capturePreset=preset(trigger,kind),
            composition=composition,camera=camera,ambientDefault=ambient,guides=[g['id'] for g in rows],
            durationSec=dict(min=min(g['durationSec'] for g in rows),max=max(g['durationSec'] for g in rows))))
    for g in guides:
        g['invariant']=us_units(g['invariant']);g['title']=us_units(g['title'])
    return dict(profile='p0',version=1,shotTypes=types,guides=guides,
        source=str(BRIEF.relative_to(ROOT.parent)),sourceSHA256=hashlib.sha256(text.encode()).hexdigest(),deferredGuides=DEFERRED,
        clock='8 target frames; optional 15 setup frames; durationSec*15 demonstration frames; 7 final target frames',
        decisions=['8/7-frame holds approximate half a second at 15 fps and total exactly one second.',
                   'Target hero must fit the intersection of the kit band and editor protection: top 28%, bottom 35%.',
                   'When numeric width/position examples conflict with the band, safe framing wins and the adjustment is recorded.',
                   'Owner restored five person guides and requested front-camera and friend-filmed options. Use the existing canonical creator rig; no new character generation.',
                   'P0 alphaFactor is 1; runtime applies 65% before capture and 30% while recording.'])


def promote(guides):
    """Owner-approved drafts join next to the guide they follow; the guides they replace stay, archived."""
    if not PROMOTED.exists():return
    data=json.loads(PROMOTED.read_text())
    for gid,row in data['archived'].items():
        guide=next(g for g in guides if g['id']==gid)
        guide.update(availability='archived',replacedBy=row['replacedBy'],archivedOn=row['archivedOn'])
    for gid,row in data['guides'].items():
        record=dict(row['record'],availability='active');assert record['id']==gid
        ids=[g['id'] for g in guides]
        # An approved re-render of an id already in the registry replaces its record in place.
        if gid in ids:guides[ids.index(gid)]=record;continue
        guides.insert(ids.index(row['after'])+1 if row.get('after') else len(guides),record)


def write():
    data=registry();out=ROOT/'guides/p0';out.mkdir(exist_ok=True)
    (out/'plan.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(shot_types=len(data['shotTypes']),guides=len(data['guides']),plan=str(out/'plan.json'))))


if __name__=='__main__':write()
