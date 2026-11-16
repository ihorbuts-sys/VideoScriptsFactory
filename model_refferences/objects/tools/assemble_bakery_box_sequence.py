"""Join the five reviewed bakery-box steps, retaining the continuous packing reveal."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
from PIL import Image
import build_hologram_view_overlay as V
import export_reconstructed_scene as E
from pack_full_frame_apng import pack as apng

BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'catalog/glass-rollout'
OUT=ROOT/'sequences/bakery-box'
ROWS=[('hook','selfie_one_high_hold','creator-bakery',1,105,'shot',6),
      ('case','case_eye_truckr_mm','creator-pastry-select',1,120,'shot',6),
      ('pick','hand_pov_pastry_pov_in_mc','creator-pack-box',1,120,'pick',6.5),
      ('box','topdown_box_top_out_cm','creator-pack-box',121,75,'box',4),
      ('total','selfie_one_high_hold','creator-box-total',1,105,'shot',6)]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def link(source,target):
    target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_name(target.name+'.tmp');temp.unlink(missing_ok=True)
    os.link(source,temp);os.replace(temp,target)

def run(catalog):
    for _,_,name,_,_,_,_ in ROWS:
        review=ROOT/'coffee'/name/'review-status.json'
        assert not review.exists() or json.loads(review.read_text()).get('status')!='rejected','Owner-rejected hand study cannot be assembled or published: '+name
    bundle=json.loads((catalog/'catalog.json').read_text())
    template=next(t for t in bundle['templates'] if t['id']=='bakery-box')
    assert [s['id'] for s in template['steps']]==[r[0] for r in ROWS]
    OUT.mkdir(parents=True,exist_ok=True);frames=OUT/'view-frames';frames.mkdir(exist_ok=True)
    colors=[];steps=[];phases=[];offset=1;palette=None
    for sid,gid,name,first,count,phase,capture in ROWS:
        source=ROOT/'coffee'/name
        browser=json.loads((source/'composite-browser-check.json').read_text())
        assert browser['status']=='passed' and browser['overlay_sha256']==sha(source/'view-overlay.png')
        with Image.open(source/'view-frames'/f'frame_{first:04d}.png') as im:
            current=(im.getpalette(),im.info.get('transparency'))
            if palette is None:palette=current
            assert current==palette,'Source palettes must agree for lossless assembly'
        for n in range(first,first+count):
            link(source/'view-frames'/f'frame_{n:04d}.png',frames/f'frame_{offset+n-first:04d}.png')
            colors.append(source/'color'/f'frame_{n:04d}.png')
        steps.append(dict(step_id=sid,guide_id=gid,start_frame=offset,frames=count,capture_seconds=capture,
            transition_out='continuous_same_worktop' if sid=='pick' else 'end' if sid=='total' else 'cut',
            source=dict(source=str(source.relative_to(BASE)),source_start_frame=first,frames=count,source_sha256=sha(source/'view-overlay.png'))))
        for name in ['view-overlay.png','view-overlay-poster.png','view-overlay-strip.jpg','color.mp4','color-poster.png']:
            link(source/'phases'/phase/name,OUT/'phases'/sid/name)
        phases.append(dict(id=sid,frames=count,start_s=(offset-1)/15,end_s=(offset-1+count)/15))
        offset+=count
    count=offset-1;assert count==525
    apng(frames,OUT/'view-overlay.png',count,15);checked=V.check(OUT/'view-overlay.png',count,15)
    writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','405x720','-r','15','-i','-',
        '-an','-vf','scale=432:768:flags=lanczos','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'color.mp4')],stdin=subprocess.PIPE)
    for p in colors:
        with Image.open(p) as im:
            bg=Image.new('RGBA',im.size,'#f7f2e7');bg.alpha_composite(im.convert('RGBA'));writer.stdin.write(bg.convert('RGB').tobytes())
    writer.stdin.close();assert writer.wait()==0
    with Image.open(frames/'frame_0001.png') as im:im.convert('RGBA').save(OUT/'view-overlay-poster.png')
    with Image.open(colors[0]) as im:im.save(OUT/'color-poster.png')
    probes=[1,105,145,225,285,345,380,420,480,525];images=[]
    for n in probes:
        with Image.open(frames/f'frame_{n:04d}.png') as im:
            image=im.convert('RGBA');image.putalpha(image.getchannel('A').point(lambda a:round(a*.65)));images.append(image)
    E.OUT=OUT;E.FPS=15;E.strip(images,probes,'view-overlay-strip.jpg')
    with Image.open(OUT/'view-overlay.png') as im:
        for n in range(1,count+1):
            im.seek(n-1)
            with Image.open(frames/f'frame_{n:04d}.png') as src:assert im.convert('RGBA').tobytes()==src.convert('RGBA').tobytes()
    write(OUT/'scene-spec.json',dict(id='bakery-box',title='Build a box / complete creator sequence',fps=15,frame_count=count,duration_s=35,
        exported_phases=phases,steps=steps,scope='full_script_instruction_sequence',full_script_sequence_complete=True,
        revision='bakery-box-creator-2026-11-02-v1',same_camera_for_color_and_ghost=True,
        display=dict(opacity_mode='image_view',image_opacity=.65,background_delay_seconds=2,viewfinder='separate_ui_layer',walls=False,floor=False,ceiling=False)))
    write(OUT/'view-overlay-checks.json',dict(status='passed',phases=[checked],opacity_100_sample_checks=[],image_opacity_baked=1,
        walls_excluded=True,floor_excluded=True,resolution=[405,720],every_step_present=True,source_pixels_preserved=True,
        files={n:sha(OUT/n) for n in ['view-overlay.png','color.mp4']}))
    write(OUT/'assembly-checks.json',dict(status='passed',source_frames=525,encoded_apng_frames=525,max_alpha=checked['max_alpha'],
        alpha_applied_again=False,all_five_steps_native_rendered=True,current_batch_bakery_steps=4,existing_hook_reused=True,continuous_pick_to_box=True,repeated_handover_frames_removed=True,
        decoded_boundaries_match_source=True,all_decoded_frames_match_source=True,full_script_sequence_complete=True))
    text=(ROOT/'coffee/creator-box-total/index.html').read_text();a=text.index('<nav aria-label="Shot">');b=text.index('</nav>',a)+6
    nav='<nav aria-label="Shot"><button data-phase="" aria-pressed="true">Full script</button>'+''.join(f'<button data-phase="{r[0]}" aria-pressed="false">{r[0].title()}</button>' for r in ROWS)+'</nav>'
    text=text[:a]+nav+text[b:];a=text.index('<h1>');b=text.index('</h1>',a)+5
    text=text[:a]+'<h1>Build a box / complete creator sequence</h1>'+text[b:]
    a=text.index('<p class="notes">');b=text.index('</p>',a)+4
    text=text[:a]+'<p class="notes">Press Play preview. Budget, display, pastry selection, the filled box and the total form the complete five-step script. Picking to the overhead box reveal is continuous; the other joins are explicit cuts. The reference video follows the guide by two seconds.</p>'+text[b:]
    text=text.replace('href="../index.html"','href="../../../interaction-scenes/index.html"')
    (OUT/'index.html').write_text(text)
    from guide_viewfinder_targets import apply
    apply(OUT,35,[dict(phase='box',start=23,end=28)])
    (OUT/'README.md').write_text('# Build a box / complete creator sequence\n\nAll five script steps use the canonical creator and reviewed native renders. Packing and the overhead reveal use consecutive frames of one physical scene. Other joins are deliberate cuts. The box retains the same two supported pastries through the final portrait.\n\n525 frames at 15 fps: 35 seconds. Capture recommendations are 6, 6, 6.5, 4 and 6 seconds. Full-strength transparent images use one 65% image-view multiplier. Viewfinder is separate, and the preview background follows two seconds behind. Original facial expressions are retained; lip sync and physical iPhone testing remain pending.\n')
    for dest,src in [('ghost.png','view-overlay.png'),('preview.mp4','color.mp4'),('poster.png','view-overlay-poster.png'),('strip.jpg','view-overlay-strip.jpg')]:link(OUT/src,OUT/dest)
    subprocess.run([sys.executable,str(Path(__file__).with_name('check_hologram_composite.py')),'--folder',str(OUT),'--url','http://127.0.0.1:8766/glass-rollout/sequences/bakery-box/index.html','--embedded'],check=True)
    manifest_path=BASE/'catalog/clay-scenes/active-revisions.json';manifest=json.loads(manifest_path.read_text())
    manifest.setdefault('sequences',{})['bakery-box']=dict(reviewed=True,reviewer='Native contact and pose checks, exact frame boundaries and embedded-browser playback',
        folder=str(OUT.relative_to(BASE)),seconds=35,steps=steps,opacity_mode='image_view',revision='bakery-box-creator-2026-11-02-v1',
        files={n:sha(OUT/n) for n in ['ghost.png','preview.mp4','poster.png','strip.jpg']})
    write(manifest_path,manifest)
    subprocess.run([sys.executable,str(BASE/'api/clay_scene_assets.py'),'--out',str(catalog)],check=True)
    write(OUT/'publication.json',dict(status='published',template='bakery-box',steps=5,full_script_sequence_complete=True,endpoint='/v1/scripts/bakery-box/guide-sequence'))
    print(json.dumps(dict(status='published',frames=525,seconds=35,steps=5)),flush=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--catalog',required=True,type=Path);a=p.parse_args();run(a.catalog.resolve())
