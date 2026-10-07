'use strict';
// NODE_PATH=/home/ubuntu/website-security-auditor/node_modules node scripts/test_native_clipboard_chromium.cjs
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const fixture = JSON.parse(execFileSync('python3', ['-B', path.join(__dirname,'native_clipboard_fixture.py')], {encoding:'utf8'}));
const evidence = {kind:'native headless Chromium clipboard; loopback secure context; CDP permission intervention',
  limitations:['Not physical system clipboard or cross-application paste integration','No permission prompt UI, other browser, screen-reader or performance claim'], records:[], errors:[]};
(async()=>{
 const server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'});res.end(fixture.html);});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 let browser;
 try {
  const origin=`http://127.0.0.1:${server.address().port}`;
  evidence.origin=origin;
  browser=await chromium.launch({headless:true}); evidence.browser=browser.version();
  for(const width of [390,768,1280]) {
   const context=await browser.newContext({viewport:{width,height:1100}});
   const page=await context.newPage(); page.setDefaultTimeout(10000);
   page.on('pageerror',e=>evidence.errors.push(String(e)));
   await page.goto(origin); await page.bringToFront();
   const cdp=await context.newCDPSession(page);
   const {browserContextId}= (await cdp.send('Target.getTargetInfo')).targetInfo;
   const permission=async(write)=>{
    // setPermission takes web PermissionDescriptor names, not grantPermissions enums.
    for(const [name,setting] of [['clipboard-read','granted'],['clipboard-write',write]])
     await cdp.send('Browser.setPermission',{permission:{name},setting,origin,browserContextId});
    const state=await page.evaluate(async()=>({
     read:(await navigator.permissions.query({name:'clipboard-read'})).state,
     write:(await navigator.permissions.query({name:'clipboard-write'})).state}));
    assert.deepEqual(state,{read:'granted',write}); return state;
   };
   const native=await page.evaluate(()=>({secure:isSecureContext,focused:document.hasFocus(),
    write:Function.prototype.toString.call(navigator.clipboard.writeText),
    read:Function.prototype.toString.call(navigator.clipboard.readText),
    own:Object.hasOwn(navigator,'clipboard')}));
   assert.equal(native.secure,true); assert.equal(native.focused,true); assert.equal(native.own,false);
   assert.match(native.write,/\[native code\]/); assert.match(native.read,/\[native code\]/);
   const button=page.locator('.dag-breadcrumb-copy-btn');
   const clickCopy=async(success)=>{
    await button.click();
    await page.waitForFunction(text=>document.querySelector('.dag-breadcrumb-copy-btn').textContent===text,success?'Tersalin!':'Gagal menyalin');
    const ui=await button.evaluate(b=>({text:b.textContent,copied:b.classList.contains('copied')}));
    assert.equal(ui.copied,success); return ui;
   };
   const read=()=>page.evaluate(()=>navigator.clipboard.readText());
   let states=await permission('granted');
   // A distinct native seed rules out a false positive from an earlier run.
   await page.evaluate(()=>navigator.clipboard.writeText('UIUX-065 seed'));
   assert.equal(await read(),'UIUX-065 seed');
   let ui=await clickCopy(true), text=await read();
   assert.equal(text,fixture.initial.text);
   evidence.records.push({width,case:'granted-exact-route',states,native,ui,text,pass:true});
   await page.evaluate(id=>historyPreview.checkout(id),fixture.recovery.id);
   states=await permission('denied');
   const rejection=await page.evaluate(async()=>{
    try {await navigator.clipboard.writeText('must not replace');return null;}
    catch(e){return {name:e.name,message:e.message};}
   });
   assert.equal(rejection?.name,'NotAllowedError');
   ui=await clickCopy(false); text=await read();
   assert.equal(text,fixture.initial.text);
   const failed=await page.evaluate(()=>historyPreview.copyLineage());
   assert.deepEqual(failed,{text:fixture.recovery.text,success:false});
   assert.equal(await read(),fixture.initial.text);
   evidence.records.push({width,case:'denied-write-retains-clipboard',states,rejection,ui,text,result:failed,pass:true});
   states=await permission('granted');
   ui=await clickCopy(true); text=await read();
   assert.equal(text,fixture.recovery.text);
   const recovered=await page.evaluate(()=>historyPreview.copyLineage());
   assert.deepEqual(recovered,{text:fixture.recovery.text,success:true});
   assert.equal(await read(),fixture.recovery.text);
   evidence.records.push({width,case:'permission-recovery-new-route',states,ui,text,result:recovered,pass:true});
   await context.close();
  }
  assert.equal(evidence.records.length,9); assert.deepEqual(evidence.errors,[]); evidence.pass=true;
 } catch(e) {evidence.pass=false;evidence.failure=String(e);throw e;}
 finally {
  if(browser) await browser.close();
  await new Promise(resolve=>server.close(resolve));
  fs.writeFileSync(path.join(__dirname,'../references/uiux-065-browser.json'),JSON.stringify(evidence,null,2)+'\n');
 }
 console.log(JSON.stringify({pass:evidence.pass,records:evidence.records.length,browser:evidence.browser}));
})().catch(e=>{console.error(e);process.exitCode=1;});
