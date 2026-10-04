"""Isolated DOM camera fixture. Not a GPU grid or browser page-zoom API."""
from pathlib import Path
import math
import sys


def projected_point(world, camera, zoom, origin=(0, 0)):
    values = (*world, *camera, *origin, zoom)
    if any(len(v) != 2 for v in (world, camera, origin)) or any(
        isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
        for v in values
    ) or zoom <= 0:
        raise ValueError('finite pairs and positive zoom required')
    out = tuple(a + (w-c)*zoom for w, c, a in zip(world, camera, origin))
    if not all(math.isfinite(v) for v in out):
        raise ValueError('projection overflow')
    return out


def render_html():
    adapter = Path(__file__).with_name('browser_autoscroll.js').read_text()
    return '''<!doctype html><meta charset="utf-8"><title>Frozen camera test fixture</title>
<style>
*{box-sizing:border-box}body{margin:16px;font:14px sans-serif;background:#faf8f5;color:#17202a}
#grid{display:grid;grid-template-columns:60px 1fr;grid-template-rows:40px 280px;width:min(700px,100%)}
#corner,#top,#left{background:#e1e7ed}#body{background:white;touch-action:none}
#top,#left,#body{position:relative;overflow:hidden}#body{border:3px solid #455a64}
.layer{position:absolute;left:0;top:0;transform-origin:0 0;width:2000px;height:1800px;pointer-events:none}
#world{background-image:linear-gradient(#ccd3da 1px,transparent 1px),linear-gradient(90deg,#ccd3da 1px,transparent 1px);background-size:80px 40px}
.mark{position:absolute;left:240px;top:160px;width:20px;height:20px;background:#1669e8}
#topmark{top:0}#leftmark{left:0}#selection{position:absolute;border:1px solid #dc2626;pointer-events:none}
</style><div id="grid"><div id="corner">Index</div><div id="top"><div class="layer" id="toplayer"><div class="mark" id="topmark"></div></div></div><div id="left"><div class="layer" id="leftlayer"><div class="mark" id="leftmark"></div></div></div><div id="body"><div class="layer" id="world"><div class="mark" id="marker"></div><div id="selection"></div></div></div></div>
<script>''' + adapter + '''
const body=document.getElementById('body');
const camera={x:40,y:30,zoom:1,maxX:0,maxY:0};let selection=null;
let disposed=false, renderCount=0;
let onSelectionHook=null;
function render(){
 if(disposed || !body.isConnected)return;
 renderCount++;
 const z=camera.zoom;camera.maxX=Math.max(0,2000-body.clientWidth/z);camera.maxY=Math.max(0,1800-body.clientHeight/z);
 camera.x=Math.max(0,Math.min(camera.x,camera.maxX));camera.y=Math.max(0,Math.min(camera.y,camera.maxY));
 world.style.transform=`translate(${-camera.x*z}px,${-camera.y*z}px) scale(${z})`;
 // Header transforms include the body border inset exactly once.
 toplayer.style.transform=`translate(${body.clientLeft-camera.x*z}px,0px) scale(${z})`;
 leftlayer.style.transform=`translate(0px,${body.clientTop-camera.y*z}px) scale(${z})`;
}
let controller=attachEdgeScroll(body,s=>{
  selection=s;
  const box=document.getElementById('selection');
  if(box){
    box.style.left=Math.min(s.anchor[0],s.end[0])+'px';
    box.style.top=Math.min(s.anchor[1],s.end[1])+'px';
    box.style.width=Math.abs(s.end[0]-s.anchor[0])+'px';
    box.style.height=Math.abs(s.end[1]-s.anchor[1])+'px';
  }
  if(onSelectionHook) onSelectionHook(s);
}, {read:()=>({...camera}),write:(x,y)=>{camera.x=x;camera.y=y;render()}});

window.fixture={
  camera,
  get controller(){return controller},
  get selection(){return selection},
  set(x,y,z){if(![x,y,z].every(Number.isFinite)||z<=0)throw new RangeError('invalid camera');Object.assign(camera,{x,y,zoom:z});render()},
  setSelectionHook(fn){onSelectionHook=fn;},
  remountController(){
    if(controller) controller.dispose();
    controller=attachEdgeScroll(body,s=>{
      selection=s;
      const box=document.getElementById('selection');
      if(box){
        box.style.left=Math.min(s.anchor[0],s.end[0])+'px';
        box.style.top=Math.min(s.anchor[1],s.end[1])+'px';
        box.style.width=Math.abs(s.end[0]-s.anchor[0])+'px';
        box.style.height=Math.abs(s.end[1]-s.anchor[1])+'px';
      }
      if(onSelectionHook) onSelectionHook(s);
    }, {read:()=>({...camera}),write:(x,y)=>{camera.x=x;camera.y=y;render()}});
    return controller;
  },
  keyboard: {
    get cursor() { return window.fixture.focalCursor ? [...window.fixture.focalCursor] : null; },
    setCursor(r, c) { window.fixture.focalCursor = [r, c]; render(); },
    recover(edgeDir, force=false) {
      if(!window.fixture.focalCursor) window.fixture.focalCursor = [0, 0];
      const z = camera.zoom, row_px = 32, col_px = 96;
      const x0 = camera.x, y0 = camera.y, x1 = x0 + body.clientWidth / z, y1 = y0 + body.clientHeight / z;
      const r_start = Math.max(0, Math.floor(y0 / row_px)), r_end = Math.ceil(y1 / row_px);
      const c_start = Math.max(0, Math.floor(x0 / col_px)), c_end = Math.ceil(x1 / col_px);
      const [cr, cc] = window.fixture.focalCursor;
      const cell_x0 = cc * col_px, cell_y0 = cr * row_px, cell_x1 = cell_x0 + col_px, cell_y1 = cell_y0 + row_px;
      const isVisible = !(cell_x1 <= x0 || cell_x0 >= x1 || cell_y1 <= y0 || cell_y0 >= y1);
      if (isVisible && !force) return { cursor: [...window.fixture.focalCursor], strategy: 'retained_visible' };
      if (edgeDir) {
        const [edx, edy] = edgeDir;
        const tr = edy > 0 ? r_end - 1 : (edy < 0 ? r_start : cr);
        const tc = edx > 0 ? c_end - 1 : (edx < 0 ? c_start : cc);
        window.fixture.focalCursor = [Math.max(r_start, Math.min(r_end - 1, tr)), Math.max(c_start, Math.min(c_end - 1, tc))];
        return { cursor: [...window.fixture.focalCursor], strategy: 'edge_direction_lead' };
      }
      window.fixture.focalCursor = [Math.max(r_start, Math.min(r_end - 1, cr)), Math.max(c_start, Math.min(c_end - 1, cc))];
      return { cursor: [...window.fixture.focalCursor], strategy: 'clamped_closest' };
      }
      },
      selection: {
      get state() {
      if(!window.fixture.selectionState) window.fixture.selectionState = { anchor: [0, 0], lead: [0, 0], is_range_active: false };
      return { ...window.fixture.selectionState };
      },
      setSelection(anchor, lead) {
      window.fixture.selectionState = {
        anchor: [...anchor],
        lead: [...lead],
        is_range_active: (anchor[0] !== lead[0] || anchor[1] !== lead[1])
      };
      render();
      },
      navigate(dir, shift=false, ctrl=false) {
      if(!window.fixture.selectionState) window.fixture.selectionState = { anchor: [0, 0], lead: [0, 0], is_range_active: false };
      const dirs = { 'ArrowRight': [0, 1], 'ArrowLeft': [0, -1], 'ArrowDown': [1, 0], 'ArrowUp': [-1, 0] };
      const delta = dirs[dir] || [0, 0];
      const stepMultiplier = ctrl ? 5 : 1;
      const [lr, lc] = window.fixture.selectionState.lead;
      const target = [Math.max(0, Math.min(49, lr + delta[0] * stepMultiplier)), Math.max(0, Math.min(49, lc + delta[1] * stepMultiplier))];
      if (shift) {
        window.fixture.selectionState = {
          anchor: [...window.fixture.selectionState.anchor],
          lead: target,
          is_range_active: (window.fixture.selectionState.anchor[0] !== target[0] || window.fixture.selectionState.anchor[1] !== target[1])
        };
      } else {
        window.fixture.selectionState = { anchor: target, lead: target, is_range_active: false };
      }
      render();
      return { ...window.fixture.selectionState };
      },
      reconcileAutoscroll(edgeDir) {
      if(!window.fixture.selectionState) window.fixture.selectionState = { anchor: [0, 0], lead: [0, 0], is_range_active: false };
      const z = camera.zoom, row_px = 32, col_px = 96;
      const x0 = camera.x, y0 = camera.y, x1 = x0 + body.clientWidth / z, y1 = y0 + body.clientHeight / z;
      const r_start = Math.max(0, Math.floor(y0 / row_px)), r_end = Math.ceil(y1 / row_px);
      const c_start = Math.max(0, Math.floor(x0 / col_px)), c_end = Math.ceil(x1 / col_px);
      if (edgeDir) {
        const [edx, edy] = edgeDir;
        const tr = edy > 0 ? r_end - 1 : (edy < 0 ? r_start : window.fixture.selectionState.lead[0]);
        const tc = edx > 0 ? c_end - 1 : (edx < 0 ? c_start : window.fixture.selectionState.lead[1]);
        const target = [Math.max(r_start, Math.min(r_end - 1, tr)), Math.max(c_start, Math.min(c_end - 1, tc))];
        window.fixture.selectionState = {
          anchor: [...window.fixture.selectionState.anchor],
          lead: target,
          is_range_active: (window.fixture.selectionState.anchor[0] !== target[0] || window.fixture.selectionState.anchor[1] !== target[1])
        };
        return { state: { ...window.fixture.selectionState }, strategy: 'lead_edge_expanded' };
      }
      return { state: { ...window.fixture.selectionState }, strategy: 'lead_retained' };
      },
      multiRange: {
      get ranges() {
        if (!window.fixture.multiRanges) window.fixture.multiRanges = [];
        return window.fixture.multiRanges.map(b => ({ ...b }));
      },
      click(r, c, ctrl=false, shift=false) {
        if (!window.fixture.multiRanges) window.fixture.multiRanges = [];
        if (!ctrl && !shift) {
          window.fixture.multiRanges = [{ r0: r, c0: c, r1: r, c1: c, id: 'box-0' }];
        } else if (ctrl && !shift) {
          const idx = window.fixture.multiRanges.findIndex(b => b.r0 === r && b.r1 === r && b.c0 === c && b.c1 === c);
          if (idx >= 0) {
            window.fixture.multiRanges.splice(idx, 1);
          } else {
            window.fixture.multiRanges.push({ r0: r, c0: c, r1: r, c1: c, id: 'box-' + window.fixture.multiRanges.length });
          }
        }
        render();
        return window.fixture.multiRanges.map(b => ({ ...b }));
      },
      deduplicate() {
        if (!window.fixture.multiRanges) window.fixture.multiRanges = [];
        const deduped = [];
        for (const b of window.fixture.multiRanges) {
          const isContained = deduped.some(k => k.r0 <= b.r0 && k.r1 >= b.r1 && k.c0 <= b.c0 && k.c1 >= b.c1);
          if (!isContained) deduped.push(b);
        }
        window.fixture.multiRanges = deduped;
        render();
        return deduped.map(b => ({ ...b }));
      },
      queryVisible() {
        if (!window.fixture.multiRanges) window.fixture.multiRanges = [];
        const z = camera.zoom, row_px = 32, col_px = 96;
        const x0 = camera.x, y0 = camera.y, x1 = x0 + body.clientWidth / z, y1 = y0 + body.clientHeight / z;
        const r_start = Math.max(0, Math.floor(y0 / row_px)), r_end = Math.ceil(y1 / row_px);
        const c_start = Math.max(0, Math.floor(x0 / col_px)), c_end = Math.ceil(x1 / col_px);
        const camBox = { r0: r_start, c0: c_start, r1: r_end, c1: c_end };
        const intersects = (a, b) => !(a.r1 < b.r0 || a.r0 > b.r1 || a.c1 < b.c0 || a.c0 > b.c1);
        return window.fixture.multiRanges.filter(b => intersects(b, camBox)).map(b => ({ ...b }));
      }
      }
      }
      };
// Container-only resizing need not emit a window resize event.
const resizeObserver=new ResizeObserver(render);resizeObserver.observe(body);
window.fixture.resize=(width,height)=>{if(![width,height].every(Number.isFinite)||width<80||height<10)throw new RangeError('invalid body size');grid.style.width=width+'px';grid.style.gridTemplateRows='40px '+height+'px';};
window.fixture.dispose=()=>{if(disposed)return;disposed=true;resizeObserver.disconnect();window.removeEventListener('resize',render);if(controller)controller.dispose();};
Object.defineProperty(window.fixture,'renderCount',{get:()=>renderCount});
window.addEventListener('resize',render);render();
</script>'''


if __name__ == '__main__':
    Path(sys.argv[1]).write_text(render_html())
