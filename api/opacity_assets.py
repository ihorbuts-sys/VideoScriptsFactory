"""One final configurable whole-image opacity pass, derived from preserved animation masters."""
from pathlib import Path
from PIL import Image,ImageDraw
import hashlib
import json
import subprocess

BASE=Path(__file__).resolve().parent.parent
TARGET=.65
PERCENT=round(TARGET*100)
OUT=BASE/f'catalog/opacity-{PERCENT}/assets'
MAX_ALPHA=round(255*TARGET)


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assets(source,video=False):
    source=Path(source);sha=digest(source);folder=OUT/(sha[:20]+f'-{PERCENT}-v1');record_path=folder/'opacity.json'
    if record_path.exists():
        record=json.loads(record_path.read_text())
        if record['source_sha256']==sha and record['opacity']==TARGET and (not video or record.get('video') and (folder/'preview.mp4').exists()):return record
    with Image.open(source) as image:
        frames=[];durations=[];maximum=0
        for i in range(getattr(image,'n_frames',1)):
            image.seek(i);frame=image.convert('RGBA');frames.append(frame)
            durations.append(image.info.get('duration',1000/15));maximum=max(maximum,frame.getchannel('A').getextrema()[1])
    scale=MAX_ALPHA/maximum if maximum else 1
    for frame in frames:
        rgb=frame.convert('RGB').tobytes();frame.putalpha(frame.getchannel('A').point(lambda value:round(value*scale)))
        assert frame.convert('RGB').tobytes()==rgb
    folder.mkdir(parents=True,exist_ok=True)
    frames[0].save(folder/'guide.png',save_all=len(frames)>1,append_images=frames[1:],duration=durations,loop=0,disposal=0,blend=0)
    frames[0].save(folder/'poster.png');total=sum(durations);times=[];elapsed=0
    for duration in durations:times.append(elapsed);elapsed+=duration
    selected=[]
    for fraction in [0,.2,.4,.6,.8,.999]:
        target=total*fraction;selected.append(max(i for i,t in enumerate(times) if t<=target))
    backing=Image.new('RGBA',frames[0].size,'#f7f5ef');sheet=Image.new('RGB',(1620,510),'#f7f5ef');draw=ImageDraw.Draw(sheet)
    for column,index in enumerate(selected):
        im=Image.alpha_composite(backing,frames[index]).convert('RGB').resize((270,480),Image.Resampling.LANCZOS)
        sheet.paste(im,(column*270,30));draw.text((column*270+8,8),f'{times[index]/1000:.2f} s',fill='#496475')
    sheet.save(folder/'strip.jpg',quality=94)
    if video:
        size=frames[0].size;writer=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{size[0]}x{size[1]}','-r','15','-i','-','-an','-c:v','libx264','-threads','2','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(folder/'preview.mp4')],stdin=subprocess.PIPE)
        cursor=0
        for index in range(round(total*15/1000)):
            timestamp=index*1000/15
            while cursor+1<len(times) and times[cursor+1]<=timestamp:cursor+=1
            writer.stdin.write(Image.alpha_composite(backing,frames[cursor]).convert('RGB').tobytes())
        writer.stdin.close();assert writer.wait()==0
    record=dict(source=str(source.relative_to(BASE)) if source.is_relative_to(BASE) else str(source),source_sha256=sha,
        folder=str(folder.relative_to(BASE)),overlay=str((folder/'guide.png').relative_to(BASE)),poster=str((folder/'poster.png').relative_to(BASE)),
        strip=str((folder/'strip.jpg').relative_to(BASE)),video=str((folder/'preview.mp4').relative_to(BASE)) if video else None,
        sha256=digest(folder/'guide.png'),opacity=TARGET,max_alpha=MAX_ALPHA,master_max_alpha=maximum,
        derived_once_from_preserved_master=True,rgb_preserved=True,duration_ms=total,encoded_frames=len(frames))
    record_path.write_text(json.dumps(record,indent=2)+'\n');return record


if __name__=='__main__':
    from concurrent.futures import ThreadPoolExecutor
    bundle=json.loads((BASE/'api/bundle/catalog.json').read_text());sources={}
    for gid,guide in bundle['guides'].items():
        if guide['style']=='blender':source=BASE/'catalog/blender-animations'/gid/'guide.png'
        elif guide['style']=='watercolor':source=BASE/'catalog/animations'/gid/'guide.png'
        else:source=BASE/'guides/overlays/schematic'/(gid+'.png')
        sources[source]=guide['style']=='blender'
    manifest=json.loads((BASE/'catalog/context-animations/index.json').read_text())
    for group in ['steps','scripts']:
        for row in manifest[group].values():
            if row.get('folder'):
                source=BASE/row['folder']/'guide.png';sources[source]=sources.get(source,False) or group=='scripts'
    def create(pair):return assets(pair[0],video=pair[1])
    with ThreadPoolExecutor(max_workers=2) as pool:
        for number,record in enumerate(pool.map(create,sorted(sources.items())),1):
            if number%10==0:print('OPACITY_READY',number,len(sources),PERCENT,flush=True)
    print('ALL_OPACITY_ASSETS_READY',len(sources),PERCENT,flush=True)
