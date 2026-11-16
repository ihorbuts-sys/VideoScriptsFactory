"""Check actual image opacity, delayed video playback and independent sights."""
import base64
import argparse
import hashlib
import io
import json
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import websocket
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parents[3] / 'catalog/coffee-hologram-study'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def run(url=None, embedded=False):
    with tempfile.TemporaryDirectory(prefix='loca-hologram-composite-') as profile:
        process = subprocess.Popen([CHROME, '--headless', '--disable-gpu', '--no-first-run',
            '--disable-background-networking', '--no-default-browser-check',
            '--remote-debugging-port=0',
            '--user-data-dir=' + profile, 'about:blank'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        connection = None
        try:
            port_file = Path(profile) / 'DevToolsActivePort'
            deadline = time.monotonic() + 15
            while not port_file.exists():
                assert time.monotonic() < deadline
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
                if embedded:
                    code = "(()=>{const document=window.frames[0]?.document;if(!document)return null;return eval(" + json.dumps(code) + ")})()"
                result = cdp('Runtime.evaluate', dict(expression=code, returnByValue=True))
                assert 'exceptionDetails' not in result, result
                return result['result'].get('value')

            def wait_for(code):
                deadline = time.monotonic() + 25
                while not evaluate(code):
                    assert time.monotonic() < deadline, code
                    time.sleep(.05)

            cdp('Page.enable')
            cdp('Runtime.enable')
            cdp('Emulation.setDeviceMetricsOverride', dict(width=1280, height=1200, deviceScaleFactor=1, mobile=False))
            target_url = url or (OUT / 'index.html').as_uri()
            cdp('Page.navigate', dict(url=target_url))
            if embedded:
                time.sleep(.5)
                # Same-origin sandboxed iframe approximates VS Code's embedded
                # browser; use normal autoplay policy and a real mouse click.
                cdp('Runtime.evaluate', dict(expression="document.body.innerHTML='';document.body.style.margin='0';const f=document.createElement('iframe');f.src=" + json.dumps(target_url) + ";f.setAttribute('sandbox','allow-scripts allow-same-origin');f.style='border:0;width:100vw;height:100vh';document.body.append(f)"))
            wait_for("Boolean(document.querySelector('#play'))")
            assert evaluate("document.querySelector('#color').paused && document.querySelector('#camera-background').paused")
            button = evaluate("(()=>{const r=document.querySelector('#play').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()")
            cdp('Input.dispatchMouseEvent', dict(type='mousePressed', button='left', clickCount=1, **button))
            cdp('Input.dispatchMouseEvent', dict(type='mouseReleased', button='left', clickCount=1, **button))
            wait_for("document.querySelector('#ghost-stage')?.dataset.ready==='true'")
            assert evaluate("getComputedStyle(document.querySelector('#ghost')).opacity") == '0.65'
            time.sleep(.6)
            assert evaluate("document.querySelector('#camera-background').paused && document.querySelector('#camera-background').currentTime===0")
            assert evaluate("document.querySelector('#color').currentTime>.3")
            wait_for("Boolean(document.querySelector('#camera-background').dataset.startedAt)")
            time.sleep(.5)
            timing = evaluate("(()=>{const s=document.querySelector('#ghost-stage'),v=document.querySelector('#camera-background'),r=document.querySelector('#color');return {start_delay_ms:Number(v.dataset.startedAt)-Number(s.dataset.guideStartedAt),playback_lag_s:r.currentTime-v.currentTime,background_time:v.currentTime}})()")
            assert 1950 <= timing['start_delay_ms'] < 2400, timing
            assert 1.75 < timing['playback_lag_s'] < 2.3, timing
            assert timing['background_time'] > .2
            evaluate("document.querySelector('#opacity').value=0;document.querySelector('#opacity').dispatchEvent(new Event('input'))")
            assert evaluate("getComputedStyle(document.querySelector('#ghost')).opacity") == '0'
            assert evaluate("getComputedStyle(document.querySelector('#viewfinder')).display!=='none' && getComputedStyle(document.querySelector('#viewfinder')).opacity==='1'")
            evaluate("document.querySelector('#viewfinder-toggle').click()")
            assert evaluate("getComputedStyle(document.querySelector('#viewfinder')).display==='none'")
            evaluate("document.querySelector('#viewfinder-toggle').click();document.querySelector('#opacity').value=100;document.querySelector('#opacity').dispatchEvent(new Event('input'))")
            assert evaluate("getComputedStyle(document.querySelector('#ghost')).opacity") == '1'
            surfaces = json.loads((OUT / 'view-overlay-checks.json').read_text())
            assert surfaces['phases'][0]['max_alpha'] == 255
            assert all(row['hero_core_median_alpha_at_100'] >= 245
                       for row in surfaces['opacity_100_sample_checks'])
            evaluate("document.querySelector('#opacity').value=65;document.querySelector('#opacity').dispatchEvent(new Event('input'))")
            evaluate("document.querySelector('#background').click()")
            assert evaluate("document.querySelector('#camera-background').hidden")
            evaluate("document.querySelector('#background').click()")
            phases = []
            target_config=evaluate('window.guideViewfinderTargets||null')
            target_checks=[]
            scene_spec=json.loads((OUT/'scene-spec.json').read_text())
            phase_ids=[row['id'] for row in scene_spec['exported_phases']]
            for phase in phase_ids:
                evaluate("document.querySelector('[data-phase=\"" + phase + "\"]').click()")
                wait_for("document.querySelector('#ghost-stage').dataset.ready==='true' && document.querySelector('#ghost').src.includes('/phases/" + phase + "/')")
                assert evaluate("document.querySelector('#camera-background').paused && document.querySelector('#camera-background').currentTime===0")
                phases.append(phase)
                if target_config:
                    overhead=any(w['phase']==phase for w in target_config['windows'])
                    wait_for("document.querySelector('#viewfinder text').textContent.includes('Y 90°')==="+str(overhead).lower())
                    target_checks.append(dict(phase=phase,overhead_target=overhead))
            if target_config:
                evaluate("document.querySelector('[data-phase=\"\"]').click()")
                wait_for("document.querySelector('#ghost-stage').dataset.ready==='true'")
                for window in target_config['windows']:
                    for sample,overhead in [(window['start']+.1,True),(window['end']+.1,False)]:
                        evaluate("document.querySelector('#ghost-stage').dataset.guideStartedAt=String(performance.now()-"+str(sample*1000)+")")
                        wait_for("document.querySelector('#viewfinder text').textContent.includes('Y 90°')==="+str(overhead).lower())
                        target_checks.append(dict(full_sequence_sample_seconds=sample,overhead_target=overhead))
            focus='extraction' if 'extraction' in phase_ids else phase_ids[-1]
            evaluate("document.querySelector('[data-phase=\""+focus+"\"]').click()")
            wait_for("document.querySelector('#ghost-stage').dataset.ready==='true' && document.querySelector('#ghost').src.includes('/phases/"+focus+"/')")
            # Compare the alignment view with the moving portion of the take.
            # Sampling at 4 and 5.2 seconds can compare two valid final holds.
            time.sleep(.8)
            # Hide the video so pixel movement can only come from the APNG.
            evaluate("document.querySelector('#background').click()")
            rect = evaluate("(()=>{document.querySelector('#ghost-stage').scrollIntoView({block:'center'});const r=document.querySelector('#ghost-stage').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()")
            def ghost_pixels():
                data = base64.b64decode(cdp('Page.captureScreenshot', dict(format='png'))['data'])
                image = Image.open(io.BytesIO(data)).convert('RGB')
                return np.array(image.crop((round(rect['x']),round(rect['y']),round(rect['x']+rect['width']),round(rect['y']+rect['height'])))).astype(float)
            first = ghost_pixels()
            time.sleep(1.8)
            change = float(np.abs(first-ghost_pixels()).mean())
            assert change > .1, ('Transparent guide is not animating', change)
            evaluate("document.querySelector('#background').click()")
            evaluate("document.querySelector('#stop').click()")
            assert evaluate("document.querySelector('#color').paused && document.querySelector('#camera-background').paused && document.querySelector('#ghost').src.includes('poster')")
            evaluate("document.querySelector('#play').click()")
            wait_for("document.querySelector('#ghost-stage').dataset.ready==='true'")
            time.sleep(2.5)
            assert evaluate("Array.from(document.images).every(im=>im.complete&&im.naturalWidth>0)")
            assert not errors, errors
            (OUT / 'composite-preview.png').write_bytes(base64.b64decode(cdp('Page.captureScreenshot', dict(format='png'))['data']))
            # Also check a phone-size layout without horizontal overflow.
            cdp('Emulation.setDeviceMetricsOverride', dict(width=390, height=844, deviceScaleFactor=1, mobile=True))
            assert evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth")
            report = dict(status='passed', actual_background_timing=timing,
                opacity_applied_to_image_only=True, separate_viewfinder=True,
                zero_opacity_keeps_viewfinder=True, viewfinder_toggle=True,
                opacity_100_shows_opaque_hero_surfaces=True,
                background_toggle=True, phase_restart_checks=phases,
                viewfinder_target_checks=target_checks,
                mobile_layout_no_horizontal_overflow=True, javascript_errors=errors,
                user_clicked_play=True, normal_autoplay_policy=True, embedded_frame=embedded,
                preview_url=target_url, apng_only_pixel_change=change,
                apng_motion_sample_seconds=[.8,2.6],stop_and_replay=True,
                overlay_sha256=hashlib.sha256((OUT / 'view-overlay.png').read_bytes()).hexdigest())
            (OUT / 'composite-browser-check.json').write_text(json.dumps(report, indent=2) + '\n')
            print(json.dumps(report))
        finally:
            if connection:
                connection.close()
            process.terminate()
            process.wait(timeout=10)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--embedded', action='store_true')
    parser.add_argument('--folder',type=Path)
    args = parser.parse_args()
    if args.folder:
        OUT=args.folder.resolve()
    run(args.url, args.embedded)
