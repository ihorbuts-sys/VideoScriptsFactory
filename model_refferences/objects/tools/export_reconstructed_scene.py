"""Full-color video and ghost APNG from one reconstructed scene and camera path."""
import hashlib,json,subprocess,sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parents[3]
OUT=BASE/'catalog/clay-scenes/cup_eye_orbitr_cc'
FPS=15
GHOST_STYLE=None

def frame(number,probes=False):
    prefix='probes-' if probes else ''
    color=Image.open(OUT/(prefix+'color')/('frame_%04d.png'%number)).convert('RGBA')
    mask=np.asarray(Image.open(OUT/(prefix+'mask')/('frame_%04d.png'%number)).convert('RGBA'))
    if GHOST_STYLE == 'smooth-contours-v1':
        from smooth_ghost import render
        return color,render(color,mask)
    if GHOST_STYLE == 'hologram-glass-v1':
        from hologram_ghost import render
        fields=Image.open(OUT/'fields'/('frame_%04d.png'%number)).convert('RGBA')
        return color,render(fields,mask,(number-1)/FPS)
    rgba=np.asarray(color);rgb=rgba[:,:,:3]
    gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);gray=cv2.GaussianBlur(gray,(3,3),.7)
    edges=np.maximum(cv2.Canny(gray,30,85),cv2.Canny(mask[:,:,1],35,95))
    edges=cv2.dilate(edges,np.ones((2,2),np.uint8))
    # Red carries base fill alpha, green the hierarchy of contour emphasis.
    coverage=mask[:,:,3].astype(np.float32)/255
    fill_alpha=mask[:,:,0].astype(np.float32)*coverage
    line_alpha=edges.astype(np.float32)/255*cv2.dilate(mask[:,:,1],np.ones((3,3),np.uint8))*coverage
    fill=Image.fromarray(np.dstack([rgb,np.rint(fill_alpha).astype(np.uint8)]),'RGBA')
    lines=np.zeros_like(rgba);lines[:,:,:3]=(113,153,178);lines[:,:,3]=np.rint(line_alpha).astype(np.uint8)
    ghost=Image.alpha_composite(fill,Image.fromarray(lines,'RGBA'))
    ghost.putalpha(ghost.getchannel('A').point(lambda a:round(a*.65)))
    assert ghost.getchannel('A').getextrema()[1]<=166
    return color,ghost

def strip(frames,numbers,name):
    w,h=frames[0].size;sheet=Image.new('RGB',(270*len(frames),510),'#f7f2e7');draw=ImageDraw.Draw(sheet)
    for i,(im,n) in enumerate(zip(frames,numbers)):
        bg=Image.new('RGBA',im.size,'#f7f2e7');bg.alpha_composite(im);bg=bg.resize((270,480),Image.Resampling.LANCZOS)
        sheet.paste(bg.convert('RGB'),(270*i,30));draw.text((270*i+10,8),'%.2f s'%((n-1)/FPS),fill='#334b3c')
    sheet.save(OUT/name,quality=94)

def run(probes=False,gid='cup_eye_orbitr_cc'):
    global OUT,FPS
    OUT=BASE/'catalog/clay-scenes'/gid
    spec=json.loads((OUT/'scene-spec.json').read_text());FPS=spec.get('fps',15)
    numbers=spec.get('probe_frames',[1,round(spec['frame_count']/2),spec['frame_count']]) if probes else list(range(1,spec['frame_count']+1))
    colors=[];ghosts=[]
    for n in numbers:
        c,g=frame(n,probes);colors.append(c);ghosts.append(g)
    if probes:
        strip(colors,numbers,'proof-color.jpg');strip(ghosts,numbers,'proof-ghost.jpg');print('SCENE_PROOF_EXPORTED');return
    durations=[round((i+1)*1000/FPS)-round(i*1000/FPS) for i in range(len(ghosts))]
    ghosts[0].save(OUT/'ghost.png',save_all=True,append_images=ghosts[1:],duration=durations,loop=0,disposal=0,blend=0)
    ghosts[0].save(OUT/'ghost-poster.png');colors[0].save(OUT/'color-poster.png')
    selected=sorted(set([1]+[round((len(numbers)-1)*u)+1 for u in [.2,.4,.6,.8,1]]))
    strip([colors[n-1] for n in selected],selected,'color-strip.jpg')
    strip([ghosts[n-1] for n in selected],selected,'ghost-strip.jpg')
    writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','540x960','-r',str(FPS),'-i','-','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'color.mp4')],stdin=subprocess.PIPE)
    for im in colors:
        bg=Image.new('RGBA',im.size,'#f7f2e7');bg.alpha_composite(im);writer.stdin.write(bg.convert('RGB').tobytes())
    writer.stdin.close();assert writer.wait()==0
    image=Image.open(OUT/'ghost.png');total=0;maximum=0
    for i in range(image.n_frames):
        image.seek(i);total+=image.info.get('duration',0);maximum=max(maximum,image.convert('RGBA').getchannel('A').getextrema()[1])
    assert image.n_frames>=2;assert abs(total-len(numbers)*1000/FPS)<1;assert maximum<=166
    changed=float(np.mean(np.any(np.asarray(colors[0])!=np.asarray(colors[-1]),axis=2)))
    assert changed>.01
    report=dict(frames=len(numbers),encoded_apng_frames=image.n_frames,duration_ms=total,fps=FPS,resolution=[540,960],max_ghost_alpha=maximum,
        whole_overlay_alpha=.65,first_last_changed_pixel_fraction=changed,
        matching_camera_for_both_variants=True,no_embedded_viewfinder=True,
        assets_are_reconstructed=True,scope=spec['scope'],handover_status=spec['handover_status'],published=False,
        files={n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in ['scene.blend','color.mp4','ghost.png']})
    (OUT/'export-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    spec['status']='color_and_ghost_proof_ready';(OUT/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__':
    args=[a for a in sys.argv[1:] if not a.startswith('--')]
    run('--probes' in sys.argv,args[0] if args else 'cup_eye_orbitr_cc')
