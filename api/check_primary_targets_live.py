"""Verify the live standalone target index, formats, previews and asset hashes."""
import argparse
import hashlib
import json
import urllib.request
import urllib.error
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
ROOT=BASE/'model_refferences/tripo-cli/primary-targets-2026-10-29'


def run(server):
    token=(server/'.token').read_text().strip();host='http://127.0.0.1:8765'
    def get(path):
        request=urllib.request.Request(host+path,headers={'Authorization':'Bearer '+token})
        with urllib.request.urlopen(request,timeout=30) as response:return json.load(response)
    index=json.loads((server/'catalog/guide-objects.json').read_text())['objects']
    page=get('/v1/guide-objects?pageSize=5');assert page['total']==16 and len(page['objects'])==5 and page['nextPage']==1
    records=get('/v1/guide-objects?pageSize=100')['objects'];assert {r['id'] for r in records}==set(index)
    food=get('/v1/guide-objects?category=food');assert food['total']==5
    assert get('/v1/guide-objects?category=not-a-category')['total']==0
    count=byte_count=0;ids=[]
    for row in records:
        detail=get('/v1/guide-objects/'+row['id']);assert detail==row
        assert row['primaryTarget'] and row['staticComponent'] and not row['animationEmbedded']
        assert row['units']=='metres' and row['coordinateSystem']=='Y up'
        assert not row['lidarRegistrationVerified'] and not row['metricScan']
        assert row['previewAlphaFactor']==1 and row['previewImageViewOpacity']==.65
        assert row['anchors']['placement']['positionM'][1]==0
        assert len(row['views'])==6 and all(row['dimensionsM'])
        for key,asset in row['assets'].items():
            sha=hashlib.sha256()
            with urllib.request.urlopen(asset['url'],timeout=60) as response:
                mime=response.headers.get_content_type()
                if key.endswith('USDZ'):assert mime=='model/vnd.usdz+zip'
                if key in ['model','geometryProxy']:assert mime=='model/gltf-binary'
                data=response.read();sha.update(data);byte_count+=len(data)
            assert sha.hexdigest()==asset['sha256'] and len(data)==asset['bytes'],(row['id'],key)
            count+=1
        for view in row['views']:
            with urllib.request.urlopen(view['url'],timeout=30) as response:data=response.read()
            assert hashlib.sha256(data).hexdigest()==view['sha256'] and data[:8]==b'\x89PNG\r\n\x1a\n'
            count+=1;byte_count+=len(data)
        ids.append(row['id'])
    try:get('/v1/guide-objects/not-an-object')
    except urllib.error.HTTPError as error:assert error.code==404
    else:raise AssertionError('Unknown object must return 404')
    assert get('/v1/guides?pageSize=1')['total']==178
    publication=json.loads((ROOT/'publication.json').read_text())
    catalog_sha=hashlib.sha256((server/'catalog/catalog.json').read_bytes()).hexdigest()
    assert catalog_sha==publication['prior_catalog_sha256']
    report=dict(status='passed',objects=16,downloaded_assets=count,downloaded_bytes=byte_count,
        ids=ids,pagination=True,category_filter=True,detail_routes=True,unknown_id_404=True,
        glb_mime_correct=True,usdz_mime_correct=True,all_asset_hashes_verified=True,
        existing_178_guides_preserved=True,script_and_guide_catalog_sha256=catalog_sha)
    (ROOT/'live-api-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--server',type=Path,required=True);args=parser.parse_args();run(args.server.resolve())
