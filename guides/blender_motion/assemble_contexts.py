"""Assemble each actual script handover from reviewed native shot frames.

All scene art is reused. There is no frame generation, interpolation drift or extra opacity pass.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib
import json
import subprocess
import sys
BASE=Path(__file__).resolve().parents[2];NATIVE=BASE/'catalog/blender-animations';OUT=BASE/'catalog/context-animations'
FPS=15;SIZE=(540,960)
LANDING_FRAMES=9


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def source(gid,step_key=None):
    variants=OUT/'variant-sources.json'
    mapping=json.loads(variants.read_text()) if variants.exists() else {}
    folder=BASE/mapping[step_key] if step_key in mapping else NATIVE/gid
    frame_sources=OUT/'frame-sources.json'
    slices=json.loads(frame_sources.read_text()) if frame_sources.exists() else {}
    subset=slices.get(step_key)
    if subset:folder=BASE/subset['source_folder'] if subset.get('source_folder') else NATIVE/subset['source_guide_id']
    if gid=='bar_low_truckr_mm' and not (folder/'scene-spec.json').exists():
        folder=BASE/'catalog/blender-study'/gid;end=60
        review=json.loads((folder/'publication-review.json').read_text());assert review['guide_sha256']==digest(folder/'guide.png')
    else:
        spec=json.loads((folder/'scene-spec.json').read_text());review=json.loads((folder/'review.json').read_text())
        assert review['guide_sha256']==digest(folder/'guide.png'),gid
        end=round(spec['take_end']*FPS)
    start=1
    if subset:start=subset['start_frame'];end=subset['end_frame']
    files=sorted((folder/'ghost_frames').glob('frame_*.png'))[start-1:end]
    assert len(files)==end-start+1,(gid,len(files),start,end)
    return files,dict(guide_id=gid,source=str(folder.relative_to(BASE)),source_sha256=digest(folder/'guide.png'),frames=len(files),
                      source_guide_id=subset['source_guide_id'] if subset else gid,source_start_frame=start)


def connected_landing(gid,next_gid,step_key=None,next_step_key=None):
    """Prefer a reviewed continuous in-scene handover over appending another scene."""
    variants=OUT/'variant-sources.json';mapping=json.loads(variants.read_text()) if variants.exists() else {}
    folder=BASE/mapping[step_key] if step_key in mapping else NATIVE/gid;path=folder/'scene-spec.json'
    if not path.exists():return None
    spec=json.loads(path.read_text());connection=spec.get('continuous_handover') or spec.get('shared_scene_handover',{})
    if connection.get('next_guide')!=next_gid:return None
    review=json.loads((folder/'review.json').read_text())
    assert review['guide_sha256']==digest(folder/'guide.png')
    start=round(spec['take_end']*FPS)
    files=sorted((folder/'ghost_frames').glob('frame_*.png'))[start:spec['frame_count']]
    assert len(files)==spec['frame_count']-start
    # Stop after the transition has reached the next shot's actual starting pose.
    # Keep the connecting camera travel, but don't replay that next shot in full.
    _,next_origin=source(next_gid,next_step_key)
    if next_origin['source']==str(folder.relative_to(BASE)):
        landing_index=next_origin['source_start_frame']-1
        files=files[:max(LANDING_FRAMES,landing_index-start+LANDING_FRAMES)]
    origin=dict(guide_id=next_gid,source_guide_id=gid,source=str(folder.relative_to(BASE)),
                source_sha256=digest(folder/'guide.png'),source_start_frame=start+1,frames=len(files))
    return files,origin,connection


def coverage(path):return sum(Image.open(path).getchannel('A').point(lambda v:255 if v>20 else 0).histogram()[255:])


def whip_overlap(primary):
    """Trailing frames of the outgoing whip-out, which the landing plays over instead of after."""
    full=max(coverage(p) for p in primary[:-LANDING_FRAMES] or primary);tail=0
    for path in reversed(primary[-LANDING_FRAMES:]):
        if coverage(path)>.9*full:break
        tail+=1
    return max(4,tail)


def whip_landing(files,folder,outgoing=()):
    """A brief incoming right-whip landing, sliding in while the outgoing frames slide out; all scene artwork remains native."""
    destination=folder/'transition-frames';destination.mkdir(parents=True,exist_ok=True)
    result=[]
    for i,path in enumerate(files[:LANDING_FRAMES]):
        image=Image.open(path).convert('RGBA');u=min(1,i/5)
        offset=round(SIZE[0]*.75*(1-u)**2)
        frame=Image.new('RGBA',SIZE)
        if i<len(outgoing):frame.paste(Image.open(outgoing[i]).convert('RGBA'),(-round(SIZE[0]*(1-(1-u)**2)),0))
        layer=Image.new('RGBA',SIZE);layer.paste(image,(offset,0))
        frame=Image.alpha_composite(frame,layer)
        frame.putalpha(frame.getchannel('A').point(lambda v:min(v,128)))
        target=destination/('landing_%02d.png'%i);frame.save(target);result.append(target)
    return result


def encode(folder,files,stages,video=False):
    folder.mkdir(parents=True,exist_ok=True)
    # Identical hold frames share one decoded image while durations remain exact.
    cache={};frames=[]
    for path in files:
        key=digest(path)
        if key not in cache:cache[key]=Image.open(path).convert('RGBA')
        frames.append(cache[key])
    assert all(frame.size==SIZE for frame in frames)
    durations=[round((i+1)*1000/FPS)-round(i*1000/FPS) for i in range(len(frames))]
    frames[0].save(folder/'guide.png',save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=0,blend=0)
    poster=next((f for f in frames[:7] if f.getchannel('A').getextrema()[1]>32),frames[0]);poster.save(folder/'poster.png')
    backing=Image.new('RGBA',SIZE,'#f7f5ef')
    selected=sorted(set([0,len(frames)//5,2*len(frames)//5,3*len(frames)//5,4*len(frames)//5,len(frames)-1]))
    sheet=Image.new('RGB',(270*len(selected),510),'#f7f5ef');draw=ImageDraw.Draw(sheet)
    for i,n in enumerate(selected):
        sheet.paste(Image.alpha_composite(backing,frames[n]).convert('RGB').resize((270,480),Image.Resampling.LANCZOS),(270*i,30))
        draw.text((270*i+8,8),f'{n/FPS:.2f} s',fill='#496475')
    sheet.save(folder/'strip.jpg',quality=94)
    if video:
        writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','15','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(folder/'preview.mp4')],stdin=subprocess.PIPE)
        for frame in frames:writer.stdin.write(Image.alpha_composite(backing,frame).convert('RGB').tobytes())
        writer.stdin.close();assert writer.wait()==0
    check=Image.open(folder/'guide.png');ms=0;maximum=0
    for i in range(check.n_frames):
        check.seek(i);ms+=check.info['duration'];maximum=max(maximum,check.convert('RGBA').getchannel('A').getextrema()[1])
    assert abs(ms-sum(durations))<1 and maximum<=128
    record=dict(frames=len(frames),fps=FPS,duration_ms=ms,sha256=digest(folder/'guide.png'),alpha_applied_again=False,max_alpha=maximum,main_fill_alpha=.25,stages=stages,status='assembled_from_reviewed_shots')
    (folder/'assembly-checks.json').write_text(json.dumps(record,indent=2)+'\n');return record


def main():
    templates=json.loads((BASE/'guides/script_templates.json').read_text())['templates'];OUT.mkdir(exist_ok=True)
    selected=sys.argv[1:];templates=[t for t in templates if not selected or t['id'] in selected]
    manifest_path=OUT/'index.json';manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else dict(steps={},scripts={},guides={})
    policy=BASE/'guides/blender_motion/people-policy.json'
    deferred=set(json.loads(policy.read_text())['deferred_guides']) if policy.exists() else set()
    plans=json.loads((BASE/'scripts/shot_plan.json').read_text())
    for template in templates:
        sequence=[];stages=[];deferred_steps=[]
        for index,step in enumerate(template['steps']):
            key=template['id']+'.'+step['id'];gid=step['overlays'][0]
            if gid in deferred:
                deferred_steps.append(step['id']);manifest['steps'][key]=dict(template_id=template['id'],step_id=step['id'],guide_id=gid,status='deferred_people');continue
            primary,provenance=source(gid,key);files=list(primary)
            stage=dict(step_id=step['id'],guide_id=gid,start_frame=len(sequence)+1,frames=len(primary),source=provenance)
            stages.append(stage);sequence.extend(primary)
            handover=[]
            cut_to_next=False
            next_is_people=index+1<len(template['steps']) and template['steps'][index+1]['overlays'][0] in deferred
            if index+1<len(template['steps']) and not next_is_people:
                nxt=template['steps'][index+1];next_key=template['id']+'.'+nxt['id'];next_gid=nxt['overlays'][0]
                connected=connected_landing(gid,next_gid,key,next_key)
                if connected:
                    landing,origin,connection=connected
                else:
                    transition=plans.get(template['id'],{}).get(step['id'],{}).get('transitionOut','cut')
                    if 'whip' in transition:
                        landing,origin=source(next_gid,next_key)
                        overlap=whip_overlap(primary);outgoing=files[-overlap:];del files[-overlap:]
                        landing=whip_landing(landing,OUT/'steps'/key,outgoing)
                        origin.update(frames=len(landing),transformation='brief incoming right-whip landing; no full next-shot replay')
                        connection=dict(method='brief_right_whip',landing_seconds=len(landing)/FPS)
                    else:
                        # A cut is the boundary between takes. Appending another
                        # complete animation made every step appear mis-sliced.
                        landing=[];cut_to_next=True
                if landing:
                    files.extend(landing)
                    handover=[dict(next_step=nxt['id'],next_guide=next_gid,start_frame=len(files)-len(landing)+1,frames=len(landing),source=origin,connection=connection)]
            folder=OUT/'steps'/key
            record=encode(folder,files,[dict(step=step['id'],frames=len(primary),source=provenance),*handover])
            row=dict(template_id=template['id'],step_id=step['id'],guide_id=gid,folder=str(folder.relative_to(BASE)),duration=record['duration_ms']/1000,sha256=record['sha256'],scope='shot_and_handover' if handover else 'base_shot' if next_is_people else 'complete_final_shot',handover_status='included' if handover else 'deferred_people' if next_is_people else 'not_applicable',next_guide=handover[0]['next_guide'] if handover else template['steps'][index+1]['overlays'][0] if next_is_people else None,source=provenance)
            if cut_to_next:row.update(scope='base_shot',handover_status='cut_to_next_step',next_guide=next_gid,transition_method='cut_at_step_boundary')
            if handover and handover[0].get('connection'):row['transition_method']=handover[0]['connection']['method']
            manifest['steps'][key]=row
            previous=manifest['guides'].get(gid)
            if previous is None or (previous['template_id']==template['id'] and previous['step_id']==step['id']):manifest['guides'][gid]=row
        if deferred_steps:
            manifest['scripts'][template['id']]=dict(id=template['id'],title=template['title'],status='deferred_people',deferred_steps=deferred_steps,object_steps=[s['step_id'] for s in stages])
            manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');print('SCRIPT_OBJECT_STEPS_READY',template['id'],len(stages),'people deferred',len(deferred_steps),flush=True);continue
        folder=OUT/'scripts'/template['id'];record=encode(folder,sequence,stages,video=True)
        manifest['scripts'][template['id']]=dict(id=template['id'],title=template['title'],folder=str(folder.relative_to(BASE)),duration=record['duration_ms']/1000,sha256=record['sha256'],steps=stages)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');print('SCRIPT_SEQUENCE_READY',template['id'],len(template['steps']),record['duration_ms']/1000,flush=True)
    print('CONTEXT_TOTALS',len(manifest['steps']),len(manifest['scripts']),len(manifest['guides']))


if __name__=='__main__':main()
