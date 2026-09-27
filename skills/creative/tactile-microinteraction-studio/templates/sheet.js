'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const sheet = $('sheet'), handle = $('handle');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let animation, drag = null, y = 0, previousOverflow, lastPulse = -Infinity;
  let committed = 'nyaman';
  const setY = value => { y = value; sheet.style.transform = `translateY(${value}px)`; };
  const stop = () => { animation?.stop(); animation = null; };
  function settle(target) {
    stop();
    if (reduced.matches || !window.Motion) { setY(target); return; }
    animation = Motion.animate(y, target, { type:'spring', stiffness:420, damping:38, mass:1, onUpdate:setY });
  }
  function pulse() {
    if (!$('haptics').checked || reduced.matches || document.hidden || performance.now()-lastPulse<250) return;
    if (typeof navigator.vibrate === 'function') {
      try { navigator.vibrate(10); lastPulse=performance.now(); } catch { /* Optional hardware; never blocks save. */ }
    }
  }
  function close() { if(sheet.open) sheet.close(); }
  $('open').onclick = () => {
    if (sheet.open) return;
    $('density').value=committed;
    previousOverflow=document.body.style.overflow;
    document.body.style.overflow='hidden';
    sheet.showModal(); setY(reduced.matches ? 0 : 48); settle(0);
  };
  sheet.addEventListener('close', () => {
    stop(); drag=null; setY(0); document.body.style.overflow=previousOverflow;
    $('open').focus();
  });
  $('close').onclick=close;
  $('save').onclick=() => {
    committed=$('density').value;
    $('status').textContent=`Kepadatan: ${committed}`;
    pulse(); close();
  };
  handle.addEventListener('pointerdown', e => {
    if (!e.isPrimary || e.button!==0 || drag) return;
    stop(); drag={id:e.pointerId, start:e.clientY-y};
    handle.setPointerCapture(e.pointerId);
  });
  handle.addEventListener('pointermove', e => {
    if(drag?.id===e.pointerId) setY(Math.max(0,Math.min(sheet.offsetHeight,e.clientY-drag.start)));
  });
  function end(e, cancelled=false) {
    if(drag?.id!==e.pointerId) return;
    const id=drag.id; drag=null;
    if(handle.hasPointerCapture(id)) handle.releasePointerCapture(id);
    if (!cancelled && y>Math.min(120,sheet.offsetHeight*0.3)) close(); else settle(0);
  }
  handle.addEventListener('pointerup',e=>end(e));
  handle.addEventListener('pointercancel',e=>end(e,true));
  handle.addEventListener('lostpointercapture',e=>end(e,true));
  reduced.addEventListener('change',()=>{ if(sheet.open){drag=null;settle(0);} });
  document.addEventListener('visibilitychange',()=>{
    if(document.hidden){stop();drag=null;setY(0);if(typeof navigator.vibrate==='function') navigator.vibrate(0);}
  });
})();
