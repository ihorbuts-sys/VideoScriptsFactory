/* Actual Chrome APNG playback checks. Node 22+; no browser dependencies. */
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../..'),output=path.join(root,'catalog/p0/people-browser');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'catalog/p0/players.json')));
const allRecords=manifest.guides.filter(r=>r.filmingMode);
const selected=process.argv.slice(2),records=allRecords.filter(r=>!selected.length||selected.includes(r.id));fs.mkdirSync(output,{recursive:true});
const profile=fs.mkdtempSync('/private/tmp/loca-people-chrome-');
const chrome=spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',[
  '--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check',
  '--remote-debugging-port=0','--user-data-dir='+profile,'about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));let socket;
(async()=>{try{
  const portFile=path.join(profile,'DevToolsActivePort');
  for(let i=0;i<100&&!fs.existsSync(portFile);i++)await sleep(100);
  const port=fs.readFileSync(portFile,'utf8').split('\n')[0];
  const target=await(await fetch(`http://127.0.0.1:${port}/json/new?about:blank`,{method:'PUT'})).json();
  socket=new WebSocket(target.webSocketDebuggerUrl);await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j});
  let serial=0;const pending=new Map();socket.onmessage=event=>{const m=JSON.parse(event.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result)}};
  const call=(method,params={})=>new Promise((resolve,reject)=>{const id=++serial;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}))});
  const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value};
  await call('Page.enable');await call('Emulation.setDeviceMetricsOverride',{width:1280,height:1000,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:'http://127.0.0.1:8766/p0/index.html'});
  for(let i=0;i<100;i++){if(await evaluate("document.querySelectorAll('article').length===37"))break;await sleep(100)}
  const results=[];
  for(const r of records){
    const id=JSON.stringify(r.id);
    const frame=async name=>{
      const clip=await evaluate(`(()=>{const r=document.getElementById(${id}).querySelector('.stage').getBoundingClientRect();return {x:r.x+scrollX,y:r.y+scrollY,width:r.width,height:r.height,scale:1}})()`);
      const shot=await call('Page.captureScreenshot',{format:'png',clip,captureBeyondViewport:true});
      fs.writeFileSync(path.join(output,r.id+'-'+name+'.png'),Buffer.from(shot.data,'base64'));
    };
    await evaluate(`(()=>{const c=document.getElementById(${id});c.scrollIntoView({block:'center'});c.querySelectorAll('button')[1].click();return true})()`);await sleep(200);await frame('before');
    await evaluate(`document.getElementById(${id}).querySelector('button').click()`);await sleep(2700);await frame('middle');
    await sleep(Math.max(0,r.seconds*1000-2700+450));await frame('after');
    const state=await evaluate(`(()=>{const c=document.getElementById(${id}),i=c.querySelector('img');return {loaded:i.complete&&i.naturalWidth===405,playing:c.dataset.playing,opacity:getComputedStyle(i).opacity,sourceCurrent:i.src.includes(${JSON.stringify(r.sha256.slice(0,12))}),mode:c.textContent.includes(${JSON.stringify(r.filmingMode==='selfie'?'Front camera':'Filmed by a friend')})}})()`);
    if(!state.loaded||state.playing!=='false'||state.opacity!=='0.65'||!state.sourceCurrent||!state.mode)throw new Error(r.id+' '+JSON.stringify(state));
    results.push({id:r.id,sha256:r.sha256,...state});console.log('BROWSER_PLAYED',r.id);
  }
  await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await sleep(150);
  const mobile=await evaluate('({width:innerWidth,content:document.documentElement.scrollWidth,missing:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length})');
  if(mobile.content>mobile.width||mobile.missing)throw new Error(JSON.stringify(mobile));
  const reportFile=path.join(root,'catalog/p0/people-browser-checks.json');
  const previous=selected.length&&fs.existsSync(reportFile)?JSON.parse(fs.readFileSync(reportFile)).records:[];
  const merged=new Map(previous.map(r=>[r.id,r]));for(const r of results)merged.set(r.id,r);
  fs.writeFileSync(reportFile,JSON.stringify({status:'browser_played',records:[...merged.values()],mobile,pixel_comparison_pending:true},null,2)+'\n');
}finally{if(socket)socket.close();chrome.kill('SIGTERM');await sleep(300);fs.rmSync(profile,{recursive:true,force:true})}})().catch(e=>{console.error(e);process.exitCode=1});
