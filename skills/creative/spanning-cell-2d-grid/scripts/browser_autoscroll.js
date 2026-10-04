/* Scrollable-body adapter. CSS pixels only; native scroll is authoritative. */
window.attachEdgeScroll = function(el, onSelection = () => {}, camera = null) {
  // camera: read() -> {x,y,zoom,maxX,maxY}; write(x,y) synchronously clamps.
  function readCamera() {
    if (!camera) return {x:el.scrollLeft,y:el.scrollTop,zoom:1,maxX:Math.max(0,el.scrollWidth-el.clientWidth),maxY:Math.max(0,el.scrollHeight-el.clientHeight)};
    const c=camera.read();
    if (!c || !['x','y','zoom','maxX','maxY'].every(k=>Number.isFinite(c[k])) || c.zoom<=0 || c.maxX<0 || c.maxY<0 || c.x<0 || c.x>c.maxX || c.y<0 || c.y>c.maxY) throw new RangeError('invalid camera');
    return c;
  }
  let id = null, point = null, anchor = null, raf = null, last = null, disposed = false;
  const clamp = (x,a,b) => Math.min(b,Math.max(a,x));
  const local = p => { const r=el.getBoundingClientRect(); return [p[0]-r.left-el.clientLeft,p[1]-r.top-el.clientTop]; };
  const world = () => { const p=local(point), c=readCamera(); return [c.x+p[0]/c.zoom,c.y+p[1]/c.zoom]; };
  const select = () => onSelection({anchor:[...anchor],end:world()});
  function stop() {
    const old=id; id=null; last=null;
    if(raf!==null) cancelAnimationFrame(raf);
    raf=null;
    if(old!==null && el.hasPointerCapture(old)) el.releasePointerCapture(old);
  }
  function frame(t) {
    raf=null;
    if(id===null || disposed || el.isConnected===false || document.hidden) {stop(); return;}
    const dt=last===null?0:clamp((t-last)/1000,0,.05); last=t;
    const p=local(point);
    const v=(p,size)=>{if(size<=0)return 0; const b=Math.min(48,size/2); return 800*(clamp((p-size+b)/b,0,1)**2-clamp((b-p)/b,0,1)**2);};
    let x=v(p[0],el.clientWidth), y=v(p[1],el.clientHeight);
    const norm=Math.hypot(x,y); if(norm>800){x*=800/norm;y*=800/norm;}
    try {
      const c=readCamera(), nx=clamp(c.x+x*dt/c.zoom,0,c.maxX), ny=clamp(c.y+y*dt/c.zoom,0,c.maxY);
      if(camera) camera.write(nx,ny); else {el.scrollLeft=nx;el.scrollTop=ny;}
      select();
    } catch(error) {stop(); throw error;}
    if(id!==null) raf=requestAnimationFrame(frame);
  }
  function down(e) {
    if(disposed || el.isConnected===false || id!==null || !e.isPrimary || e.button!==0 || document.hidden)return;
    el.setPointerCapture(e.pointerId);
    id=e.pointerId; point=[e.clientX,e.clientY]; last=null;
    e.preventDefault();
    try {anchor=world();select();} catch(error) {stop(); throw error;}
    if(id!==null)raf=requestAnimationFrame(frame);
  }
  function move(e){if(e.pointerId===id)point=[e.clientX,e.clientY];}
  function end(e){if(e.pointerId===id)stop();}
  function visibility(){if(document.hidden)stop();}
  const events={pointerdown:down,pointermove:move,pointerup:end,pointercancel:end,lostpointercapture:end};
  for(const [event,handler] of Object.entries(events))el.addEventListener(event,handler);
  document.addEventListener('visibilitychange',visibility);
  window.addEventListener('blur',stop);
  return {stop, get active(){return id!==null;}, dispose(){stop();disposed=true;for(const [event,handler] of Object.entries(events))el.removeEventListener(event,handler);document.removeEventListener('visibilitychange',visibility);window.removeEventListener('blur',stop);}};
};
