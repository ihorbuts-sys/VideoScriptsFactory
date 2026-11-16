"""Reject automatic full-next-shot copies and verify the reported cafe slices."""
from pathlib import Path
from PIL import Image
import json
import hashlib

BASE=Path(__file__).resolve().parents[2]
ROOT=BASE/'catalog/context-animations'
manifest=json.loads((ROOT/'index.json').read_text())
before=json.loads((BASE/'catalog/cafe-review/before-context-index.json').read_text())
cuts=[];whips=[];connected=[];changed=[]
for key,row in manifest['steps'].items():
    if not row.get('folder'):continue
    folder=BASE/row['folder'];check=json.loads((folder/'assembly-checks.json').read_text())
    primary=row['source']['frames'];total=check['frames']
    if row.get('handover_status')=='cut_to_next_step':
        assert total==primary and len(check['stages'])==1,(key,total,primary)
        # The final image must be the final frame of this step's own native slice.
        origin=row['source'];last=origin['source_start_frame']+primary-1
        expected=Image.open(BASE/origin['source']/'ghost_frames'/('frame_%04d.png'%last)).convert('RGBA')
        actual=Image.open(folder/'guide.png');actual.seek(actual.n_frames-1)
        assert actual.convert('RGBA').tobytes()==expected.tobytes(),key
        cuts.append(key)
    if row.get('transition_method')=='brief_right_whip':
        assert total-primary==9 and len(check['stages'])==2,key
        whips.append(key)
    elif row.get('handover_status')=='included':
        stage=check['stages'][1];next_key=row['template_id']+'.'+stage['next_step']
        next_source=manifest['steps'][next_key]['source']
        if next_source['source']==row['source']['source']:
            assert stage['source']['source_start_frame']+stage['frames']<=next_source['source_start_frame']+9,key
        connected.append(key)
    if before['steps'].get(key,{}).get('sha256')!=row['sha256']:changed.append(key)
cup=manifest['steps']['cafe-morning-ritual.cup']
pastry=manifest['steps']['cafe-morning-ritual.pastry']
assert cup['source']['frames']==75 and pastry['source']['source_start_frame']==76
assert pastry['source']['frames']==51 and pastry['source']['source']==cup['source']['source']
assert pastry['handover_status']=='cut_to_next_step' and pastry['duration']==3.4
spec=json.loads((BASE/cup['source']['source']/'scene-spec.json').read_text())
assert not any('laptop' in o['name'].lower() for o in spec['objects'])
sequence=manifest['scripts']['cafe-morning-ritual']
assert len({s['step_id'] for s in sequence['steps']})==len(sequence['steps'])==4
assert abs(sequence['duration']-sum(s['frames'] for s in sequence['steps'])/15)<.001
for key in ['cafe-first-visit.counter','cafe-before-opening.lights']:
    assert manifest['steps'][key].get('folder') and manifest['steps'][key].get('status')!='deferred_people'
baseline=json.loads((BASE/'guides/watercolor/input_hashes.json').read_text())
changed_sources=[rel for rel,sha in baseline.items() if hashlib.sha256((BASE/rel).read_bytes()).hexdigest()!=sha]
assert not changed_sources
report=dict(status='passed',cut_steps_end_on_own_frame=len(cuts),brief_whip_landings=len(whips),
    native_connected_handovers=len(connected),changed_context_steps=len(changed),changed_steps=changed,
    no_automatically_appended_full_next_shots=True,morning_cup_and_pastry_same_scene=True,
    morning_pastry_has_no_laptop=True,full_script_shows_each_step_once=True,
    source_files_preserved=len(baseline),source_files_changed=changed_sources)
(BASE/'catalog/cafe-review/boundary-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('STEP_BOUNDARIES_VERIFIED',len(cuts),len(whips),len(connected),len(changed),flush=True)
