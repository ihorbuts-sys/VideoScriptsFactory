"""Withdraw owner-rejected grips while preserving all unrelated catalog data."""
import copy,json,os
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
SERVER=Path('/Users/ihor.buts/Documents/Development/Scriptwriter/catalog')
TARGETS={'bakery-box.pick','bakery-box.box','bakery-box.total','cafe-seasonal-drink.verdict'}
REJECTED=['creator-coffee-present','creator-pack-box','creator-box-total']

def read(p):return json.loads(p.read_text())
def write(p,r):
    tmp=p.with_suffix('.withdraw.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');os.replace(tmp,p)

def run():
    out=BASE/'catalog/interaction-scenes/withdrawal';out.mkdir(exist_ok=True)
    previous=read(BASE/'catalog/interaction-scenes/catalog-before.json')
    catalog=read(SERVER/'catalog.json');original=copy.deepcopy(catalog)
    manifest_path=BASE/'catalog/clay-scenes/active-revisions.json';manifest=read(manifest_path)
    baseline=read(BASE/'catalog/interaction-scenes/manifest-before.json')
    collection_path=SERVER/'guide-collections.json';collections=read(collection_path)
    for name,value in [('catalog-before-withdrawal.json',catalog),('manifest-before-withdrawal.json',manifest),('collections-before-withdrawal.json',collections)]:
        if not (out/name).exists():write(out/name,value)
    before_steps={t['id']+'.'+s['id']:s for t in previous['templates'] for s in t['steps']}
    for template in catalog['templates']:
        for step in template['steps']:
            key=template['id']+'.'+step['id']
            if key in TARGETS:
                for field in ['direction','seconds']:step[field]=before_steps[key][field]
    for group in catalog['stepGroups']:
        for step in group['steps']:
            key=step['templateID']+'.'+step['id']
            if key in TARGETS:
                for field in ['direction','seconds']:step[field]=before_steps[key][field]
    for key in TARGETS:
        if key in previous['stepGuideOverrides']:catalog['stepGuideOverrides'][key]=previous['stepGuideOverrides'][key]
        else:catalog['stepGuideOverrides'].pop(key,None)
    catalog['scriptGuideSequences']['bakery-box']=previous['scriptGuideSequences']['bakery-box']
    for gid in ['hand_pov_pastry_pov_in_mc','topdown_box_top_out_cm']:
        if gid in baseline['guides']:manifest['guides'][gid]=baseline['guides'][gid]
        else:manifest['guides'].pop(gid,None)
    for key in ['bakery-box.total','cafe-seasonal-drink.verdict']:manifest.get('guide_variants',{}).pop(key,None)
    if 'bakery-box' in baseline.get('sequences',{}):manifest['sequences']['bakery-box']=baseline['sequences']['bakery-box']
    else:manifest.get('sequences',{}).pop('bakery-box',None)
    reason='Owner rejected the cup and tong grips as unnatural. Numeric contact checks do not establish a natural grasp. Hand interaction work is deferred in favour of practical commercial camera guides.'
    for key in REJECTED:
        folder=BASE/'catalog/glass-rollout/coffee'/key
        write(folder/'review-status.json',dict(status='rejected',date='2026-11-02',reason=reason,publication_allowed=False))
        publication=folder/'publication.json'
        if publication.exists():publication.replace(folder/'withdrawn-publication.json')
        collections['collections'].pop('coffee-guide-'+key,None)
        p=folder/'index.html';text=p.read_text()
        if 'id="owner-rejection"' not in text:text=text.replace('<main>','<main><p id="owner-rejection"><strong>Rejected study / removed from the active API.</strong> Unnatural hand grip. Kept for inspection only; hand animation work is deferred.</p>',1)
        p.write_text(text)
    sequence=BASE/'catalog/glass-rollout/sequences/bakery-box'
    write(sequence/'review-status.json',dict(status='rejected',reason=reason,date='2026-11-02',publication_allowed=False))
    publication=sequence/'publication.json'
    if publication.exists():publication.replace(sequence/'withdrawn-publication.json')
    p=sequence/'index.html';text=p.read_text()
    if 'id="owner-rejection"' not in text:text=text.replace('<main>','<main><p id="owner-rejection"><strong>Withdrawn sequence / removed from the active API.</strong> Contains rejected cup or tong grips. Retained for inspection only.</p>',1)
    p.write_text(text)
    assert catalog['guides']==original['guides'] and catalog['previewArt']==original['previewArt']
    for key,row in original['stepGuideOverrides'].items():
        if key not in TARGETS:assert catalog['stepGuideOverrides'][key]==row
    write(SERVER/'catalog.json',catalog);write(manifest_path,manifest);write(collection_path,collections)
    report=dict(status='withdrawn',date='2026-11-02',scenes=REJECTED,step_bindings=sorted(TARGETS),full_sequence='bakery-box',
        reason=reason,original_preview_art_preserved=True,guide_defaults_preserved=True,unrelated_overrides_preserved=True,source_artifacts_preserved=True)
    write(out/'report.json',report);print(json.dumps(report))

if __name__=='__main__':run()
