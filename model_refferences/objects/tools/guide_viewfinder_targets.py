"""Add an overhead pitch target to the separate preview UI at the relevant phase."""
import json,re
from pathlib import Path


def apply(folder:Path,duration:float,overhead_windows:list):
    path=folder/'index.html';text=path.read_text()
    text=re.sub(r'<script id="overhead-viewfinder-targets">.*?</script>\s*','',text,flags=re.S)
    config=json.dumps(dict(duration=duration,windows=overhead_windows))
    script='''<script id="overhead-viewfinder-targets">
(()=>{
 const config=CONFIG;
 const finder=document.querySelector('#viewfinder'),label=finder.querySelector('text');
 window.guideViewfinderTargets=config;
 function update(){
  const started=Number(stage.dataset.guideStartedAt);
  const elapsed=stage.dataset.ready==='true'&&Number.isFinite(started)?Math.max(0,(performance.now()-started)/1000)%config.duration:0;
  const overhead=config.windows.some(w=>currentPhase?w.phase===currentPhase:elapsed>=w.start&&elapsed<w.end);
  label.textContent=overhead?'X 0° / Y 90°':'X 0°';
  finder.setAttribute('aria-label',overhead?'Viewfinder with X horizon and Y down-angle targets':'Viewfinder with X horizon level');
  requestAnimationFrame(update);
 }
 update();
})();
</script>
'''.replace('CONFIG',config)
    path.write_text(text.replace('</body>',script+'</body>'))
