"""Verify real video/APNG playback in isolated headless Chrome, without launching Blender."""
import base64,io,json,os,signal,subprocess,tempfile,time,urllib.request
from pathlib import Path
import numpy as np
from PIL import Image
import websocket
BASE=Path(__file__).resolve().parents[3]
CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

def main():
    folder=BASE/'catalog/clay-scenes/bar_low_truckr_mm'
    with tempfile.TemporaryDirectory(prefix='loca-clay-review-') as profile:
        process=subprocess.Popen([CHROME,'--headless','--disable-gpu','--no-first-run',
            '--disable-background-networking','--remote-debugging-port=0',f'--user-data-dir={profile}','about:blank'],
            stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
        connection=None
        try:
            deadline=time.monotonic()+20;port_file=Path(profile)/'DevToolsActivePort'
            while not port_file.exists():
                if time.monotonic()>deadline:raise RuntimeError('Chrome did not start')
                time.sleep(.1)
            port=port_file.read_text().splitlines()[0];targets=json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json'))
            connection=websocket.create_connection(next(t for t in targets if t['type']=='page')['webSocketDebuggerUrl'],suppress_origin=True,timeout=20)
            serial=0;exceptions=[]
            def cdp(method,params=None):
                nonlocal serial
                serial+=1;rid=serial;connection.send(json.dumps(dict(id=rid,method=method,params=params or {})))
                while True:
                    r=json.loads(connection.recv())
                    if r.get('method')=='Runtime.exceptionThrown':exceptions.append(r['params'])
                    if r.get('id')==rid:
                        if 'error' in r:raise RuntimeError(r['error'])
                        return r.get('result',{})
            def evaluate(expression):
                r=cdp('Runtime.evaluate',dict(expression=expression,returnByValue=True))
                if 'exceptionDetails' in r:raise RuntimeError(r['exceptionDetails'])
                return r['result'].get('value')
            def ready(expression):
                deadline=time.monotonic()+25
                while not evaluate(expression):
                    if time.monotonic()>deadline:raise RuntimeError('Browser condition timed out')
                    time.sleep(.1)
            def screenshot(name):
                raw=base64.b64decode(cdp('Page.captureScreenshot',dict(format='png'))['data']);(folder/name).write_bytes(raw)
                return np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),dtype=np.float32)
            cdp('Runtime.enable');cdp('Page.enable');cdp('Emulation.setDeviceMetricsOverride',dict(width=1280,height=1100,deviceScaleFactor=1,mobile=False))
            cdp('Page.navigate',dict(url=(folder/'index.html').as_uri()))
            ready("document.readyState==='complete' && document.querySelector('video')?.readyState>=2 && [...document.images].every(i=>i.complete&&i.naturalWidth>0)")
            evaluate("replayBoth();document.querySelector('.ghost').style.background='#23313b'")
            time.sleep(.5);start=screenshot('browser-start.png');first_time=evaluate("document.querySelector('video').currentTime")
            time.sleep(6);moving=screenshot('browser-moving.png');later_time=evaluate("document.querySelector('video').currentTime")
            difference=float(np.abs(start-moving).mean());assert difference>.2
            assert later_time>first_time+4,'Color video did not play'
            evaluate("document.querySelector('video').pause();document.querySelector('.ghost').style.background='#f7f2e7'")
            screenshot('browser-light.png')
            cdp('Page.navigate',dict(url=(BASE/'catalog/animations.html').as_uri()+'#bar_low_truckr_mm'))
            ready("document.readyState==='complete' && document.querySelector('#bar_low_truckr_mm .motion-image')?.naturalWidth===540")
            assert evaluate("document.querySelector('#bar_low_truckr_mm .motion-image').dataset.animation.includes('clay-scenes/bar_low_truckr_mm/ghost.png')")
            evaluate("document.querySelector('#bar_low_truckr_mm [data-pause]').click()")
            assert evaluate("document.querySelector('#bar_low_truckr_mm .motion-card').dataset.playing==='false'")
            evaluate("document.querySelector('#bar_low_truckr_mm [data-play]').click()")
            assert evaluate("document.querySelector('#bar_low_truckr_mm .motion-card').dataset.playing==='true'")
            assert not exceptions
            report=dict(status='passed',browser='Chrome headless',paired_page_no_missing_images=True,
                video_time_advanced_s=later_time-first_time,animation_pixel_difference=difference,
                main_gallery_points_to_new_render=True,replay_and_starting_pose_controls=True,javascript_exceptions=exceptions)
            (folder/'browser-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
        finally:
            if connection:connection.close()
            os.killpg(process.pid,signal.SIGTERM);process.wait(timeout=10)

if __name__=='__main__':main()
