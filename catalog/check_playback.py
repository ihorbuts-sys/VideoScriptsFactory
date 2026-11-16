"""Verify actual APNG playback and controls in an isolated local Chrome session."""
import base64
import argparse
import io
import json
import os
import signal
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image
import websocket

HERE=Path(__file__).resolve().parent
CHECKS=HERE/'checks'
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--guide',default='burger_low_in_mc')
    guide_id=parser.parse_args().guide
    ready_count=json.loads((HERE/'animations/index.json').read_text())['count']
    CHECKS.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='loca-playback-') as profile:
        process=subprocess.Popen([CHROME,'--headless','--disable-gpu','--no-first-run',
                                  '--disable-background-networking','--no-default-browser-check',
                                  '--remote-debugging-port=0',f'--user-data-dir={profile}','about:blank'],
                                 stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        connection=None
        try:
            port_file=Path(profile)/'DevToolsActivePort'
            deadline=time.monotonic()+15
            while not port_file.exists():
                if time.monotonic()>deadline:raise RuntimeError('Chrome debugging port was not ready')
                time.sleep(.1)
            port=port_file.read_text().splitlines()[0]
            targets=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json'))
            target=next(item for item in targets if item['type']=='page')
            connection=websocket.create_connection(target['webSocketDebuggerUrl'],suppress_origin=True,timeout=15)
            serial=0;exceptions=[]
            def cdp(method,params=None):
                nonlocal serial
                serial+=1;request_id=serial
                connection.send(json.dumps(dict(id=request_id,method=method,params=params or {})))
                while True:
                    reply=json.loads(connection.recv())
                    if reply.get('method')=='Runtime.exceptionThrown':exceptions.append(reply['params'])
                    if reply.get('id')==request_id:
                        if 'error' in reply:raise RuntimeError(reply['error'])
                        return reply.get('result',{})
            def evaluate(expression):
                result=cdp('Runtime.evaluate',dict(expression=expression,returnByValue=True))
                if 'exceptionDetails' in result:raise RuntimeError(result['exceptionDetails'])
                return result['result'].get('value')
            def wait_for(expression):
                deadline=time.monotonic()+15
                while not evaluate(expression):
                    if time.monotonic()>deadline:raise RuntimeError('Browser condition timed out: '+expression)
                    time.sleep(.1)
            def capture(name):
                rect=evaluate("(()=>{const r=document.querySelector('.guide:not([hidden]) .motion-stage').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()")
                # Capture the existing viewport without resizing it. Enlarging
                # the viewport for a clip can trigger IntersectionObserver and
                # restart a just-visible APNG during the screenshot itself.
                encoded=cdp('Page.captureScreenshot',dict(format='png',captureBeyondViewport=False))['data']
                screen=Image.open(io.BytesIO(base64.b64decode(encoded))).convert('RGB')
                x,y=round(rect['x']),round(rect['y']);assert y>=0 and y+rect['height']<=screen.height,rect
                stage=screen.crop((x,y,x+round(rect['width']),y+round(rect['height'])))
                stage.save(CHECKS/name)
                return np.asarray(stage,dtype=float)
            cdp('Runtime.enable');cdp('Page.enable')
            cdp('Emulation.setDeviceMetricsOverride',dict(width=1280,height=1000,deviceScaleFactor=1,mobile=False))
            cdp('Page.navigate',dict(url=(HERE/'animations.html').as_uri()+'#'+guide_id))
            wait_for("document.readyState==='complete' && document.querySelector('.guide:not([hidden]) .motion-image')?.naturalWidth===405")
            counts=evaluate("({total:document.querySelectorAll('.guide').length,watercolor:document.querySelectorAll('.guide[data-new=true]').length,visible:document.querySelectorAll('.guide:not([hidden])').length})")
            assert counts==dict(total=178,watercolor=ready_count,visible=1),counts
            evaluate("document.querySelector('.guide:not([hidden]) .motion-stage').scrollIntoView({block:'center'})")
            # Reset after layout settles, then compare pixels before and during orbit.
            time.sleep(.2)
            evaluate("document.querySelector('.guide:not([hidden]) [data-play]').click()")
            time.sleep(.4);first=capture('animation-start.png')
            time.sleep(1.8);moving=capture('animation-moving.png')
            difference=float(np.abs(first-moving).mean())
            assert difference>.1,('APNG did not visibly advance',difference)
            evaluate("document.querySelector('.guide:not([hidden]) [data-pause]').click()")
            time.sleep(.25);held=capture('animation-held.png')
            time.sleep(1.2);held_later=capture('animation-held-later.png')
            assert np.array_equal(held,held_later),'Starting pose did not remain still'
            evaluate("document.querySelector('.guide:not([hidden]) [data-play]').click()")
            assert evaluate("document.querySelector('.guide:not([hidden]) .motion-card').dataset.playing==='true'")
            cdp('Page.navigate',dict(url=(HERE/'catalog.html').as_uri()))
            wait_for("document.readyState==='complete'")
            assert evaluate("document.querySelectorAll('.motion-card').length")==304
            assert not exceptions,exceptions
            report=dict(guides=178,watercolor_previews=ready_count,script_step_players=304,checked_guide=guide_id,
                        browser='Google Chrome headless',actual_playback_pixel_difference=difference,
                        starting_pose_holds=True,replay_works=True,javascript_exceptions=exceptions)
            (HERE/'playback-check.json').write_text(json.dumps(report,indent=2)+'\n')
            print(json.dumps(report))
        finally:
            if connection:connection.close()
            os.killpg(process.pid,signal.SIGTERM)
            process.wait(timeout=10)


if __name__=='__main__':main()
