"""Sequence the approved generated viewpoints; do not simulate orbit by panning art."""
import importlib.util
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
GUIDES=HERE.parents[1]
ROOT=HERE.parents[2]
W,H,FPS=405,720,15


def pair_flow(a,b):
    def gray(image):
        rgba=np.asarray(image,dtype=np.float32)
        return np.clip((255-rgba[:,:,:3].mean(axis=2))*.6+rgba[:,:,3]*.5,0,255).astype(np.uint8)
    ga,gb=gray(a),gray(b)
    return (cv2.calcOpticalFlowFarneback(ga,gb,None,.5,5,35,5,7,1.5,0),
            cv2.calcOpticalFlowFarneback(gb,ga,None,.5,5,35,5,7,1.5,0))


def interpolate(a,b,flows,progress):
    if progress<=0:return a.copy()
    if progress>=1:return b.copy()
    aa,bb=np.asarray(a,dtype=np.float32),np.asarray(b,dtype=np.float32)
    aa[:,:,:3]*=aa[:,:,3:4]/255;bb[:,:,:3]*=bb[:,:,3:4]/255
    yy,xx=np.indices(aa.shape[:2],dtype=np.float32)
    f,r=flows
    left=cv2.remap(aa,xx-f[:,:,0]*progress,yy-f[:,:,1]*progress,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    right=cv2.remap(bb,xx-r[:,:,0]*(1-progress),yy-r[:,:,1]*(1-progress),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
    mixed=left*(1-progress)+right*progress
    mixed[:,:,:3]=np.divide(mixed[:,:,:3]*255,mixed[:,:,3:4],out=np.zeros_like(mixed[:,:,:3]),where=mixed[:,:,3:4]>0)
    return Image.fromarray(np.clip(mixed,0,255).astype(np.uint8))


def alpha_batch(frames):
    lut=[(value+1)//2 for value in range(256)]
    results=[]
    for original in frames:
        output=original.copy()
        output.putalpha(original.getchannel('A').point(lut))
        assert np.array_equal(np.asarray(original)[:,:,:3],np.asarray(output)[:,:,:3])
        results.append(output)
    return results


def main():
    source=Image.open(HERE/'keyframes-original.png').convert('RGBA')
    # The generated sheet has two columns and three rows. Equal row spacing
    # is measured from the actual approved artwork, not its outer blank margin.
    origins=[(0,60),(470,60),(0,580),(470,580),(0,1100),(470,1100)]
    centers=[(230,207),(225,207),(236,207),(230,207),(236,207),(234,207)]
    views=[]
    for i,((x,y),(cx,cy)) in enumerate(zip(origins,centers)):
        cell=source.crop((x,y,min(x+471,source.width),y+535))
        scale=.86
        transform=(1/scale,0,cx-W/(2*scale),0,1/scale,cy-345/scale)
        view=cell.transform((W,H),Image.Transform.AFFINE,transform,resample=Image.Resampling.BICUBIC)
        views.append(view)
    flows=[pair_flow(a,b) for a,b in zip(views,views[1:])]
    frames=[]
    duration=4.7
    for index in range(math.ceil(duration*FPS)):
        t=index/FPS
        linear=max(0,min(1,(t-1.2)/1.8))
        position=(1-math.cos(math.pi*linear))/2*5
        segment=min(4,int(position))
        frame=interpolate(views[segment],views[segment+1],flows[segment],position-segment)
        if t>4.4:
            fade=max(0,(duration-t)/.3)
            frame.putalpha(frame.getchannel('A').point(lambda value:round(value*fade)))
        frames.append(frame)
    # All viewpoints/frames exist first. Alpha is applied in one final pass.
    exported=alpha_batch(frames)
    exported[0].save(HERE/'guide.png',save_all=True,append_images=exported[1:],duration=1000/FPS,loop=0,disposal=0,blend=0)
    exported[0].save(HERE/'poster.png')
    design=ROOT.parent/'codex_design_study/render_guided_reviews.py'
    spec=importlib.util.spec_from_file_location('fixed_sights',design)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    frame_paths,composition=module.geometry()
    ui=module.layer(composition+frame_paths)
    ui50=alpha_batch([ui])[0];ui50.save(HERE/'viewfinder.png')
    guided=alpha_batch([Image.alpha_composite(frame,ui) for frame in frames])
    guided[0].save(HERE/'guide_with_guides.png',save_all=True,append_images=guided[1:],duration=1000/FPS,loop=0,disposal=0,blend=0)
    previews=[]
    for image in guided:
        background=Image.new('RGBA',(W,H),'#23343e');background.alpha_composite(image)
        previews.append(background.convert('RGB'))
    previews[0].save(HERE/'preview.gif',save_all=True,append_images=previews[1:],duration=1000/FPS,loop=0)
    sheet=Image.new('RGB',(1080,320),'#23343e')
    for col,t in enumerate([.6,1.56,1.92,2.28,2.64,3.5]):
        sheet.paste(previews[min(len(previews)-1,round(t*FPS))].resize((180,320),Image.Resampling.LANCZOS),(180*col,0))
    sheet.save(HERE/'strip.png')
    guide=json.loads((GUIDES/'templates/cup_eye_orbitr_cc.json').read_text())
    record=dict(guide='cup_eye_orbitr_cc',description=guide['description'],source_timeline=guide['timeline'],source_live_steps=guide['live']['steps'],
                generated_views=6,atlas_layout=[2,3],atlas_crop_origins=origins,atlas_registration=centers,
                camera_angle='At cup height, approximately horizontal, throughout the shot.',
                move='Right orbit through 60 degrees; centered subject, constant framing and distance.',
                timing={'start_hold':[0,1.2],'orbit':[1.2,3.0],'end_hold':[3.0,4.4],'fade':[4.4,4.7]},
                fps=FPS,samples=len(frames),alpha_factor=.5,alpha_phase='Final batch after all rendered frames exist',
                colors_unchanged_by_alpha=True,method='Generated changing viewpoints; bidirectional optical-flow interpolation. No simulated camera pan/zoom of a single illustration.')
    (HERE/'guide.json').write_text(json.dumps(record,indent=2)+'\n')
    print(f'{len(frames)} frames; 6 generated viewpoints; alpha applied as final batch; cup-height orbit.')


if __name__=='__main__':main()
