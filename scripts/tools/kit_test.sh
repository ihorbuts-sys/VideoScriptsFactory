#!/bin/zsh
# Runs VideoScriptsTests on a scratch copy of VideoEditorKit with scripts/script_templates.json in place.
# Run A: the catalog as is. Run B: the same catalog with stand-ins for what agents 02 and 03 still owe
# (a copy of an existing step image per missing image, one existing overlay per step), so every other test can pass.
# Usage: kit_test.sh <scratch directory>
set -e
KIT=/Users/ihor.buts/Documents/Development/VideoEditorKit
HERE=${0:A:h}
SCRATCH=${1:?scratch directory}
COPY=$SCRATCH/kit
RES=$COPY/Sources/VideoScripts/Resources
mkdir -p $COPY
rsync -a --delete --exclude .git --exclude Demo --exclude tools --exclude docs --exclude .build $KIT/ $COPY/
cp $HERE/../script_templates.json $RES/script_templates.json
cd $COPY
echo "== Run A: catalog as is"
swift test --filter VideoScriptsTests 2>&1 | grep -E "passed after|failed after|error:" | grep -vE " Test .* passed after" | tail -25 || true
python3 -I - $RES <<'EOF'
import json, os, shutil, sys
res = sys.argv[1]
path = os.path.join(res, 'script_templates.json')
d = json.load(open(path))
previews = os.path.join(res, 'StepPreviews')
stand_in = sorted(os.listdir(previews))[0]
made = 0
for t in d['templates']:
    for s in t['steps']:
        target = os.path.join(previews, s['imageURL'])
        if not os.path.exists(target):
            shutil.copy(os.path.join(previews, stand_in), target)
            made += 1
        s['overlays'] = ['talking_head_eye_level']
json.dump(d, open(path, 'w'), indent=2)
print(f"stand-in images: {made}")
EOF
echo "== Run B: with stand-in images and overlays"
swift test --filter VideoScriptsTests 2>&1 | grep -E "Test run|failed after|error:" | tail -25 || true
