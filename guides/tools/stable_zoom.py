"""Rebuild zoom and held close-up frames from one existing generated image.

No illustration is drawn here. Every frame samples the same saved master PNG;
the camera crop changes while the source object's geometry and pigment stay fixed.
"""
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

GUIDES=Path(__file__).resolve().parents[1]
ROOT=GUIDES.parent
OUT=GUIDES/'watercolor_motion'
W,H=405,720

FOCUS={
    'burger_cut_high_in_cd_through':(.35,.57),
    'burger_cut_high_in_cd_whipout':(.35,.57),
    'burger_cut_low_in_cd':(.50,.54),
    'burger_low_in_mc':(.50,.52),
    'card_menu_high_in_cd_whipout':(.65,.54),
    'card_tag_top_in_cd':(.57,.51),
    'card_tag_top_in_cd_through':(.72,.58),
    'card_ticket_eye_in_cd':(.50,.58),
    'case_eye_in_mc_through':(.53,.49),
    'case_eye_out_cm':(.50,.44),
    'counter_barista_side':(.66,.54),
    'cup_high_out_dm':(.48,.57),
    'door_curtain_eye_in_md_through':(.50,.51),
    'door_eye_in_wd_through':(.52,.625),
    'door_pov_in_wc_through':(.52,.56),
    'door_pov_in_wd_through':(.52,.615),
    'facade_eye_in_wm':(.50,.61),
    'facade_truck_eye_in_wm':(.50,.56),
    'glass_outro_high_out_dm':(.51,.59),
    'glass_pour_eye_in_cd_through':(.50,.49),
    'glass_pour_low_in_cd':(.50,.53),
    'hair_work_high_in_cd_through':(.49,.69),
    'hand_pov_garment_pov_in_mc':(.53,.48),
    'hand_pov_item_pov_in_mc':(.54,.45),
    'over_shoulder_hands_os_in_mc':(.60,.50),
    'topdown_box_top_out_cm':(.52,.54),
}

# A push-through's ending illustration must show the named surface, rather than
# a replacement texture generated for the last pose. Record this crop separately
# from the legacy live-sensor amount, which was not calibrated to these paintings.
SURFACE_ZOOM={
    'burger_cut_high_in_cd_through':4.0,
    'card_tag_top_in_cd_through':4.2,
    'case_eye_in_mc_through':6.0,
    'glass_pour_eye_in_cd_through':4.0,
    'hair_work_high_in_cd_through':4.0,
}


def plan():
    import guide_motion_render as render
    manifest=json.loads((OUT/'manifest.json').read_text())
    available=set(json.loads((ROOT/'catalog/animations/index.json').read_text())['guides'])
    folder=OUT/'masters';folder.mkdir(exist_ok=True)
    records=[]
    for entry in manifest['guides']:
        if entry['id'] not in available:continue
        if entry.get('local_motion_sources'):continue
        follows=[s for s in entry['source_live_steps'] if s['kind']=='follow']
        zoom=next((s for s in follows if s['action'] in ('dolly_in','dolly_out')),None)
        close_hold=not follows and ('close' in entry['description'] or 'detail' in entry['description'])
        if not zoom and not close_hold:continue
        gid=entry['id'];direction=zoom['action'] if zoom else 'hold'
        cells,_=render.atlas_cells(entry)
        source_index=5 if direction=='dolly_out' else 0
        if gid=='burger_cut_low_in_cd':source_index=3
        if gid in ('card_menu_top_hold','card_pricelist_top_hold'):source_index=3
        master=folder/f'{gid}.png';cells[source_index].save(master)
        amount=float(zoom.get('amount',1.25)) if zoom else 1
        extent=max(amount,1/max(.001,amount)) if zoom else 1
        if gid in SURFACE_ZOOM:extent=max(extent,SURFACE_ZOOM[gid])
        start_zoom=extent if direction=='dolly_out' else 1
        end_zoom=extent if direction=='dolly_in' else 1
        fx,fy=FOCUS.get(gid,(.5,.5))
        def rectangle(scale):
            if scale==1:return [0,0,W,H]
            return [fx*W-W/(2*scale),fy*H-H/(2*scale),W/scale,H/scale]
        config=dict(method='single_source_crop',master=str(master.resolve()),
                    master_sha256=hashlib.sha256(master.read_bytes()).hexdigest(),
                    source_original=entry['original'],source_cell=entry.get('hold_cell',source_index),
                    selected_staged_view=source_index,
                    mode=direction,start_rect=rectangle(start_zoom),end_rect=rectangle(end_zoom),
                    focus=[fx,fy],start_zoom=start_zoom,end_zoom=end_zoom,
                    source_live_amount=amount,ending_surface_crop=gid in SURFACE_ZOOM,
                    sensor_scenarios_changed=False,synthetic_subject_motion=False,
                    note='Same illustration sampled for every frame. Camera crop/zoom only; no independently generated poses or optical-flow morphing.')
        entry['rendering']=config
        existing=ROOT/'catalog/animations'/gid
        archive=ROOT/'catalog/backups/pre-stable-zoom/animations'/gid
        if not archive.exists():shutil.copytree(existing,archive)
        records.append(dict(id=gid,**config))
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    report=dict(count=len(records),zoom=sum(e['mode']!='hold' for e in records),
                close_holds=sum(e['mode']=='hold' for e in records),guides=records)
    (ROOT/'catalog/stable-zoom-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'{len(records)} single-image masters ready; {report["zoom"]} zoom guides and {report["close_holds"]} held close-ups.')


def crop_at(entry,t,eased):
    config=entry['rendering'];start=config['start_rect'];end=config['end_rect']
    if config['mode']=='hold':return start.copy()
    window=entry['windows'][0]
    progress=eased((t-window['start'])/(window['end']-window['start']),window['ease'])
    rect=[a+(b-a)*progress for a,b in zip(start,end)]
    if len(entry['windows'])>1:
        window=entry['windows'][1]
        p=eased((t-window['start'])/(window['end']-window['start']),window['ease'])
        direction=config.get('whip_direction') or next((s.get('direction','right') for s in entry['source_live_steps'] if s.get('action')=='whip'),'right')
        if direction in ('right','left'):rect[0]+=end[2]*1.7*p*(1 if direction=='right' else -1)
        else:rect[1]+=end[3]*1.7*p*(1 if direction=='down' else -1)
    return rect


def frame_at(master,entry,t,eased):
    x,y,width,height=crop_at(entry,t,eased)
    return master.transform((W,H),Image.Transform.AFFINE,
                            (width/W,0,x,0,height/H,y),
                            resample=Image.Resampling.BICUBIC)


if __name__=='__main__':plan()
