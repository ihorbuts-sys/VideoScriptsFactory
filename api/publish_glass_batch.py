"""Publish completed object-only glass scenes as additive API collections."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from publish_venue_collections import versioned

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE/'catalog/glass-rollout/coffee'


def run(catalog):
    before=(catalog/'catalog.json').read_bytes()
    target=catalog/'guide-collections.json'
    data=json.loads(target.read_text())
    published=[];publication_reports=[]
    for folder in sorted(ROOT.iterdir()):
        review=folder/'review-status.json'
        if review.exists() and json.loads(review.read_text()).get('status')=='rejected':
            data['collections'].pop('coffee-guide-'+folder.name,None)
            continue
        if not (folder/'composite-browser-check.json').exists():continue
        spec=json.loads((folder/'scene-spec.json').read_text())
        browser=json.loads((folder/'composite-browser-check.json').read_text())
        checks=json.loads((folder/'view-overlay-checks.json').read_text())
        assert browser['status']==checks['status']=='passed'
        assert browser['overlay_sha256']==hashlib.sha256((folder/'view-overlay.png').read_bytes()).hexdigest()
        for name,sha in checks['files'].items():assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==sha
        key='coffee-guide-'+folder.name
        record=dict(id=key,title=spec['title'],venueKinds=spec.get('venue_kinds',['coffee']),revision=spec['revision'],
            ghostStyle=spec['ghost_style'],surfaceStyle=spec.get('surface_style'),existingGuidesReplaced=True,
            seconds=spec['duration_s'],animationSeconds=spec['duration_s'],status='reviewed-guide',
            scope=spec['scope'],rendering='native-clay-3d-glass',fullScriptSequenceComplete=False,
            alphaFactor=1,imageViewOpacity=.65,opacityAppliedIn='image_view',backgroundDelaySeconds=2,
            viewfinderEmbedded=False,viewfinderLayer='separate_ui',wallsEmbedded=False,floorEmbedded=False,
            ceilingEmbedded=False,sameSceneForBothVariants=True,colorResolution=spec['color_resolution'],
            ghostResolution=[405,720],composition=spec['composition'],lighting=spec['lighting'],mobile=spec['mobile'],
            phases=[],templateBindings=[dict(templateID=spec['template'],stepID=spec['step'],guideID=spec['guide'])])
        def files(row,source,prefix,scene=False):
            rows=[('overlay','view-overlay.png','sequences'),('poster','view-overlay-poster.png','sequences'),
                  ('strip','view-overlay-strip.jpg','sequences'),('video','color.mp4','sequences'),
                  ('colorPoster','color-poster.png','sequences'),('colorStrip','color-strip.jpg','sequences')]
            if scene:rows += [('blender','scene.blend','3d'),('sceneSpec','scene-spec.json','3d')]
            for field,name,kind in rows:row[field]=versioned(source/name,catalog,kind,prefix+'-'+name)
        files(record,folder,key,True)
        for phase in spec['exported_phases']:
            row=dict(id=phase['id'],seconds=phase['capture_seconds'],animationSeconds=phase['animation_seconds'],
                handoverSeconds=phase['handover_seconds'],nextPhaseID=phase['next_phase'],scope=phase['scope'],
                alphaFactor=1,imageViewOpacity=.65,opacityAppliedIn='image_view',backgroundDelaySeconds=2,
                viewfinderEmbedded=False,wallsEmbedded=False,floorEmbedded=False)
            files(row,folder/'phases'/phase['id'],key+'-'+phase['id']);record['phases'].append(row)
        if folder.name=='morning-pair':
            record['templateBindings'] += [dict(templateID='cafe-morning-ritual',stepID='pastry',guideID='pastry_tear_open'),
                dict(templateID='food-review-sweet',stepID='break',guideID='pastry_tear_open')]
        if spec.get('guide_bindings'):
            record['templateBindings']=[dict(templateID=b['template'],stepID=b['step'],guideID=b['guide'],phaseID=b['phase']) for b in spec['guide_bindings']]
        data['collections'][key]=record
        report=dict(status='published',id=key,endpoint='/v1/guide-collections/'+key,source_folder=str(folder))
        publication_reports.append((folder,report))
        published.append(key)
    temporary=target.with_suffix('.json.tmp');temporary.write_text(json.dumps(data,indent=2)+'\n');os.replace(temporary,target)
    # A ready marker must follow the atomic catalog update. Consumers can then
    # verify the collection immediately without racing its first publication.
    for folder,report in publication_reports:
        path=folder/'publication.json';temporary=path.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(report,indent=2)+'\n');os.replace(temporary,path)
    assert (catalog/'catalog.json').read_bytes()==before
    print(json.dumps(dict(status='published',collections=published,main_catalog_preserved=True)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args();run(args.out.resolve())
