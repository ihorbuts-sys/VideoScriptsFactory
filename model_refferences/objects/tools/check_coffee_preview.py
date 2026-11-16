"""Verify that the color video, ghost APNG and phase controls actually play."""
import base64
import hashlib
import argparse
import io
import json
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image
import websocket

OUT = Path(__file__).resolve().parents[3] / 'catalog/coffee-ordering'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def run():
    with tempfile.TemporaryDirectory(prefix='loca-coffee-browser-') as profile:
        process = subprocess.Popen([CHROME, '--headless', '--disable-gpu', '--no-first-run',
            '--disable-background-networking', '--no-default-browser-check',
            '--autoplay-policy=no-user-gesture-required', '--remote-debugging-port=0',
            '--user-data-dir=' + profile, 'about:blank'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        connection = None
        try:
            port_file = Path(profile) / 'DevToolsActivePort'
            deadline = time.monotonic() + 15
            while not port_file.exists():
                assert time.monotonic() < deadline, 'Chrome did not become ready'
                time.sleep(.1)
            port = port_file.read_text().splitlines()[0]
            targets = json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json'))
            target = next(t for t in targets if t['type'] == 'page')
            connection = websocket.create_connection(target['webSocketDebuggerUrl'], suppress_origin=True, timeout=20)
            serial = 0
            errors = []

            def cdp(method, params=None):
                nonlocal serial
                serial += 1
                connection.send(json.dumps(dict(id=serial, method=method, params=params or {})))
                while True:
                    reply = json.loads(connection.recv())
                    if reply.get('method') == 'Runtime.exceptionThrown':
                        errors.append(reply['params'])
                    if reply.get('id') == serial:
                        assert 'error' not in reply, reply
                        return reply.get('result', {})

            def evaluate(code):
                result = cdp('Runtime.evaluate', dict(expression=code, returnByValue=True))
                assert 'exceptionDetails' not in result, result
                return result['result'].get('value')

            def wait_for(code):
                deadline = time.monotonic() + 20
                while not evaluate(code):
                    assert time.monotonic() < deadline, code
                    time.sleep(.1)

            def capture():
                rect = evaluate("(()=>{const r=document.querySelector('#ghost-stage').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()")
                data = cdp('Page.captureScreenshot', dict(format='png'))['data']
                shot = Image.open(io.BytesIO(base64.b64decode(data))).convert('RGB')
                x, y = round(rect['x']), round(rect['y'])
                return np.asarray(shot.crop((x, y, x + round(rect['width']), y + round(rect['height']))), dtype=float)

            cdp('Page.enable')
            cdp('Runtime.enable')
            cdp('Emulation.setDeviceMetricsOverride', dict(width=1280, height=1200, deviceScaleFactor=1, mobile=False))
            cdp('Page.navigate', dict(url=(OUT / 'index.html').as_uri()))
            wait_for("document.readyState==='complete' && document.querySelector('#color').readyState>=2 && document.querySelector('#ghost').naturalWidth===405")
            assert evaluate("document.querySelector('#color').duration") == 16
            evaluate("document.querySelector('#ghost').scrollIntoView({block:'center'})")
            time.sleep(.5)
            first = capture()
            start = evaluate("document.querySelector('#color').currentTime")
            time.sleep(1.7)
            later = capture()
            end = evaluate("document.querySelector('#color').currentTime")
            difference = float(np.abs(first - later).mean())
            assert difference > .15, ('Ghost is static', difference)
            assert end > start + .5, ('Color video is static', start, end)
            phase_checks = []
            for phase in ['order', 'extraction', 'cup-detail']:
                evaluate("document.querySelector('[data-phase=\"" + phase + "\"]').click()")
                wait_for("document.querySelector('#color').readyState>=2 && document.querySelector('#color').currentSrc.includes('/phases/" + phase + "/') && document.querySelector('#ghost').complete")
                assert evaluate("document.querySelector('#ghost').naturalWidth") == 405
                duration = evaluate("document.querySelector('#color').duration")
                assert duration > 3
                assert evaluate("document.querySelector('#color').error===null")
                phase_checks.append(dict(id=phase, duration_s=duration))
            evaluate("document.querySelector('#background').click()")
            assert evaluate("document.querySelector('#ghost-stage').classList.contains('dark')")
            assert evaluate("Array.from(document.images).every(im=>im.complete&&im.naturalWidth>0)")
            assert not errors, errors
            report = dict(status='passed', color_video_advances=True, ghost_apng_advances=True,
                ghost_sha256=hashlib.sha256((OUT / 'ghost.png').read_bytes()).hexdigest(),
                mean_ghost_pixel_change=difference, no_missing_images=True, javascript_errors=errors,
                phase_controls=phase_checks, background_toggle=True)
            (OUT / 'browser-check.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(report))
        finally:
            if connection:
                connection.close()
            process.terminate()
            process.wait(timeout=10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type=Path)
    args = parser.parse_args()
    if args.folder:
        OUT = args.folder.resolve()
    run()
