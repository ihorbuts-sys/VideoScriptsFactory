"""Refresh the bar and best-table section of its existing full-script sequence."""
import bisect,copy,hashlib,json,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parents[3];ROOT=BASE/'catalog/clay-scenes'
LIVE=Path('/Users/ihor.buts/Documents/Development/VideoEditorKit/tools/scriptwriter/catalog')
FPS=15;TID='restaurant-room-tour'

def frames(path,count):
    source=Image.open(path);ends=[];images=[];clock=0
    for i in range(source.n_frames):
        source.seek(i);images.append(source.convert('RGBA').copy());clock+=source.info.get('duration',1000/FPS);ends.append(clock)
    return [images[min(bisect.bisect_right(ends,(i+.5)*1000/FPS),len(images)-1)] for i in range(count)]

def run():
    out=ROOT/'sequences'/TID;out.mkdir(parents=True,exist_ok=True)
    baseline=out/'source-index.json'
    if not baseline.exists():
        row=json.loads((LIVE/'catalog.json').read_text())['scriptGuideSequences'][TID]
        assert row['sha256']=='b2cb1527822398c0431ca0214a9882b6a5c455f8e40840dd55712ca0e4f10004'
        baseline.write_text(json.dumps(row,indent=2)+'\n')
    original=json.loads(baseline.read_text());old_steps=original['steps'];bar=next(s for s in old_steps if s['step_id']=='bar');seat=next(s for s in old_steps if s['step_id']=='seat')
    assert bar['start_frame']+bar['frames']==seat['start_frame']
    total=sum(s['frames'] for s in old_steps);old=frames(LIVE/original['overlay'],total)
    new=frames(ROOT/'bar_low_truckr_mm/ghost.png',180)
    start=bar['start_frame']-1;stop=seat['start_frame']-1+seat['frames']
    sequence=old[:start]+new+old[stop:];assert len(sequence)==539
    durations=[round((i+1)*1000/FPS)-round(i*1000/FPS) for i in range(len(sequence))]
    sequence[0].save(out/'ghost.png',save_all=True,append_images=sequence[1:],duration=durations,loop=0,disposal=0,blend=0)
    sequence[0].save(out/'poster.png')
    writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r','15','-i','-','-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'preview.mp4')],stdin=subprocess.PIPE)
    for im in sequence:
        bg=Image.new('RGBA',im.size,'#f7f2e7');bg.alpha_composite(im);writer.stdin.write(bg.convert('RGB').tobytes())
    writer.stdin.close();assert writer.wait()==0
    selected=[1,start+1,start+61,start+126,start+180,len(sequence)];sheet=Image.new('RGB',(1620,510),'#f7f2e7');draw=ImageDraw.Draw(sheet)
    for i,n in enumerate(selected):
        bg=Image.new('RGBA',sequence[n-1].size,'#f7f2e7');bg.alpha_composite(sequence[n-1]);sheet.paste(bg.convert('RGB').resize((270,480)),(i*270,30));draw.text((i*270+10,8),f'{(n-1)/15:.2f} s',fill='#334b3c')
    sheet.save(out/'strip.jpg',quality=93)
    steps=copy.deepcopy(old_steps);cursor=1;sha=hashlib.sha256((ROOT/'bar_low_truckr_mm/ghost.png').read_bytes()).hexdigest()
    for step in steps:
        if step['step_id'] in ['bar','seat']:
            first=1 if step['step_id']=='bar' else 126;count=125 if step['step_id']=='bar' else 55
            step['frames']=count;step['source']=dict(guide_id=step['guide_id'],source='catalog/clay-scenes/bar_low_truckr_mm',source_sha256=sha,frames=count,source_start_frame=first,source_guide_id='bar_low_truckr_mm',alpha_already_applied=True)
        step['start_frame']=cursor;cursor+=step['frames']
    encoded=Image.open(out/'ghost.png');duration=0;maximum=0
    for i in range(encoded.n_frames):
        encoded.seek(i);duration+=encoded.info.get('duration',0);maximum=max(maximum,encoded.convert('RGBA').getchannel('A').getextrema()[1])
    assert abs(duration-sum(durations))<1 and maximum<=166
    assert all(np.array_equal(np.asarray(sequence[start+i]),np.asarray(new[i])) for i in [0,60,125,179])
    report=dict(status='passed',source_frames=len(sequence),encoded_apng_frames=encoded.n_frames,duration_ms=duration,max_alpha=maximum,
        alpha_applied_again=False,unchanged_surrounding_source_frames=total-(stop-start),replaced_steps=['bar','seat'],shared_new_scene_frames=180,
        limitations=['Other script sections retain their existing artwork, including its human guides'])
    (out/'assembly-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    row=dict(reviewed=True,folder=str(out.relative_to(BASE)),title=original['title'],seconds=round(duration/1000,3),steps=steps,
        files={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['ghost.png','preview.mp4','poster.png','strip.jpg']})
    manifest=ROOT/'active-revisions.json';data=json.loads(manifest.read_text());data.setdefault('sequences',{})[TID]=row;manifest.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__':run()
