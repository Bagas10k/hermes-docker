// Run from a sandbox with motion and playwright installed.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const base=path.resolve(process.argv[2]||process.cwd());
const {chromium}=require(require.resolve('playwright',{paths:[base]}));
const motionEntry=require.resolve('motion',{paths:[base]});
const motionRoot=path.resolve(path.dirname(motionEntry),'../..');
const templates=path.resolve(__dirname,'../templates');
const routes={'/':path.join(templates,'sheet.html'),'/sheet.js':path.join(templates,'sheet.js'),'/motion.js':path.join(motionRoot,'dist/motion.js')};
(async()=>{
const server=http.createServer((req,res)=>{const p=routes[req.url];if(!p){res.writeHead(404).end();return;}res.setHeader('Content-Type',req.url==='/'?'text/html':'text/javascript');res.end(fs.readFileSync(p));});
await new Promise(r=>server.listen(0,'127.0.0.1',r));
let browser;const checks=[],errors=[];
try{
browser=await chromium.launch({headless:true});
const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
await page.addInitScript(()=>{window.pulses=[];Object.defineProperty(navigator,'vibrate',{value:n=>{window.pulses.push(n);return true;},configurable:true});});
for(const width of [390,768,1440]){
 await page.setViewportSize({width,height:900}); await page.goto(`http://127.0.0.1:${server.address().port}`);
 await page.click('#open');await page.waitForTimeout(650);
 assert(await page.locator('#sheet').evaluate(e=>e.open));
 assert.equal(await page.evaluate(()=>document.activeElement.id),'density');
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.selectOption('#density','padat');await page.click('#save');
 assert.equal(await page.locator('#status').textContent(),'Kepadatan: padat');
 assert.equal(await page.evaluate(()=>document.activeElement.id),'open');
 assert.deepEqual(await page.evaluate(()=>pulses),[]);
 checks.push(`width-${width}: focus, save, overflow, default silence`);
}
await page.click('#open');await page.waitForTimeout(650);await page.keyboard.press('Escape');
assert.equal(await page.locator('#sheet').evaluate(e=>e.open),false);checks.push('Escape closes');
async function drag(distance,cancel=false){await page.click('#open');await page.waitForTimeout(650);const b=await page.locator('#handle').boundingBox();await page.mouse.move(b.x+100,b.y+20);await page.mouse.down();await page.mouse.move(b.x+100,b.y+20+distance,{steps:6});if(cancel)await page.locator('#handle').dispatchEvent('pointercancel',{pointerId:1});await page.mouse.up();await page.waitForTimeout(650);}
await drag(160);assert.equal(await page.locator('#sheet').evaluate(e=>e.open),false);checks.push('drag dismiss');
await drag(35);assert(await page.locator('#sheet').evaluate(e=>e.open));assert.equal(await page.locator('#sheet').evaluate(e=>e.style.transform),'translateY(0px)');await page.click('#close');checks.push('short drag snaps back');
await drag(160,true);assert(await page.locator('#sheet').evaluate(e=>e.open));await page.click('#close');checks.push('pointercancel does not dismiss');
await page.click('#open');await page.check('#haptics');await page.click('#save');assert.deepEqual(await page.evaluate(()=>pulses),[10]);checks.push('opt-in invokes API stub; not hardware proof');
await page.emulateMedia({reducedMotion:'reduce'});await page.click('#open');assert.equal(await page.locator('#sheet').evaluate(e=>e.style.transform),'translateY(0px)');await page.click('#save');assert.deepEqual(await page.evaluate(()=>pulses),[10]);checks.push('reduced motion: immediate position and no haptics');
await page.evaluate(()=>Object.defineProperty(navigator,'vibrate',{value:undefined}));await page.click('#open');await page.click('#save');checks.push('missing vibration API keeps save working');
assert.deepEqual(errors,[]);
console.log(JSON.stringify({browser:browser.version(),checks,errors},null,2));
}finally{await browser?.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
