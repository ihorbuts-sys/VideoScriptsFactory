"""Exercise additive collection routes without changing the running service."""
import argparse
import json
import shutil
import tempfile
import threading
import types
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path


def run(server_dir):
    staged = Path(__file__).with_name('shared-collections-server.py')
    module = types.ModuleType('loca_collection_route_check')
    module.__file__ = str(server_dir / 'server.py')
    exec(compile(staged.read_text(), str(staged), 'exec'), module.__dict__)
    token = 'temporary-local-route-check'
    module.Handler.token = token
    with tempfile.TemporaryDirectory(prefix='loca-collection-check-') as tmp:
        folder = Path(tmp)
        shutil.copy2(server_dir / 'catalog/catalog.json', folder / 'catalog.json')
        (folder / 'sequences').mkdir()
        (folder / 'sequences/proof.png').write_bytes(b'collection-file-content')
        phase = dict(id='extraction', video='sequences/proof.png', overlay='sequences/proof.png')
        record = dict(id='coffee-ordering', venueKinds=['coffee'], alphaFactor=.65,
                      video='sequences/proof.png', overlay='sequences/proof.png', phases=[phase])
        (folder / 'guide-collections.json').write_text(json.dumps(dict(collections={'coffee-ordering': record})))
        module.CATALOG_DIR = str(folder)
        server = ThreadingHTTPServer(('127.0.0.1', 0), module.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)

        def request(path, auth=True, expected=200, json_body=True):
            headers = {'Authorization': 'Bearer ' + token} if auth else {}
            try:
                response = urllib.request.urlopen(urllib.request.Request(base + path, headers=headers))
            except urllib.error.HTTPError as error:
                response = error
            with response:
                assert response.status == expected, (path, response.status, expected)
                body = response.read()
                return json.loads(body) if json_body else body

        try:
            request('/v1/guide-collections', auth=False, expected=401)
            listing = request('/v1/guide-collections?venueKind=coffee&pageSize=1')
            assert listing['total'] == 1 and len(listing['collections']) == 1
            assert request('/v1/guide-collections?venueKind=bakery')['total'] == 0
            assert request('/v1/guide-collections?page=1&pageSize=1')['collections'] == []
            item = request('/v1/guide-collections/coffee-ordering')
            assert item['alphaFactor'] == .65 and 'colorVideoURL' in item
            assert 'video' not in item and 'overlayURL' in item
            phase_item = request('/v1/guide-collections/coffee-ordering/phases/extraction')
            assert phase_item['id'] == 'extraction' and 'colorVideoURL' in phase_item
            request('/v1/guide-collections/unknown', expected=404)
            request('/v1/guide-collections/coffee-ordering/phases/unknown', expected=404)
            asset_path = item['overlayURL'].removeprefix(base)
            assert request(asset_path, auth=False, json_body=False) == b'collection-file-content'
            request('/v1/files/sequences/proof.png', auth=False, expected=401)
            guides = request('/v1/guides?pageSize=2')
            assert guides['total'] == 178 and len(guides['guides']) == 2
            request('/v1/health', auth=False)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
    report = dict(status='passed', authenticated_collection_routes=True,
        file_authorization_preserved=True, phase_routes=True, pagination=True,
        kind_filter=True, unknown_ids_404=True, existing_guides=178,
        existing_catalog_changed=False, running_service_changed=False)
    staged.with_name('shared-collections-route-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('server_dir', type=Path)
    run(parser.parse_args().server_dir)
