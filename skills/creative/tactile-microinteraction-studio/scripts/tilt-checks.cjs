const assert=require('node:assert/strict'),path=require('node:path');
module.exports=async function(browser,url,base,errors){
 const checks=[],activeAccessibility=[];
 async function fresh(mode='granted'){
  const p=await browser.newPage({viewport:{width:390,height:900}});p.on('pageerror',e=>errors.push(e.message));
  await p.addInitScript(mode=>{
   window.requests=0;window.resolves=null;
   if(mode==='missing')Object.defineProperty(window,'DeviceOrientationEvent',{value:undefined});
   else if(mode==='implicit')DeviceOrientationEvent.requestPermission=undefined;
   else DeviceOrientationEvent.requestPermission=()=>{
    window.requests++;window.activation=navigator.userActivation.isActive;
    if(mode==='pending')return new Promise(r=>window.resolves=r);
    if(mode==='rejected')return Promise.reject(new Error('blocked'));
    return Promise.resolve(mode==='denied'?'denied':'granted');
   };
   if(mode==='insecure')Object.defineProperty(window,'isSecureContext',{value:false});
  },mode);
  await p.goto(url);await p.click('#open');await p.waitForTimeout(650);return p;
 }
 const emit=(p,beta,gamma)=>p.evaluate(([beta,gamma])=>{
  const e=new Event('deviceorientation');Object.defineProperties(e,{beta:{value:beta},gamma:{value:gamma}});dispatchEvent(e);
 },[beta,gamma]);
 const style=p=>p.locator('#material').getAttribute('style');
 for(const mode of ['granted','implicit']){
  const p=await fresh(mode);assert.equal(await p.evaluate(()=>requests),0);
  await emit(p,10,10);assert(!(await style(p)));
  await p.click('#tilt');if(mode==='granted')assert(await p.evaluate(()=>activation));
  await emit(p,null,NaN);assert(!(await style(p)));
  await emit(p,20,20);await emit(p,90,80);await p.waitForTimeout(60);
  assert.equal(await p.locator('#material').evaluate(e=>e.style.getPropertyValue('--ry')),'6deg');
  assert.equal(await p.locator('#material').evaluate(e=>e.style.getPropertyValue('--rx')),'-6deg');
  assert.equal(await p.locator('#sheet').evaluate(e=>e.style.transform),'translateY(0px)');
  assert.equal(await p.locator('#material').evaluate(e=>getComputedStyle(e,'::before').pointerEvents),'none');
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  if(mode==='granted'){
   await p.addScriptTag({path:require.resolve('axe-core/axe.min.js',{paths:[base]})});
   for(const width of [390,768,1440]){
    await p.setViewportSize({width,height:900});await emit(p,90,80);await p.waitForTimeout(50);
    assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
    const result=await p.evaluate(async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {width:innerWidth,violations:r.violations,incomplete:r.incomplete.map(x=>x.id)};});
    assert.deepEqual(result.violations,[]);activeAccessibility.push(result);
    await p.screenshot({path:path.join(base,`tilt-active-${width}.png`),fullPage:true});
   }
  }
  await p.emulateMedia({reducedMotion:'reduce'});await p.waitForFunction(()=>document.getElementById('tilt').getAttribute('aria-pressed')==='false');assert.equal(await style(p),'');
  await emit(p,0,0);assert.equal(await style(p),'');
  await p.click('#tilt');assert.equal(await p.locator('#tilt').getAttribute('aria-pressed'),'false');
  await p.click('#save');assert.equal(await p.locator('#status').textContent(),'Kepadatan: nyaman');await p.close();
  checks.push(`${mode}: default off, finite data, relative/clamped tilt, sheen, separate transform, dynamic reduced motion`);
 }
 for(const mode of ['denied','rejected','missing','insecure','granted']){
  const p=await fresh(mode);await p.click('#tilt');if(mode==='granted')await p.waitForTimeout(1900);
  assert.match(await p.locator('#tilt-status').textContent(),/kursor/);
  const b=await p.locator('#material').boundingBox();await p.mouse.move(b.x+b.width*.85,b.y+b.height*.65);await p.waitForTimeout(60);
  assert.equal(await p.locator('#material').evaluate(e=>e.style.getPropertyValue('--shine')),'0.6');
  await p.click('#tilt');assert.equal(await style(p),'');
  await p.click('#save');assert.equal(await p.locator('#status').textContent(),'Kepadatan: nyaman');await p.close();
  checks.push(`${mode}: fallback pointer/static and save; explicit off resets`);
 }
 for(const interrupt of ['close','hidden','pagehide','reduce']){
  const p=await fresh('pending');await p.click('#tilt');
  if(interrupt==='close'){await p.click('#close');await p.click('#open');}
  if(interrupt==='hidden')await p.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));});
  if(interrupt==='pagehide')await p.evaluate(()=>dispatchEvent(new Event('pagehide')));
  if(interrupt==='reduce'){await p.emulateMedia({reducedMotion:'reduce'});await p.waitForFunction(()=>document.getElementById('tilt').getAttribute('aria-pressed')==='false');}
  await p.evaluate(()=>resolves('granted'));await emit(p,10,10);await emit(p,90,80);await p.waitForTimeout(60);
  assert.equal(await p.locator('#tilt').getAttribute('aria-pressed'),'false');assert.equal(await style(p),'');await p.close();
  checks.push(`${interrupt}: late permission cannot restart effect (synthetic lifecycle)`);
 }
 const small=await fresh('missing');await small.setViewportSize({width:390,height:520});
 await small.selectOption('#density','padat');await small.click('#close');await small.click('#open');
 assert.equal(await small.locator('#density').inputValue(),'nyaman');
 for(let i=0;i<10;i++){await small.keyboard.press('Tab');assert.notEqual(await small.evaluate(()=>document.activeElement.id),'open');}
 await small.locator('#save').scrollIntoViewIfNeeded();const box=await small.locator('#save').boundingBox();assert(box.y>=0 && box.y+box.height<=520);
 await small.click('#save');await small.close();checks.push('390x520: scroll-reachable footer, background opener excluded from Tab traversal, cancel preserves density');
 return {checks,activeAccessibility};
};
