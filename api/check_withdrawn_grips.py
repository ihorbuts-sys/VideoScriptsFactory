"""Check that rejected grips cannot remain the active API artwork."""
import json,urllib.request,urllib.error
from pathlib import Path
from withdraw_hand_studies import BASE,SERVER,TARGETS,REJECTED

def run():
    before=json.loads((BASE/'catalog/interaction-scenes/catalog-before.json').read_text())
    current=json.loads((SERVER/'catalog.json').read_text())
    token=(SERVER.parent/'.token').read_text().strip()
    def get(path):
        request=urllib.request.Request('http://127.0.0.1:8765'+path,headers={'Authorization':'Bearer '+token})
        with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
    for key in TARGETS:
        tid,sid=key.split('.')
        a=next(s for t in before['templates'] if t['id']==tid for s in t['steps'] if s['id']==sid)
        z=next(s for t in current['templates'] if t['id']==tid for s in t['steps'] if s['id']==sid)
        assert z==a,key
        assert current['stepGuideOverrides'].get(key)==before['stepGuideOverrides'].get(key),key
        get('/v1/steps/'+key+'/guides')
    assert current['scriptGuideSequences']['bakery-box']==before['scriptGuideSequences']['bakery-box']
    for key in REJECTED:
        try:get('/v1/guide-collections/coffee-guide-'+key)
        except urllib.error.HTTPError as error:assert error.code==404
        else:raise AssertionError('Rejected collection is still published: '+key)
    r=dict(status='passed',restored_step_bindings=sorted(TARGETS),rejected_collections_unavailable=True,
        prior_bakery_sequence_restored=True,preview_art_preserved=current['previewArt']==before['previewArt'])
    (BASE/'catalog/interaction-scenes/withdrawal/live-api-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))

if __name__=='__main__':run()
