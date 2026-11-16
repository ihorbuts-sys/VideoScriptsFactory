"""Export Blender camera shots with the approved contour/fill hierarchy."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib
import importlib.util
import json
import subprocess
import sys
import numpy as np

BASE=Path(__file__).resolve().parents[2]
CATALOG=BASE/"catalog/blender-animations"
reference=BASE/"catalog/blender-study/export_sequence.py"
loader=importlib.util.spec_from_file_location("approved_review_guides",reference)
module=importlib.util.module_from_spec(loader);loader.loader.exec_module(module)
SIZE=(540,960)
INTRO_REVEAL=False
LIGHT_CACHE={}
EVENT_CACHE={}


def compose(out,number,probes=False):
    prefix="probes-" if probes else ""
    name="frame_%04d.png"%number
    contour=Image.open(out/(prefix+"contours")/name).convert("RGBA")
    mask=np.asarray(Image.open(out/(prefix+"fills")/name).convert("RGBA"),dtype=np.uint16)
    alpha=np.rint(mask[:,:,0]*mask[:,:,3]/255).astype(np.uint8)
    assert int(alpha.max())<=130
    fill=Image.new("RGBA",SIZE,(118,155,178,0));fill.putalpha(Image.fromarray(alpha))
    # Warm fixture annotations fade in once for the explicit opening-time event.
    # Geometry, light positions, furniture and source frames remain unchanged.
    key=str(out)
    if key not in EVENT_CACHE:EVENT_CACHE[key]=json.loads((out/'scene-spec.json').read_text()).get('lights_on_events',[])
    events=EVENT_CACHE[key]
    if events:
        data=np.asarray(contour).copy();warm=(data[:,:,0]>data[:,:,2]*1.6)&(data[:,:,3]>0)
        # Lamp locations project left-to-right in this fixed frontal room view.
        t=(number-1)/15
        for index,event in enumerate(events):
            lo,hi=event.get('pixel_x_range',[round(index*SIZE[0]/len(events)),round((index+1)*SIZE[0]/len(events))])
            u=max(0,min(1,(t-event['starts'])/(event['ends']-event['starts'])))
            region=warm[:,lo:hi];alpha=data[:,lo:hi,3]
            alpha[region]=np.rint(alpha[region]*(u*u*(3-2*u))).astype(np.uint8)
        contour=Image.fromarray(data)
    combined=Image.alpha_composite(fill,contour)
    lighting=out/'gliding-light.json'
    if lighting.exists() and not probes:
        key=str(lighting)
        if key not in LIGHT_CACHE:LIGHT_CACHE[key]=json.loads(lighting.read_text())
        cues=LIGHT_CACHE[key]
        if number<=len(cues['frames']) and cues['frames'][number-1]:
            layer=Image.new('RGBA',(SIZE[0]*3,SIZE[1]*3),(0,0,0,0));draw=ImageDraw.Draw(layer)
            for path in cues['frames'][number-1]:draw.line([(x*3,y*3) for x,y in path['points']],fill=tuple(cues['rgba']),width=round(cues['width']*3),joint='curve')
            combined=Image.alpha_composite(combined,layer.resize(SIZE,Image.Resampling.LANCZOS))
    if INTRO_REVEAL and number<=6:
        combined.putalpha(combined.getchannel("A").point(lambda a:round(a*number/6)))
    result=combined.copy();result.putalpha(combined.getchannel("A").point(lambda a:round(a*.5)))
    assert result.convert("RGB").tobytes()==combined.convert("RGB").tobytes()
    assert result.getchannel("A").getextrema()[1]<=128
    return result


def sheet(out,frames,numbers,name):
    image=Image.new("RGB",(270*len(frames),510),"#f7f5ef");draw=ImageDraw.Draw(image)
    backing=Image.new("RGBA",SIZE,"#f7f5ef");ui=module.guides()
    for index,(frame,number) in enumerate(zip(frames,numbers)):
        view=Image.alpha_composite(backing,Image.alpha_composite(frame,ui)).convert("RGB").resize((270,480),Image.Resampling.LANCZOS)
        image.paste(view,(270*index,30));draw.text((270*index+10,8),"%.2f s"%((number-1)/15),fill="#496475")
    image.save(out/name,quality=94)


def run(gid,probes=False):
    global INTRO_REVEAL
    out=CATALOG/gid;spec=json.loads((out/"scene-spec.json").read_text())
    INTRO_REVEAL=spec.get("static_hold",False)
    if probes:
        numbers=[int(p.stem.split("_")[-1]) for p in sorted((out/"probes-contours").glob("frame_*.png"))]
        frames=[compose(out,n,True) for n in numbers]
        sheet(out,frames,numbers,"proof.jpg");print("PROOF",gid,len(frames));return
    numbers=list(range(1,spec["frame_count"]+1));frames=[compose(out,n) for n in numbers]
    folder=out/"ghost_frames";folder.mkdir(exist_ok=True)
    for old in folder.glob("frame_*.png"):old.unlink()
    for number,frame in zip(numbers,frames):frame.save(folder/("frame_%04d.png"%number))
    durations=[round((n+1)*1000/15)-round(n*1000/15) for n in range(len(frames))]
    ui=module.guides();ui.save(out/"viewfinder.png")
    review=[Image.alpha_composite(f,ui) for f in frames]
    for name,sequence in [("guide.png",frames),("guide_with_guides.png",review)]:
        sequence[0].save(out/name,save_all=True,append_images=sequence[1:],duration=durations,loop=0,disposal=0,blend=0)
    frames[0].save(out/"poster.png")
    selected=sorted(set([1,round(len(frames)*.2),round(len(frames)*.4),round(len(frames)*.6),round(len(frames)*.8),len(frames)]))
    sheet(out,[frames[n-1] for n in selected],selected,"strip.jpg")
    backing=Image.new("RGBA",SIZE,"#f7f5ef")
    writer=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s","540x960","-r","15","-i","-","-an","-c:v","libx264","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(out/"preview.mp4")],stdin=subprocess.PIPE)
    for frame in review:writer.stdin.write(Image.alpha_composite(backing,frame).convert("RGB").tobytes())
    writer.stdin.close();assert writer.wait()==0
    image=Image.open(out/"guide.png");duration=0
    for n in range(image.n_frames):image.seek(n);duration+=image.info.get("duration",0)
    assert abs(duration-sum(durations))<1
    first=np.asarray(frames[0]);last=np.asarray(frames[-1]);change=float(np.mean(np.any(first!=last,axis=2)))
    peak_change=max(float(np.mean(np.any(first!=np.asarray(frames[n]),axis=2))) for n in sorted(set([len(frames)//4,len(frames)//2,3*len(frames)//4,len(frames)-1])))
    assert peak_change>.0001 or spec.get("static_hold"),"The declared camera/object action must produce a visible change"
    checks=dict(frames=len(frames),fps=15,duration_ms=duration,main_fill_alpha=.25,alpha_multiplier_applied_once=.5,
                build_fingerprint=spec.get("build_fingerprint"),
                encoded_apng_frames=image.n_frames,first_last_changed_fraction=change,peak_sample_changed_fraction=peak_change,
                contains_walls=False,rgb_preserved_in_final_alpha_pass=True,
                scope=spec.get("scope","Shot plus contextual handover"),handover_status=spec.get("handover_status"),
                original_render_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (out/"contours").glob("frame_*.png")})
    if (out/'gliding-light.json').exists():checks['gliding_light_sha256']=hashlib.sha256((out/'gliding-light.json').read_bytes()).hexdigest()
    (out/"export-checks.json").write_text(json.dumps(checks,indent=2)+"\n")
    spec["status"]="shot_exported_pending_visual_review";(out/"scene-spec.json").write_text(json.dumps(spec,indent=2)+"\n")
    print(json.dumps({k:v for k,v in checks.items() if k!="original_render_sha256"}))


if __name__=="__main__":
    if '--profile' in sys.argv and sys.argv[sys.argv.index('--profile')+1]=='p0':
        from export_p0 import export
        gid=sys.argv[1]
        source=Path(sys.argv[sys.argv.index('--source')+1]) if '--source' in sys.argv else BASE/'catalog/p0/animations-light'/gid
        export(source)
    else:run(sys.argv[1],"--probes" in sys.argv)
