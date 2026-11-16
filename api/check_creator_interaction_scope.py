"""Verify per-step variants coexist without changing unrelated scripts or guide defaults."""
import json,urllib.request,urllib.parse
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
SERVER=Path('/Users/ihor.buts/Documents/Development/Scriptwriter')
TARGETS={'bakery-box.case','bakery-box.pick','bakery-box.box','bakery-box.total','cafe-seasonal-drink.verdict'}

def run():
    before=json.loads((BASE/'catalog/interaction-scenes/catalog-before.json').read_text())
    current=json.loads((SERVER/'catalog/catalog.json').read_text())
    assert current['guides']==before['guides'],'Guide defaults must remain unchanged'
    assert current['previewArt']==before['previewArt']
    for tid,t in {t['id']:t for t in before['templates']}.items():
        after=next(r for r in current['templates'] if r['id']==tid)
        for step in t['steps']:
            if tid+'.'+step['id'] not in TARGETS:assert next(s for s in after['steps'] if s['id']==step['id'])==step
    for key,overrides in before['stepGuideOverrides'].items():
        if key not in TARGETS:assert current['stepGuideOverrides'][key]==overrides
    for tid,value in before['scriptGuideSequences'].items():
        if tid!='bakery-box':assert current['scriptGuideSequences'][tid]==value
    token=(SERVER/'.token').read_text().strip()
    def get(path):
        r=urllib.request.Request('http://127.0.0.1:8765'+path,headers={'Authorization':'Bearer '+token})
        with urllib.request.urlopen(r,timeout=30) as response:return json.load(response)
    paths=[];bindings=[]
    for key in ['bakery-box.hook','cafe-seasonal-drink.verdict','bakery-box.total']:
        result=get('/v1/steps/'+key+'/guides');row=next(g for g in result['guides'] if g['id']=='selfie_one_high_hold')
        paths.append(urllib.parse.urlparse(row['overlayURL']).path)
        bindings.append(dict(step=key,seconds=row['seconds'],animation_seconds=row['animationSeconds']))
    assert len(set(paths))==3,'The three contexts need distinct artwork'
    assert [r['seconds'] for r in bindings]==[6,10,6]
    seq=get('/v1/scripts/bakery-box/guide-sequence')
    duration=seq.get('animationSeconds',seq['seconds'])
    assert seq['fullScriptSequenceComplete'] and abs(duration-35)<.01
    assert [r['step_id'] for r in seq['steps']]==['hook','case','pick','box','total']
    report=dict(status='passed',guide_defaults_preserved=True,unrelated_steps_preserved=True,unrelated_overrides_preserved=True,
        preview_art_preserved=True,three_selfie_variants_distinct=True,variants=bindings,full_bakery_steps=5)
    (BASE/'catalog/interaction-scenes/api-scope-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

if __name__=='__main__':run()
