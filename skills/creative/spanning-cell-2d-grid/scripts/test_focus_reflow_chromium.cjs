'use strict';
// Real keyboard + application-driven controlled clipboard. Not native page zoom.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const {execFileSync, spawnSync} = require('node:child_process');
const http = require('node:http');
const path = require('node:path');
const fs = require('node:fs');
const fixture = JSON.parse(execFileSync('python3', ['-B', path.join(__dirname, 'native_clipboard_fixture.py')], {encoding:'utf8'}));
const output = path.join(__dirname, '../references/uiux-069-browser.json');
const evidence = {target:'UIUX-069', records:[], negativeControls:{}, errors:[], pass:false,
  limitations:['Explicit computed-font scaling, not native browser zoom',
    'Known foreground opaque rectangles and sampled hit-testing, not arbitrary CSS paint proof',
    'Rounded outline AABB is conservative; no pixel-area or screen-reader speech claim',
    'Controlled clipboard promises; native Tab/Enter; no OS clipboard claim',
    'Clipboard button/bar and document width audited, not all content or full-page reflow certification']};

// Same extractor for positive records and ALL negative controls.
function measure(meta) {
  const b = document.querySelector('.dag-breadcrumb-copy-btn'), bar = document.getElementById('dag-breadcrumbs');
  const rect = el => {const r=el.getBoundingClientRect(); return {left:r.left,top:r.top,right:r.right,bottom:r.bottom};};
  const br=rect(b), cs=getComputedStyle(b), clips=[], unsupported=[];
  for(let el=b; el; el=el.parentElement) {
    const s=getComputedStyle(el);
    for(const prop of ['transform','filter','clipPath','maskImage','perspective'])
      if(s[prop] && s[prop]!=='none') unsupported.push(el.tagName+':'+prop);
    if(s.opacity!=='1' || s.mixBlendMode!=='normal') unsupported.push('opacity/blend');
    for(const pseudo of ['::before','::after']) {
      const p=getComputedStyle(el,pseudo);
      if(p.content!=='none' && p.content!=='normal') unsupported.push('pseudo');
    }
    if(el===b) continue;
    const paint=/(paint|strict|content)/.test(s.contain);
    const x=paint || /^(auto|scroll|hidden|clip)$/.test(s.overflowX);
    const y=paint || /^(auto|scroll|hidden|clip)$/.test(s.overflowY);
    if(x||y) {
      const r=rect(el);
      clips.push({left:r.left+el.clientLeft,top:r.top+el.clientTop,
        right:r.left+el.clientLeft+el.clientWidth,bottom:r.top+el.clientTop+el.clientHeight,x,y});
      if(parseFloat(s.borderRadius)>0) unsupported.push('rounded clipping ancestor');
      if(s.overflowClipMargin && s.overflowClipMargin!=='0px') unsupported.push('overflow-clip-margin');
    }
  }
  const points=[[.5,.5],[.1,.1],[.9,.1],[.1,.9],[.9,.9]];
  const hitTestPassed=points.every(([x,y])=>{const e=document.elementFromPoint(br.left+(br.right-br.left)*x,br.top+(br.bottom-br.top)*y);return e===b||b.contains(e);});
  // ponytail: only known foreground fixtures, not a general stacking-context solver.
  const opaqueOverlays=[];
  for(const el of document.querySelectorAll('[data-focus-audit-overlay], #dag-diff-popover')) {
    const s=getComputedStyle(el), r=el.getBoundingClientRect();
    if(s.display==='none'||s.visibility==='hidden'||!r.width||!r.height) continue;
    if(s.opacity!=='1'||!s.backgroundColor.startsWith('rgb(')||s.transform!=='none') unsupported.push('overlay paint');
    // Existing popover is clipped by #dag-view. Intersect that known clip first.
    const box=rect(el);
    if(el.id==='dag-diff-popover') {
      const clip=rect(document.getElementById('dag-view'));
      box.left=Math.max(box.left,clip.left); box.right=Math.min(box.right,clip.right);
      box.top=Math.max(box.top,clip.top); box.bottom=Math.min(box.bottom,clip.bottom);
    }
    if(box.left<box.right&&box.top<box.bottom) opaqueOverlays.push(box);
  }
  return {...meta, focused:document.activeElement===b, focusVisible:b.matches(':focus-visible'),
    outlineStyle:cs.outlineStyle,outlineWidth:parseFloat(cs.outlineWidth),outlineOffset:parseFloat(cs.outlineOffset),
    buttonRect:br,barRect:rect(bar),viewportSize:{width:innerWidth,height:innerHeight},clips,unsupported,
    hitTestPassed,opaqueOverlays,btnScrollWidth:b.scrollWidth,btnClientWidth:b.clientWidth,
    btnScrollHeight:b.scrollHeight,btnClientHeight:b.clientHeight,barScrollWidth:bar.scrollWidth,barClientWidth:bar.clientWidth,
    fontSamples:window.fontBaseline.map(([el,before])=>({before,after:parseFloat(getComputedStyle(el).fontSize)})),
    label:b.textContent,statusText:document.getElementById('status').textContent,copied:b.classList.contains('copied'),
    trustedClicks:window.trustedClicks,writeCalls:window.writeCalls,
    reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,
    transitionSeconds:Math.max(...cs.transitionDuration.split(',').map(v=>parseFloat(v)*(v.trim().endsWith('ms')?.001:1))),
    documentScrollWidth:document.documentElement.scrollWidth,documentClientWidth:document.documentElement.clientWidth};
}

