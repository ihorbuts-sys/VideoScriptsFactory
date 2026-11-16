"""Publish reviewed standalone targets without replacing script or guide assets."""
import argparse
import hashlib
import json
import os
from pathlib import Path

from publish_venue_collections import versioned

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE/'model_refferences/tripo-cli/primary-targets-2026-10-29'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def run(catalog):
    before=digest(catalog/'catalog.json')
    plan=json.loads((ROOT/'plan.json').read_text())
    checks=json.loads((ROOT/'export-roundtrip.json').read_text())
    assert checks['status']=='passed' and checks['objects']==16 and checks['files']==64
    reviews=json.loads((ROOT/'visual-review.json').read_text())
    records={}
    names={'model':'model.glb','modelUSDZ':'model.usdz','geometryProxy':'geometry-proxy.glb',
        'geometryProxyUSDZ':'geometry-proxy.usdz','poster':'rendered/preview.png',
        'ghostPreview':'ghost-preview.png','metadata':'component.json',
        'blender':'model.blend','assetBlend':'asset.blend'}
    for row in plan['objects']:
        aid=row['id'];folder=BASE/'model_refferences/objects'/aid/'tripo-generated/review'
        assert reviews['objects'][aid]['status']=='reviewed_for_component_reuse'
        component=json.loads((folder/'component.json').read_text())
        for name,info in component['files'].items():assert digest(folder/name)==info['sha256'],(aid,name)
        record=dict(id=aid,title=aid.replace('_',' ').title(),category=row['category'],primaryTarget=True,
            independentlyPlaceable=True,staticComponent=True,animationEmbedded=False,units='metres',
            coordinateSystem='Y up',dimensionsM=component['actual_dimensions_gltf_m'],
            boundsM=component['bounds_gltf_m'],anchors={name:{'positionM':anchor['position_gltf_m'],'kind':anchor['kind'],'gltfNodeName':anchor.get('gltf_node_name')} for name,anchor in component['anchors'].items()},
            geometryProxy=component['geometry_proxy'],registrationMode=component['registration_mode'],
            lidarRegistrationVerified=False,metricScan=False,source='Tripo v3.1 from built-in imagegen references',
            sourcePreserved=True,previewAlphaFactor=1,previewImageViewOpacity=.65,
            modelMaterial='full_color',proxyMaterial='neutral',canUseRuntimeGhostMaterial=True,
            candidateGuideIDs=row['guide_candidates'],assets={},views=[])
        for key,name in names.items():
            relative=versioned(folder/name,catalog,'3d','object-'+aid+'-'+Path(name).name)
            record['assets'][key]=dict(path=relative,sha256=digest(folder/name),bytes=(folder/name).stat().st_size)
        for view in ['front','back','left','right','top','bottom']:
            source=folder/'rendered'/(view+'.png')
            relative=versioned(source,catalog,'3d','object-'+aid+'-'+view+'.png')
            record['views'].append(dict(name=view,path=relative,sha256=digest(source)))
        records[aid]=record
    existing=catalog/'guide-objects.json'
    data=json.loads(existing.read_text()) if existing.exists() else dict(version=1,objects={})
    data['objects'].update(records)
    temporary=existing.with_suffix('.json.tmp');temporary.write_text(json.dumps(data,indent=2)+'\n');os.replace(temporary,existing)
    assert digest(catalog/'catalog.json')==before
    report=dict(status='published',objects=16,ids=list(records),catalog_preserved=True,
        prior_catalog_sha256=before,endpoint='/v1/guide-objects',motion_assets_replaced=False,
        total_generation_credits=sum(r['actual_credits'] for r in plan['objects']))
    (ROOT/'publication.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--catalog',type=Path,required=True);args=parser.parse_args();run(args.catalog.resolve())
