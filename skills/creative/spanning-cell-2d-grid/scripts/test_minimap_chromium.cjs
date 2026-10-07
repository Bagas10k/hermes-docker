'use strict';
// NODE_PATH=<existing node_modules> node scripts/test_minimap_chromium.cjs
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = execFileSync('python3', ['-c', `from branch_history import BranchHistory
from history_browser import render
h=BranchHistory({})
for b in 'bcdefg':
 h.commit(b,'root',{})
 parent=b
 for i in range(12):
  child=b+str(i); h.commit(child,parent,{}); parent=child
print(render(h))`], {cwd:__dirname, encoding:'utf8'});
const evidence = {kind:'real Chromium / Playwright mouse', records:[], errors:[]};
const clipboard = {kind:'controlled clipboard promises, execCommand and timers / real Chromium DOM (not OS clipboard)', records:[]};
const clipboardChecks = require('./clipboard_checks.cjs');
const lifecycle = {kind:'native ResizeObserver + instrumented callback replay / Chromium', records:[]};
// Instrument ownership, but retain native observation and native event dispatch.
function instrumentLifecycle() {
 const audit = window.minimapAudit = {observers:[], listeners:[], resizeEvents:0, scrollEvents:0,collecting:true};
 const Native = window.ResizeObserver;
 window.ResizeObserver = class {
  constructor(callback) {
   this.callback=callback; this.targets=[]; this.disconnects=0; this.deliveries=0;
   this.native=new Native(entries=>{this.deliveries++; callback(entries,this);});
   audit.observers.push(this);
  }
  observe(target) {this.targets.push(target.id); this.native.observe(target);}
  disconnect() {this.disconnects++; this.native.disconnect();}
 };
 const add=EventTarget.prototype.addEventListener, remove=EventTarget.prototype.removeEventListener;
 add.call(window,'resize',()=>audit.resizeEvents++);
 EventTarget.prototype.addEventListener=function(type,callback,options) {
  if (audit.collecting && ((this===window && ['mousemove','mouseup','blur','resize'].includes(type)) ||
      (this.id==='dag-view' && type==='scroll') || this.closest?.('#dag-minimap-wrap'))) {
   audit.listeners.push({target:this,type,callback,removed:0});
  }
  if (this.id==='dag-view' && type==='scroll') add.call(this,'scroll',()=>audit.scrollEvents++);
  return add.call(this,type,callback,options);
 };
 EventTarget.prototype.removeEventListener=function(type,callback,options) {
  const item=audit.listeners.find(x=>x.target===this && x.type===type && x.callback===callback);
  if (item) item.removed++;
  return remove.call(this,type,callback,options);
 };
}
async function checkLifecycle(page,width) {
 // Fresh idle document: no auto-center animation or drag can mask observer work.
 await page.setContent(html.replace('<script>'+"'use strict';", '<script>('+instrumentLifecycle.toString()+')();</script><script>'+"'use strict';").replace('</script></html>','</script><script>minimapAudit.collecting=false;</script></html>'));
 await page.waitForFunction(()=>window.minimapAudit?.observers[0]?.deliveries>0);
 await page.evaluate(async()=>{
  minimapAudit.collecting=false; // Exclude later Playwright-injected mouse listeners.
  document.querySelector('#dag-view').scrollTo({left:0,behavior:'instant'});
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
 });
 const initial=await page.evaluate(()=>({client:document.querySelector('#dag-view').clientWidth,
  resize:minimapAudit.resizeEvents,scroll:minimapAudit.scrollEvents,deliveries:minimapAudit.observers[0].deliveries}));
 const sizes=[];
 for (const factor of [.55,.85]) {
  await page.evaluate(size=>{document.querySelector('#dag-view').style.width=size+'px';},Math.floor(initial.client*factor));
  await page.waitForFunction(()=>{
   const v=document.querySelector('#dag-view'),m=document.querySelector('.dag-minimap-svg');
   return Math.abs(historyPreview.minimapFrameBounds().width-180*v.clientWidth/+m.dataset.worldWidth)<.06;
  });
  const s=await page.evaluate(()=>{
   const v=document.querySelector('#dag-view'),m=document.querySelector('.dag-minimap-svg'),f=document.querySelector('#minimap-viewport-frame');
   const r=m.getBoundingClientRect(),fr=f.getBoundingClientRect();
   return {client:v.clientWidth,world:+m.dataset.worldWidth,scroll:v.scrollLeft,units:historyPreview.minimapFrameBounds(),
    screenWidth:fr.width,mapWidth:r.width,screenX:fr.x-r.x,resize:minimapAudit.resizeEvents,scrollEvents:minimapAudit.scrollEvents,deliveries:minimapAudit.observers[0].deliveries};
  });
  assert.notEqual(s.client,initial.client); assert.equal(s.resize,initial.resize); assert.equal(s.scrollEvents,initial.scroll);
  assert.ok(s.deliveries>initial.deliveries); near(s.units.x,180*s.scroll/s.world,.06);
  near(s.screenWidth,s.mapWidth*s.client/s.world,.2); near(s.screenX,s.mapWidth*s.scroll/s.world,.2);
  sizes.push(s);
 }
 // Dispose during a real mouse drag, then replay callbacks saved before removal.
 await page.locator('.dag-minimap-svg').scrollIntoViewIfNeeded();
 const box=await page.locator('.dag-minimap-svg').boundingBox();
 await page.mouse.move(box.x+box.width/2,box.y+box.height/2); await page.mouse.down();
 const disposed=await page.evaluate(async()=>{
  const a=minimapAudit,v=document.querySelector('#dag-view'),wrap=document.querySelector('#dag-minimap-wrap');
  const results=[historyPreview.disposeMinimap(),historyPreview.disposeMinimap()];
  const before=wrap.outerHTML,scroll=v.scrollLeft;
  let mutations=0;
  const mo=new MutationObserver(records=>mutations+=records.length);
  mo.observe(wrap,{attributes:true,childList:true,subtree:true,characterData:true});
  v.style.width='120px';
  // Explicitly queue saved callbacks after disposal: native disconnect alone cannot guard them.
  await Promise.resolve().then(()=>{
   a.observers[0].callback([],a.observers[0]);
   for (const x of a.listeners) x.callback(new MouseEvent(x.type,{button:0,clientX:999}));
  });
  window.dispatchEvent(new Event('resize')); v.dispatchEvent(new Event('scroll'));
  historyPreview.minimapPan(0); historyPreview.setMinimapScale(1.5); historyPreview.toggleMinimap();
  const panUnchanged=v.scrollLeft===scroll;
  historyPreview.search('b1'); historyPreview.checkout('b1'); historyPreview.refresh();
  await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
  mo.disconnect();
  return {results,targets:a.observers.map(o=>o.targets),disconnects:a.observers.map(o=>o.disconnects),
   listeners:a.listeners.map(x=>({target:x.target===window?'window':x.target.id||x.target.tagName,type:x.type,removed:x.removed})),
   beforeDeliveries:a.observers[0].deliveries,mutations,unchanged:before===wrap.outerHTML,panUnchanged,
   historyLive:historyPreview.state().cursor==='b1',searchLive:historyPreview.searchQuery()==='b1'};
 });
 await page.mouse.move(box.x+box.width,box.y+box.height/2); await page.mouse.up();
 assert.deepEqual(disposed.results,[true,false]); assert.deepEqual(disposed.targets,[['dag-view']]);
 assert.deepEqual(disposed.disconnects,[1]); assert.equal(disposed.listeners.length,10,JSON.stringify(disposed.listeners));
 assert.ok(disposed.listeners.every(x=>x.removed===1));
 assert.equal(disposed.mutations,0); assert.equal(disposed.unchanged,true); assert.equal(disposed.panUnchanged,true);
 assert.equal(disposed.historyLive,true); assert.equal(disposed.searchLive,true);
 await page.evaluate(()=>{document.querySelector('#dag-view').style.width='180px';});
 await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
 assert.equal(await page.evaluate(()=>minimapAudit.observers[0].deliveries),disposed.beforeDeliveries);
 lifecycle.records.push({width,sizes,disposed,pass:true});
}
const near = (a,b,t=1) => assert.ok(Math.abs(a-b)<=t, `${a} != ${b}`);
(async () => {
 const browser=await chromium.launch({headless:true});
 evidence.browser=browser.version();
 try {
  for (const width of [390,768,1280]) {
   const page=await browser.newPage({viewport:{width,height:1100}});
   page.on('pageerror', e=>evidence.errors.push(String(e)));
   await page.setContent(html);
   await page.waitForFunction(()=>!!window.historyPreview);
   for (const scale of [1,1.5,2]) {
    await page.evaluate(s=>{historyPreview.setMinimapScale(s); historyPreview.minimapPan(250);},scale);
    await page.locator('.dag-minimap-svg').scrollIntoViewIfNeeded();
    const geometry = await page.evaluate(()=>{
     const v=document.querySelector('#dag-view'), m=document.querySelector('.dag-minimap-svg'), f=document.querySelector('#minimap-viewport-frame');
     const r=m.getBoundingClientRect(), fr=f.getBoundingClientRect();
     return {world:+m.dataset.worldWidth,client:v.clientWidth,scroll:v.scrollLeft,map:{x:r.x,y:r.y,width:r.width,height:r.height},frame:{x:fr.x-r.x,width:fr.width},units:historyPreview.minimapFrameBounds(),scrollWidth:v.scrollWidth};
    });
    near(geometry.scrollWidth,geometry.world);
    near(geometry.units.width,180*geometry.client/geometry.world,0.06);
    near(geometry.units.x,180*geometry.scroll/geometry.world,0.06);
    near(geometry.frame.width,geometry.map.width*geometry.client/geometry.world,0.2);
    near(geometry.frame.x,geometry.map.width*geometry.scroll/geometry.world,0.2);
    near(geometry.map.height,geometry.map.width/2,0.1);
    const {x,y,width:mw,height:mh}=geometry.map;
    assert.ok(x>=0 && x+mw<=width+1,'map must stay reachable');
    await page.mouse.move(x+mw*.35,y+mh/2); await page.mouse.down();
    await page.mouse.move(x+mw*.7,y+mh/2,{steps:5});
    const actual=await page.evaluate(()=>document.querySelector('#dag-view').scrollLeft);
    const expected=Math.max(0,Math.min(geometry.world-geometry.client,geometry.world*.7-geometry.client/2));
    // Chromium mouse clientX is quantized to a CSS pixel; bound world error.
    near(actual,expected,geometry.world/mw+1);
    await page.mouse.move(x+mw+10,y+mh/2);
    near(await page.evaluate(()=>document.querySelector('#dag-view').scrollLeft),geometry.world-geometry.client);
    await page.mouse.move(x-10,y+mh/2);
    near(await page.evaluate(()=>document.querySelector('#dag-view').scrollLeft),0);
    await page.mouse.up(); await page.mouse.move(x+mw*.8,y+mh/2);
    near(await page.evaluate(()=>document.querySelector('#dag-view').scrollLeft),0);
    const labels=await page.evaluate(()=>{
     const before=document.querySelector('#branch-root-labels').textContent;
     historyPreview.search('b1'); historyPreview.checkout('g11'); historyPreview.search('');
     return {stable:before===document.querySelector('#branch-root-labels').textContent,count:document.querySelectorAll('#branch-root-labels li').length,roots:[...document.querySelectorAll('.minimap-node')].every(n=>n.getAttribute('aria-label').includes('branch root '+n.dataset.branchRoot))};
    });
    assert.equal(labels.stable,true); assert.equal(labels.count,7); assert.equal(labels.roots,true);
    evidence.records.push({width,scale,geometry,drag:{actual,expected,edges:true,released:true},labels,pass:true});
   }
   await page.close();
   const lifecyclePage=await browser.newPage({viewport:{width,height:1100}});
   lifecyclePage.on('pageerror',e=>evidence.errors.push(String(e)));
   await checkLifecycle(lifecyclePage,width);
   await lifecyclePage.close();
   const clipboardPage=await browser.newPage({viewport:{width,height:1100}});
   clipboardPage.on('pageerror',e=>evidence.errors.push(String(e)));
   await clipboardPage.setContent(html);
   const checks=await clipboardPage.evaluate(clipboardChecks);
   assert.equal(checks.length,10);
   await clipboardPage.setContent(html);
   checks.push(...await clipboardPage.evaluate(clipboardChecks,true));
   assert.equal(checks.length,11);
   clipboard.records.push({width,checks,pass:true});
   await clipboardPage.close();
  }
  assert.deepEqual(evidence.errors,[]); assert.equal(evidence.records.length,9);
  assert.equal(lifecycle.records.length,3);
  evidence.pass=true;
 } catch(e) {evidence.pass=false;evidence.failure=String(e);throw e;}
 finally {await browser.close();fs.writeFileSync(path.join(root,'references/uiux-064-browser.json'),JSON.stringify({...evidence,lifecycle,clipboard},null,2)+'\n');}
 console.log(JSON.stringify({pass:true,records:evidence.records.length,lifecycleRecords:lifecycle.records.length,clipboardRecords:clipboard.records.length,clipboardChecks:clipboard.records.reduce((n,r)=>n+r.checks.length,0),browser:evidence.browser}));
})().catch(e=>{console.error(e);process.exitCode=1;});
