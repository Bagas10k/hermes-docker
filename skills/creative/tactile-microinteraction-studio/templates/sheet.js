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
  let audio;
  async function confirmSound() {
    if (!$('sound').checked || reduced.matches || document.hidden) return;
    try {
      const Context = window.AudioContext || window.webkitAudioContext;
      if (!Context) throw new Error('unsupported');
      audio ||= new Context();
      await audio.resume();
      if (document.hidden || reduced.matches || !$('sound').checked) return;
      const oscillator = audio.createOscillator(), gain = audio.createGain();
      const now = audio.currentTime;
      oscillator.frequency.value = 660;
      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(0.035, now + 0.008);
      gain.gain.linearRampToValueAtTime(0, now + 0.07);
      oscillator.connect(gain); gain.connect(audio.destination);
      oscillator.onended = () => { oscillator.disconnect(); gain.disconnect(); };
      oscillator.start(now); oscillator.stop(now + 0.08);
    } catch { $('status').textContent += ' · Bunyi tidak tersedia; pengaturan tetap tersimpan.'; }
  }
  document.addEventListener('visibilitychange', () => { if(document.hidden) audio?.suspend().catch(()=>{}); });
  window.addEventListener('pagehide', () => { audio?.close().catch(()=>{}); });
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
  handle.addEventListener('click', e => { if(e.detail===0) close(); });
  $('save').onclick=() => {
    committed=$('density').value;
    $('status').textContent=`Kepadatan: ${committed}`;
    pulse(); void confirmSound(); close();
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
  // Independent visual surface: never compete with the sheet's translateY writer.
  const material=$('material'), tilt=$('tilt'), tiltStatus=$('tilt-status');
  let enabled=false, generation=0, frame=0, watchdog, baseline, latest=[0,0], sensor=false;
  const clamp=n=>Math.max(-1,Math.min(1,n));
  const allowed=()=>enabled && sheet.open && !document.hidden && !reduced.matches;
  function neutral(){cancelAnimationFrame(frame);frame=0;material.style.cssText='';}
  function paint(x,z){
    latest=[clamp(x),clamp(z)];
    if(frame || !allowed()) return;
    frame=requestAnimationFrame(()=>{
      frame=0;if(!allowed())return;
      const [a,b]=latest;
      material.style.setProperty('--rx',`${-b*6}deg`);
      material.style.setProperty('--ry',`${a*6}deg`);
      material.style.setProperty('--sx',`${50+a*35}%`);
      material.style.setProperty('--sy',`${50+b*35}%`);
      material.style.setProperty('--shine','0.6');
    });
  }
  function detach(){window.removeEventListener('deviceorientation',orient);clearTimeout(watchdog);sensor=false;baseline=null;}
  function disable(message='Efek mati. Pengaturan tetap bisa disimpan.'){
    enabled=false;generation++;detach();neutral();tilt.setAttribute('aria-pressed','false');
    tilt.textContent='Aktifkan tilt & kilau';tiltStatus.textContent=message;
  }
  function fallback(message){detach();neutral();tiltStatus.textContent=message+' Gerakkan kursor pada pratinjau, atau gunakan tampilan statis.';}
  function armWatchdog(){clearTimeout(watchdog);watchdog=setTimeout(()=>fallback('Data sensor tidak tersedia.'),1800);}
  function orient(e){
    if(!allowed() || !Number.isFinite(e.beta) || !Number.isFinite(e.gamma))return;
    baseline ||= [e.beta,e.gamma];sensor=true;armWatchdog();
    const dy=((e.beta-baseline[0]+540)%360)-180;
    const dx=((e.gamma-baseline[1]+540)%360)-180;
    const angle=(screen.orientation?.angle || 0)*Math.PI/180;
    paint((dx*Math.cos(angle)+dy*Math.sin(angle))/30,(dy*Math.cos(angle)-dx*Math.sin(angle))/30);
    tiltStatus.textContent='Tilt sensor aktif. Kilau mengikuti pratinjau.';
  }
  tilt.onclick=async()=>{
    if(enabled){disable();return;}
    if(reduced.matches){disable('Efek dinonaktifkan oleh preferensi kurangi gerakan.');return;}
    enabled=true;const ticket=++generation;
    tilt.setAttribute('aria-pressed','true');tilt.textContent='Matikan tilt & kilau';
    tiltStatus.textContent='Menunggu izin atau data sensor; kursor tetap tersedia.';
    if(!window.isSecureContext){fallback('Sensor membutuhkan HTTPS.');return;}
    if(!window.DeviceOrientationEvent){fallback('Sensor tidak didukung.');return;}
    try{
      // Call directly from activation, before any unrelated await.
      const permission=typeof DeviceOrientationEvent.requestPermission==='function'
        ? await DeviceOrientationEvent.requestPermission() : 'granted';
      if(ticket!==generation || !allowed())return;
      if(permission!=='granted'){fallback('Izin sensor ditolak.');return;}
      window.addEventListener('deviceorientation',orient);armWatchdog();
    }catch{if(ticket===generation && allowed())fallback('Izin sensor tidak tersedia.');}
  };
  material.addEventListener('pointermove',e=>{
    if(!allowed() || sensor || e.pointerType!=='mouse')return;
    const r=material.getBoundingClientRect();paint((e.clientX-r.left)/r.width*2-1,(e.clientY-r.top)/r.height*2-1);
  });
  material.addEventListener('pointerleave',()=>{if(!sensor)neutral();});
  sheet.addEventListener('close',()=>disable());
  reduced.addEventListener('change',()=>{if(reduced.matches)disable('Efek dinonaktifkan oleh preferensi kurangi gerakan.');});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)disable('Efek dihentikan saat halaman tersembunyi. Aktifkan lagi bila diperlukan.');});
  window.addEventListener('pagehide',()=>disable());
  screen.orientation?.addEventListener('change',()=>{baseline=null;neutral();});
})();
