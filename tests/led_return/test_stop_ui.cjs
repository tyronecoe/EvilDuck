// Actual embedded control code in an isolated Node VM; no network/browser/HID.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const text=fs.readFileSync(process.argv[2],'utf8');
const code=text.split('// BEGIN STOP CONTROLS')[1].split('// END STOP CONTROLS')[0];
let checks=0,groups=0;function check(v){checks++;assert.ok(v);}
function env(fetch){const element={textContent:''};const calls=[];const context={document:{getElementById:()=>element},fetch:(u,o)=>{calls.push([u,o]);return fetch(u,o);},AbortController,setTimeout,clearTimeout,duckHeaders:()=>({'X-Duck-Password':'synthetic-only'}),refreshStatus:()=>{},log:m=>{element.textContent=m;}};vm.createContext(context);vm.runInContext(code,context);return {context,element,calls,run:s=>vm.runInContext(s,context)};}
const reply=(status,value)=>Promise.resolve({status,ok:status===200||status===202,json:async()=>value,text:async()=>typeof value==='object'?JSON.stringify(value):String(value)});
(async()=>{
 let e=env(()=>reply(202,{engine:'routeb',requestId:'42',wasOwned:true}));await e.run('stopScript()');check(e.calls[0][0]==='/stop'&&e.calls[0][1].method==='POST');check(e.calls[0][1].headers['X-Duck-Password']==='synthetic-only');check(e.element.textContent.includes('waiting'));groups++;
 e.run('observeStop({snapshotKind:"request-capture",routeBRequestId:"41",routeBPhase:0,routeBOwned:false,routeBReason:2})');check(e.element.textContent.includes('waiting'));
 e.run('observeStop({snapshotKind:"published-observation",routeBRequestId:"42",routeBPhase:0,routeBOwned:false,routeBReason:2})');check(e.element.textContent.includes('waiting'));groups++;
 e.run('observeStop({snapshotKind:"request-capture",routeBRequestId:"42",routeBPhase:0,routeBOwned:false,routeBReason:2})');check(e.element.textContent.includes('Stopped / Cancelled')&&e.element.textContent.includes('not proven'));groups++;
 for(const status of [401,409,500]){e=env(()=>reply(status,'denied'));await e.run('stopScript()');check(e.element.textContent.includes('STOP not confirmed')&&e.element.textContent.includes(String(status)));check(e.calls.length===1);}groups++;
 e=env(()=>Promise.reject(new Error('offline')));await e.run('stopScript()');check(e.element.textContent.includes('not confirmed'));check(e.calls.length===1);e.context.fetch=()=>reply(202,{engine:'routeb',wasOwned:false});await e.run('stopScript()');check(e.element.textContent.includes('No active'));groups++;
 let finish;e=env(()=>new Promise(r=>{finish=r;}));const pending=e.run('stopScript()');await e.run('stopScript()');check(e.calls.length===1);finish(await reply(202,{engine:'routeb',wasOwned:true,requestId:'5'}));await pending;groups++;
 e=env(()=>new Promise(r=>{finish=r;}));const run=e.run('runScript("safe.txt")');await e.run('runScript("safe.txt")');check(e.calls.length===1&&e.calls[0][0]==='/run?engine=routeb&s=safe.txt');finish(await reply(409,'busy'));await run;check(e.calls.length===1);groups++;
 e=env(()=>new Promise(()=>{}));e.context.setTimeout=(fn)=>setTimeout(fn,1);await e.run('stopScript()');check(e.element.textContent.includes('timed out')&&e.element.textContent.includes('not confirmed'));groups++;
 e=env(()=>Promise.resolve({status:202,ok:true,text:()=>new Promise(()=>{})}));e.context.setTimeout=(fn)=>setTimeout(fn,1);await e.run('stopScript()');check(e.element.textContent.includes('timed out')&&e.element.textContent.includes('not confirmed'));groups++;
 check(text.includes('position:sticky;top:0')&&text.includes('aria-live="polite"')&&text.includes('Programs already launched on the computer may keep running.'));groups++;
 console.log(JSON.stringify({PASS:groups,FAIL:0,assertions:checks,scope:'actual embedded JS with mocks; not native browser or hardware'}));
})().catch(e=>{console.error(e);process.exitCode=1;});
