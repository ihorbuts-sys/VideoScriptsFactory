"""Verify every released step picture through the actual authenticated HTTP API."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
import hashlib
import io
import json
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'http://127.0.0.1:8765'
TOKEN = Path('/Users/ihor.buts/Documents/Development/VideoEditorKit/tools/scriptwriter/.token').read_text().strip()


def request(path, auth=True):
    url = path if path.startswith('http') else BASE_URL + path
    headers = {'Authorization': 'Bearer ' + TOKEN} if auth else {}
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30)


def main():
    with request('/v1/health', False) as response:
        assert json.load(response)['ok']
    try:
        request('/v1/scripts', False)
    except urllib.error.HTTPError as error:
        assert error.code == 401
    else:
        raise AssertionError('Catalog authentication was bypassed')
    templates = []
    page = 0
    while page is not None:
        with request(f'/v1/scripts?page={page}&pageSize=100') as response:
            payload = json.load(response)
        templates.extend(payload['templates'])
        page = payload['nextPage']
    assert len(templates) == 56
    steps = [s for t in templates for s in t['steps']]
    assert len(steps) == 304

    def check(step):
        url = step['imageURL']
        path = urllib.parse.urlsplit(url).path
        name = Path(path).name
        expected = (ROOT / 'assets' / name).read_bytes()
        sha = hashlib.sha256(expected).hexdigest()
        assert path.endswith('/previews/' + sha[:16] + '/' + name), name
        with request(url) as response:
            assert response.status == 200
            assert response.headers['Content-Type'].split(';')[0] == 'image/jpeg', name
            data = response.read()
        assert hashlib.sha256(data).hexdigest() == sha, name
        with Image.open(io.BytesIO(data)) as image:
            assert image.size == (1080, 1920) and image.format == 'JPEG', name
            image.verify()
        return name

    with ThreadPoolExecutor(max_workers=4) as pool:
        checked = list(pool.map(check, steps))
    assert len(set(checked)) == 304
    report = dict(status='passed',scripts=56,step_images=304,authenticated_http=True,
                  all_images_http_200=True,all_images_match_export_hashes=True,
                  all_images_1080x1920_jpeg=True,all_urls_content_versioned=True)
    (ROOT / 'publication/live-api-check.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
