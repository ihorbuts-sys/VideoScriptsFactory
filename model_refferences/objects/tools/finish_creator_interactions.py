"""Keep the batch browsable, then assemble and verify the complete bakery flow."""
import json,subprocess,sys,time
from pathlib import Path
import creator_interaction_gallery as gallery
from assemble_bakery_box_sequence import run as assemble
BASE=Path(__file__).resolve().parents[3]
CATALOG=Path('/Users/ihor.buts/Documents/Development/Scriptwriter/catalog')

def run():
    previous=None;deadline=time.monotonic()+10800
    while True:
        rejected=[k for k in gallery.KEYS if (gallery.ROOT/k/'review-status.json').exists() and json.loads((gallery.ROOT/k/'review-status.json').read_text()).get('status')=='rejected']
        if rejected:
            gallery.run()
            print(json.dumps(dict(status='withdrawn_after_owner_review',scenes=rejected)),flush=True)
            return
        assert time.monotonic()<deadline,'Interaction render window expired'
        ready=tuple(k for k in gallery.KEYS if (gallery.ROOT/k/'publication.json').exists())
        if ready!=previous:gallery.run();previous=ready
        if len(ready)==4:break
        time.sleep(5)
    time.sleep(2)
    assemble(CATALOG)
    subprocess.run([sys.executable,str(BASE/'api/check_glass_batch_live.py'),'--server',str(CATALOG.parent)],check=True)
    subprocess.run([sys.executable,str(BASE/'api/check_creator_interaction_scope.py')],check=True)
    gallery.run()
    print('CREATOR_INTERACTIONS_COMPLETE',flush=True)

if __name__=='__main__':run()