async function prepare(page, origin, meta) {
  await page.goto(origin); await page.bringToFront();
  await page.evaluate(({container,scale})=>{
    if(container==='narrow') document.getElementById('dag-breadcrumbs').style.maxWidth='220px';
    // Snapshot BEFORE any mutation: reading inherited sizes after scaling parents compounds 2x into 4x.
    window.fontBaseline=[document.body,...document.querySelectorAll('main, main *')]
      .filter(el=>el instanceof HTMLElement).map(el=>[el,parseFloat(getComputedStyle(el).fontSize)]);
    for(const [el,size] of fontBaseline) el.style.fontSize=(size*scale)+'px';
    const realSetTimeout=window.setTimeout.bind(window);
    window.setTimeout=(callback,ms,...args)=>ms===1500?777777:realSetTimeout(callback,ms,...args);
    window.writeCalls=0; window.trustedClicks=0;
    const b=document.querySelector('.dag-breadcrumb-copy-btn');
    b.addEventListener('click',e=>{if(e.isTrusted) window.trustedClicks++;});
    Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:()=>{
      window.writeCalls++; return new Promise((resolve,reject)=>{window.settleCopy={resolve,reject};});
    }}});
  },meta);
  await page.locator('#outside').focus();
  let tabs=0;
  while(tabs<30 && !await page.evaluate(()=>document.activeElement.matches('.dag-breadcrumb-copy-btn'))) {
    await page.keyboard.press('Tab'); tabs++;
  }
  assert.ok(tabs>0&&tabs<30,'native Tab must reach copy');
  if(meta.state!=='idle') {
    await page.keyboard.press('Enter');
    await page.waitForFunction(()=>window.writeCalls===1 && document.querySelector('.dag-breadcrumb-copy-btn').textContent==='Menyalin…');
    if(meta.state==='success') await page.evaluate(()=>window.settleCopy.resolve());
    if(meta.state==='failure') await page.evaluate(()=>window.settleCopy.reject(new Error('controlled denial')));
    if(meta.state!=='pending') await page.waitForFunction(st=>document.querySelector('.dag-breadcrumb-copy-btn').textContent===(st==='success'?'Tersalin!':'Gagal menyalin'),meta.state);
  }
  await page.evaluate(async()=>{await new Promise(requestAnimationFrame); await Promise.all(document.querySelector('.dag-breadcrumb-copy-btn').getAnimations().map(a=>a.finished));});
  return {...meta,tabCount:tabs};
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { measure, prepare };
}

if (require.main === module) {
(async()=>{
  const server=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'});res.end(fixture.html);});
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  let browser;
  try {
    const origin=`http://127.0.0.1:${server.address().port}`;
    browser=await chromium.launch({headless:true}); evidence.browser=browser.version();
    for(const viewport of [320,390,768]) {
      const context=await browser.newContext({viewport:{width:viewport,height:900},reducedMotion:'reduce'});
      const page=await context.newPage(); page.setDefaultTimeout(10000);
      page.on('pageerror',e=>evidence.errors.push(String(e)));
      for(const container of ['normal','narrow']) for(const scale of [1,2]) for(const state of ['idle','pending','success','failure']) {
        const meta=await prepare(page,origin,{viewport,container,scale,state});
        evidence.records.push(await page.evaluate(measure,meta));
      }
      await context.close();
    }
    const ctx=await browser.newContext({viewport:{width:320,height:900},reducedMotion:'reduce'});
    const page=await ctx.newPage(); page.on('pageerror',e=>evidence.errors.push(String(e)));
    for(const name of ['clipping','occlusionStandard','occlusionPointerEventsNone','outlineOnly','unfocused','textOverflow']) {
      const meta=await prepare(page,origin,{viewport:320,container:'normal',scale:1,state:'idle'});
      await page.evaluate(name=>{
        const b=document.querySelector('.dag-breadcrumb-copy-btn'), r=b.getBoundingClientRect();
        if(name==='clipping') {
          const s=b.closest('section'), sr=s.getBoundingClientRect();
          s.style.height=(r.bottom-sr.top-1)+'px'; s.style.overflow='hidden';
        } else if(name.startsWith('occlusion')||name==='outlineOnly') {
          const o=document.createElement('div'); o.dataset.focusAuditOverlay='';
          Object.assign(o.style,{position:'fixed',left:(name==='outlineOnly'?r.left-3.5:r.left)+'px',top:(r.top+5)+'px',
            width:(name==='outlineOnly'?1:r.width)+'px',height:(r.height-10)+'px',
            backgroundColor:'rgb(0, 0, 0)',zIndex:'2147483647',pointerEvents:name==='occlusionStandard'?'auto':'none'});
          document.body.appendChild(o);
        } else if(name==='unfocused') document.getElementById('outside').focus();
        else {b.style.whiteSpace='nowrap';b.style.maxWidth='30px';}
      },name);
      evidence.negativeControls[name]={record:await page.evaluate(measure,meta)};
    }
    await ctx.close();
    assert.equal(evidence.records.length,48); assert.deepEqual(evidence.errors,[]); evidence.pass=true;
  } catch(err) {evidence.errors.push(String(err));}
  finally {if(browser) await browser.close(); await new Promise(resolve=>server.close(resolve));}
  fs.writeFileSync(output,JSON.stringify(evidence,null,2));
  const gate=spawnSync('python3',['-B',path.join(__dirname,'clipboard_focus_reflow.py'),output],{encoding:'utf8'});
  console.log(JSON.stringify({browser:evidence.browser,records:evidence.records.length,negativeControls:Object.keys(evidence.negativeControls).length,gateExit:gate.status,gate:gate.stdout,errors:evidence.errors,stderr:gate.stderr}));
  process.exit(gate.status===0?0:1);
})();
}
