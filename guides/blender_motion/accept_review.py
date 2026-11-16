"""Record an explicit completed visual review, bound to the exported artifact hash.

Call only after inspecting source plans, framing proofs and final motion samples.
"""
from pathlib import Path
import hashlib
import json
import sys
BASE=Path(__file__).resolve().parents[2]
plan=BASE/'guides/blender_motion/work-plan.json';work=json.loads(plan.read_text())
for gid in sys.argv[1:]:
 out=BASE/'catalog/blender-animations'/gid
 spec=json.loads((out/'scene-spec.json').read_text());checks=json.loads((out/'export-checks.json').read_text());geometry=json.loads((out/'geometry-checks.json').read_text())
 assert geometry['status']=='passed'
 assert checks['build_fingerprint']==spec['build_fingerprint']
 assert checks['main_fill_alpha']==.25 and checks['rgb_preserved_in_final_alpha_pass']
 review=dict(status='shot_and_handover_reviewed' if spec.get('scope')=='shot_and_handover' else 'final_shot_reviewed' if spec.get('scope')=='complete_final_shot' else 'base_shot_reviewed',
             guide_sha256=hashlib.sha256((out/'guide.png').read_bytes()).hexdigest(),
             observations=spec.get('subject_actions',spec['composition']),
             reviewed_artifacts=['source description and script contexts','pre-render-review.json','proof.jpg','strip.jpg','geometry-checks.json','export-checks.json'],
             handover=spec.get('handover_status'),mobile_feasibility=spec.get('mobile_feasibility'),publication='Reviewed for local guide API')
 (out/'review.json').write_text(json.dumps(review,indent=2)+'\n')
 for g in work['guides']:
  if g['id']==gid:g.update(status=review['status'],handover_status=spec.get('handover_status'))
ready=[g for g in work['guides'] if g['status'] in ['approved_prototype','shot_and_handover_reviewed','base_shot_reviewed','final_shot_reviewed']]
work['counts'].update(unique_guides_with_blender_work=len(ready),remaining_guides_without_blender_shot=178-len(ready),reviewed_new_base_shots=sum(g['status']=='base_shot_reviewed' for g in ready),reviewed_shot_and_handover=sum(g['status'] in ['shot_and_handover_reviewed','approved_prototype'] for g in ready),reviewed_final_shots=sum(g['status']=='final_shot_reviewed' for g in ready))
plan.write_text(json.dumps(work,indent=2)+'\n')
print('Accepted visual reviews:',len(sys.argv)-1,'; remaining:',178-len(ready))
