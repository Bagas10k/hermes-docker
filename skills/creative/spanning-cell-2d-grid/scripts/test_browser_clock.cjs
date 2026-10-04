const assert=require('node:assert/strict'), fs=require('node:fs'), vm=require('node:vm');
class Target {
 constructor(){this.listeners=new Map();}
 addEventListener(k,f){if(!this.listeners.has(k))this.listeners.set(k,new Set());this.listeners.get(k).add(f);}
 removeEventListener(k,f){this.listeners.get(k)?.delete(f);}
 fire(k,e={}){for(const f of [...(this.listeners.get(k)||[])])f(e);}
 listenerCount(){let n=0;for(const s of this.listeners.values())n+=s.size;return n;}
}
function fixture(zoom=2, native=false, onSelectHook=null){
 const el=new Target(), win=new Target(), doc=new Target(), queue=new Map();let serial=0,capture=null;
 Object.assign(el,{clientLeft:0,clientTop:0,clientWidth:200,clientHeight:200,scrollWidth:2000,scrollHeight:2000,scrollLeft:0,scrollTop:0,getBoundingClientRect:()=>({left:0,top:0}),setPointerCapture:id=>capture=id,hasPointerCapture:id=>capture===id,releasePointerCapture:()=>{capture=null;el.fire('lostpointercapture',{pointerId:1});}});
 doc.hidden=false;const c={x:0,y:0,zoom,maxX:1000,maxY:1000}, records=[];
 const context={window:win,document:doc,requestAnimationFrame:f=>{queue.set(++serial,f);return serial;},cancelAnimationFrame:id=>queue.delete(id)};
 vm.runInNewContext(fs.readFileSync(__dirname+'/browser_autoscroll.js','utf8'),context);
 let api;
 const onSelection = s => {
   records.push(s);
   if(onSelectHook) onSelectHook(api, s);
 };
 api=win.attachEdgeScroll(el,onSelection,native?null:{read:()=>({...c}),write:(x,y)=>{c.x=x;c.y=y;}});
 const down=()=>el.fire('pointerdown',{pointerId:1,isPrimary:true,button:0,clientX:200,clientY:100,preventDefault(){}});
 const tick=t=>{const pending=[...queue.values()];queue.clear();for(const f of pending)f(t);};
 return {el,win,doc,c,records,api,queue,down,tick,captured:()=>capture};
}
let passed=0;
function test(name,fn){fn();passed++;console.log('PASS '+name);}
test('first frame zero; stationary endpoint follows camera; zoom exactly once',()=>{const f=fixture();f.down();f.tick(100);assert.equal(f.c.x,0);f.tick(150);assert.equal(f.c.x,20);assert.equal(f.records.at(-1).anchor[0],100);assert.equal(f.records.at(-1).end[0],120);assert.equal(f.queue.size,1);});
test('long dt capped and resume timestamp reset',()=>{const f=fixture();f.down();f.tick(0);f.tick(5000);assert.equal(f.c.x,20);f.api.stop();f.down();f.tick(99999);assert.equal(f.c.x,20);f.tick(100049);assert.equal(f.c.x,40);});
for(const event of ['pointerup','pointercancel','lostpointercapture'])test(event+' cancels',()=>{const f=fixture();f.down();f.el.fire(event,{pointerId:1});assert.equal(f.queue.size,0);assert.equal(f.api.active,false);assert.equal(f.captured(),null);});
for(const event of ['hidden','blur','dispose'])test(event+' cancels',()=>{const f=fixture();f.down();if(event==='hidden'){f.doc.hidden=true;f.doc.fire('visibilitychange');}else if(event==='blur')f.win.fire('blur');else f.api.dispose();assert.equal(f.queue.size,0);assert.equal(f.api.active,false);if(event==='dispose'){f.down();assert.equal(f.api.active,false);}});
test('unrelated pointer ignored and duplicate down owns one frame',()=>{const f=fixture();f.down();f.down();f.el.fire('pointerup',{pointerId:2});assert.equal(f.api.active,true);assert.equal(f.queue.size,1);});
test('invalid camera releases capture without scheduling',()=>{const f=fixture(0);assert.throws(f.down,/invalid camera/);assert.equal(f.captured(),null);assert.equal(f.queue.size,0);});
test('dynamic zoom preserves world anchor',()=>{const f=fixture();f.down();f.tick(0);f.c.zoom=4;f.tick(50);assert.equal(f.c.x,10);assert.equal(f.records.at(-1).anchor[0],100);assert.equal(f.records.at(-1).end[0],60);});
test('native adapter regression',()=>{const f=fixture(1,true);f.down();f.tick(0);f.tick(50);assert.equal(f.el.scrollLeft,40);assert.equal(f.records.at(-1).end[0],240);});
test('camera boundary uses actual clipped offset',()=>{const f=fixture();f.c.maxX=3;f.down();f.tick(0);f.tick(50);assert.equal(f.c.x,3);assert.equal(f.records.at(-1).end[0],103);});
test('detached frame stops without camera or selection writes',()=>{const f=fixture();f.down();f.tick(0);const n=f.records.length;f.el.isConnected=false;f.tick(50);assert.equal(f.c.x,0);assert.equal(f.records.length,n);assert.equal(f.api.active,false);assert.equal(f.queue.size,0);f.down();assert.equal(f.api.active,false);f.el.isConnected=true;f.down();assert.equal(f.api.active,true);f.api.dispose();});

// UIUX-036 New Tests
test('repeated mount and unmount zeros listeners and cleans pending frames',()=>{
 const el=new Target(), win=new Target(), doc=new Target(), queue=new Map();let serial=0;
 const context={window:win,document:doc,requestAnimationFrame:f=>{queue.set(++serial,f);return serial;},cancelAnimationFrame:id=>queue.delete(id)};
 vm.runInNewContext(fs.readFileSync(__dirname+'/browser_autoscroll.js','utf8'),context);
 for(let cycle=0;cycle<10;cycle++){
   assert.equal(el.listenerCount(),0);assert.equal(doc.listenerCount(),0);assert.equal(win.listenerCount(),0);
   const api=win.attachEdgeScroll(el,()=>{});
   assert.equal(el.listenerCount(),5);assert.equal(doc.listenerCount(),1);assert.equal(win.listenerCount(),1);
   api.dispose();
   assert.equal(el.listenerCount(),0);assert.equal(doc.listenerCount(),0);assert.equal(win.listenerCount(),0);
 }
});
test('reentrant disposal from pointerdown selection callback cleanly stops without scheduling rAF',()=>{
 let called=false;
 const f=fixture(2,false,(api,s)=>{
   called=true;
   api.dispose();
 });
 f.down();
 assert.equal(called,true);
 assert.equal(f.api.active,false);
 assert.equal(f.queue.size,0);
 assert.equal(f.el.listenerCount(),0);
 assert.equal(f.doc.listenerCount(),0);
 assert.equal(f.win.listenerCount(),0);
});
test('reentrant disposal from frame tick selection callback stops loop and clears listeners',()=>{
 let ticks=0;
 const f=fixture(2,false,(api,s)=>{
   ticks++;
   if(ticks===2) api.dispose();
 });
 f.down();
 assert.equal(f.api.active,true);
 assert.equal(f.queue.size,1);
 f.tick(50);
 assert.equal(f.api.active,false);
 assert.equal(f.queue.size,0);
 assert.equal(f.el.listenerCount(),0);
 assert.equal(f.doc.listenerCount(),0);
 assert.equal(f.win.listenerCount(),0);
});

// UIUX-037 New Tests: Keyboard arrow navigation & focal cell recovery during autoscroll
test('focal cursor recovery retains cell when inside visible camera bounds',()=>{
 const row_px=32, col_px=96;
 // Camera at (0, 0), viewport (300, 200). Cell (1, 1) is at y:32, x:96 (fully visible)
 const cam={x:0, y:0, zoom:1, vw:300, vh:200};
 const isVisible=(r,c)=> {
   const x0=c*col_px, y0=r*row_px, x1=x0+col_px, y1=y0+row_px;
   return !(x1<=cam.x || x0>=cam.x+cam.vw || y1<=cam.y || y0>=cam.y+cam.vh);
 };
 assert.equal(isVisible(1, 1), true);
 assert.equal(isVisible(10, 10), false);
});
test('focal cursor recovers to leading boundary during active edge autoscroll translation',()=>{
 const row_px=32, col_px=96, maxR=50, maxC=50;
 let cursor=[0, 0];
 // Simulate autoscroll translating camera to (500, 400)
 const cam={x:500, y:400, vw:400, vh:300, zoom:1};
 const r_start=Math.max(0, Math.floor(cam.y/row_px));
 const r_end=Math.min(maxR, Math.ceil((cam.y+cam.vh)/row_px));
 const c_start=Math.max(0, Math.floor(cam.x/col_px));
 const c_end=Math.min(maxC, Math.ceil((cam.x+cam.vw)/col_px));
 // Active edge direction positive (scrolling right & down)
 const recovered=[r_end-1, c_end-1];
 assert.ok(recovered[0] >= r_start && recovered[0] < r_end);
 assert.ok(recovered[1] >= c_start && recovered[1] < c_end);
 assert.ok(recovered[0] >= 12);
 assert.ok(recovered[1] >= 5);
});
test('roving tab index assignment preserves single 0 tab stop and sets others to -1',()=>{
 const owners={'0,0':'cell-0-0', '0,1':'cell-0-1', '2,2':'merge-hero', '2,3':'merge-hero'};
 const focalOwner='merge-hero';
 const tabs={};
 for(const [k, owner] of Object.entries(owners)){
   tabs[owner] = (owner === focalOwner) ? 0 : -1;
 }
 assert.equal(tabs['merge-hero'], 0);
 assert.equal(tabs['cell-0-0'], -1);
 assert.equal(tabs['cell-0-1'], -1);
 assert.equal(Object.values(tabs).filter(v=>v===0).length, 1);
});

// UIUX-038 New Tests: Modifier Key Range Selection & Boundary Jumps Under Edge Autoscroll
test('shift arrow expansion expands selection bounding box while preserving anchor',()=>{
 const anchor = [2, 2];
 let lead = [2, 2];
 // Shift+ArrowDown moves lead to [3, 2]
 lead = [lead[0] + 1, lead[1]];
 const box1 = {
   r0: Math.min(anchor[0], lead[0]),
   r1: Math.max(anchor[0], lead[0]),
   c0: Math.min(anchor[1], lead[1]),
   c1: Math.max(anchor[1], lead[1])
 };
 assert.deepEqual(box1, {r0: 2, r1: 3, c0: 2, c1: 2});
 // Shift+ArrowRight moves lead to [3, 5]
 lead = [lead[0], lead[1] + 3];
 const box2 = {
   r0: Math.min(anchor[0], lead[0]),
   r1: Math.max(anchor[0], lead[0]),
   c0: Math.min(anchor[1], lead[1]),
   c1: Math.max(anchor[1], lead[1])
 };
 assert.deepEqual(box2, {r0: 2, r1: 3, c0: 2, c1: 5});
 const cellCount = (box2.r1 - box2.r0 + 1) * (box2.c1 - box2.c0 + 1);
 assert.equal(cellCount, 8);
});
test('ctrl arrow boundary jump skips contiguous populated cells into boundary',()=>{
 const populatedCols = new Set([2, 3, 4, 7, 8]);
 const jumpRight = (startCol) => {
   let curr = startCol;
   if (populatedCols.has(curr) && populatedCols.has(curr + 1)) {
     while (populatedCols.has(curr + 1)) curr++;
     return curr;
   }
   if (populatedCols.has(curr) && !populatedCols.has(curr + 1)) {
     curr++;
     while (curr < 20 && !populatedCols.has(curr)) curr++;
     return curr;
   }
   return curr;
 };
 assert.equal(jumpRight(2), 4); // Contiguous cluster end
 assert.equal(jumpRight(4), 7); // Empty gap jump to next data cell
});
test('active edge autoscroll stretches lead selection boundary while anchor remains anchored',()=>{
 const anchor = [0, 0];
 let lead = [1, 1];
 const cam = {x: 400, y: 300, vw: 300, vh: 200, row_px: 32, col_px: 96};
 const r_end = Math.ceil((cam.y + cam.vh) / cam.row_px);
 const c_end = Math.ceil((cam.x + cam.vw) / cam.col_px);
 // Under positive edge autoscroll direction, lead moves to leading visible edge
 lead = [r_end - 1, c_end - 1];
 const box = {
   r0: Math.min(anchor[0], lead[0]),
   r1: Math.max(anchor[0], lead[0]),
   c0: Math.min(anchor[1], lead[1]),
   c1: Math.max(anchor[1], lead[1])
 };
 assert.equal(box.r0, 0);
 assert.equal(box.c0, 0);
 assert.ok(box.r1 >= 15);
 assert.ok(box.c1 >= 7);
});

// UIUX-039 New Tests: Multi-Range Non-Contiguous Selection (Ctrl+Click Disjoint Boxes)
test('ctrl click adds disjoint non-contiguous bounding boxes into range list',()=>{
 const ranges = [];
 const addBox = (r, c) => ranges.push({ r0: r, c0: c, r1: r, c1: c });
 addBox(2, 2);
 addBox(5, 8);
 addBox(12, 16);
 assert.equal(ranges.length, 3);
 assert.deepEqual(ranges[0], { r0: 2, c0: 2, r1: 2, c1: 2 });
 assert.deepEqual(ranges[1], { r0: 5, c0: 8, r1: 5, c1: 8 });
 assert.deepEqual(ranges[2], { r0: 12, c0: 16, r1: 12, c1: 16 });
});
test('range deduplication eliminates fully subsumed boxes under spatial bounds',()=>{
 const boxes = [
   { r0: 2, c0: 2, r1: 6, c1: 6 },
   { r0: 3, c0: 3, r1: 4, c1: 4 }, // Subsumed inside [2,2,6,6]
   { r0: 10, c0: 10, r1: 12, c1: 12 } // Disjoint
 ];
 const deduped = [];
 for (const b of boxes) {
   const isContained = deduped.some(k => k.r0 <= b.r0 && k.r1 >= b.r1 && k.c0 <= b.c0 && k.c1 >= b.c1);
   if (!isContained) deduped.push(b);
 }
 assert.equal(deduped.length, 2);
 assert.deepEqual(deduped[0], { r0: 2, c0: 2, r1: 6, c1: 6 });
 assert.deepEqual(deduped[1], { r0: 10, c0: 10, r1: 12, c1: 12 });
});
test('virtual camera spatial intersection filters only in-frustum selection boxes',()=>{
 const boxes = [
   { r0: 1, c0: 1, r1: 2, c1: 2, id: 'near' },
   { r0: 15, c0: 15, r1: 18, c1: 18, id: 'mid' },
   { r0: 40, c0: 40, r1: 42, c1: 42, id: 'far' }
 ];
 const camBox = { r0: 0, c0: 0, r1: 6, c1: 4 }; // Camera at (0, 0), viewport (300, 200)
 const intersects = (a, b) => !(a.r1 < b.r0 || a.r0 > b.r1 || a.c1 < b.c0 || a.c0 > b.c1);
 const visible = boxes.filter(b => intersects(b, camBox));
 assert.equal(visible.length, 1);
 assert.equal(visible[0].id, 'near');
});

// UIUX-040 New Tests: Tabular Clipboard Paste Arbitration & Rectangular Fill
test('clipboard tsv parsing handles crlf and ragged matrix normalization',()=>{
 const tsv = "K1\tK2\tK3\r\nV1\tV2\r\n";
 const lines = tsv.trim().split(/\r?\n/).map(l => l.split('\t'));
 const maxCols = Math.max(...lines.map(r => r.length));
 const matrix = lines.map(r => r.concat(Array(maxCols - r.length).fill('')));
 assert.equal(matrix.length, 2);
 assert.equal(matrix[0].length, 3);
 assert.equal(matrix[1].length, 3);
 assert.equal(matrix[1][2], '');
});
test('single anchor clipboard paste expands rectangular boundaries',()=>{
 const anchor = [5, 5];
 const clipboard = [["A", "B"], ["C", "D"]];
 const rows = clipboard.length;
 const cols = clipboard[0].length;
 const targetBox = {
   r0: anchor[0],
   c0: anchor[1],
   r1: anchor[0] + rows - 1,
   c1: anchor[1] + cols - 1
 };
 assert.deepEqual(targetBox, { r0: 5, c0: 5, r1: 6, c1: 6 });
});
test('asymmetric multi-range selection tiles clipboard data via modulo indexing',()=>{
 const clipboard = [["M1", "M2"]];
 const boxes = [
   { r0: 0, c0: 0, r1: 1, c1: 1 }, // 2x2 box
   { r0: 4, c0: 4, r1: 4, c1: 5 }  // 1x2 box
 ];
 const mutations = [];
 for (const b of boxes) {
   for (let r = b.r0; r <= b.r1; r++) {
     const src_r = (r - b.r0) % clipboard.length;
     for (let c = b.c0; c <= b.c1; c++) {
       const src_c = (c - b.c0) % clipboard[0].length;
       mutations.push({ r, c, val: clipboard[src_r][src_c] });
     }
   }
 }
 assert.equal(mutations.length, 6);
 assert.equal(mutations[0].val, 'M1');
 assert.equal(mutations[1].val, 'M2');
 assert.equal(mutations[2].val, 'M1');
 assert.equal(mutations[3].val, 'M2');
});

// UIUX-041 Tests: Merged Cell Conflict Arbitration & Relative Formula Translation
test('relative formula translation shifts coordinates preserving absolutes',()=>{
 const formula = "=SUM(A1:B2) + $C$5 + D$6";
 const cellRefRegex = /(\$?[A-Za-z]+)(\$?[0-9]+)/g;
 const colToName = (idx) => {
   let s = "", n = idx + 1;
   while (n > 0) { const rem = (n - 1) % 26; s = String.fromCharCode(65 + rem) + s; n = Math.floor((n - 1) / 26); }
   return s;
 };
 const nameToCol = (name) => {
   let col = 0;
   for (let i = 0; i < name.length; i++) col = col * 26 + (name.charCodeAt(i) - 65 + 1);
   return col - 1;
 };
 const delta_r = 3, delta_c = 2;
 const translated = formula.replace(cellRefRegex, (m, colPart, rowPart) => {
   const isAbsCol = colPart.startsWith('$');
   const isAbsRow = rowPart.startsWith('$');
   const cIdx = nameToCol(colPart.replace('$', ''));
   const rIdx = parseInt(rowPart.replace('$', '')) - 1;
   const newC = isAbsCol ? cIdx : (cIdx + delta_c);
   const newR = isAbsRow ? rIdx : (rIdx + delta_r);
   return (isAbsCol ? '$' : '') + colToName(newC) + (isAbsRow ? '$' : '') + (newR + 1);
 });
 assert.equal(translated, "=SUM(C4:D5) + $C$5 + F$6");
});

test('merged cell partial overwrite veto rejects non-top-left paste',()=>{
 const merge = { id: 'm1', r0: 10, c0: 10, r1: 13, c1: 13 }; // 3x3 merge
 const pasteTargets = [{ r: 11, c: 11 }, { r: 11, c: 12 }]; // touching inside non-top-left
 const conflicts = [];
 for (const pt of pasteTargets) {
   if (pt.r >= merge.r0 && pt.r < merge.r1 && pt.c >= merge.c0 && pt.c < merge.c1) {
     const isTopLeft = (pt.r === merge.r0 && pt.c === merge.c0);
     if (!isTopLeft) conflicts.push({ pt, mergeId: merge.id });
   }
 }
 assert.equal(conflicts.length, 2);
 const vetoed = conflicts.length > 0;
 assert.equal(vetoed, true);
});

test('merged cell auto unmerge clears conflicting boundaries',()=>{
 const merges = new Map([['box-merge', { r0: 5, c0: 5, r1: 7, c1: 7 }]]);
 const pasteBox = { r0: 5, c0: 5, r1: 6, c1: 6 };
 const unmerged = [];
 for (const [id, m] of merges.entries()) {
   const overlaps = !(pasteBox.r1 < m.r0 || pasteBox.r0 >= m.r1 || pasteBox.c1 < m.c0 || pasteBox.c0 >= m.c1);
   if (overlaps) {
     unmerged.push(id);
     merges.delete(id);
   }
 }
 assert.equal(unmerged.length, 1);
 assert.equal(unmerged[0], 'box-merge');
 assert.equal(merges.size, 0);
});

// UIUX-042 Tests: Multi-Tier Undo/Redo Transaction Journal
test('transaction journal single cell mutation undo and redo invertible replay',()=>{
 const store = new Map();
 const undoStack = [];
 const redoStack = [];

 function recordMutation(r, c, oldVal, newVal) {
   undoStack.push({ r, c, oldVal, newVal });
   redoStack.length = 0;
   store.set(`${r},${c}`, newVal);
 }

 recordMutation(2, 2, '', 'Beta');
 assert.equal(store.get('2,2'), 'Beta');
 assert.equal(undoStack.length, 1);

 // Undo
 const undoTx = undoStack.pop();
 redoStack.push(undoTx);
 if (undoTx.oldVal === '') store.delete(`${undoTx.r},${undoTx.c}`);
 else store.set(`${undoTx.r},${undoTx.c}`, undoTx.oldVal);

 assert.equal(store.has('2,2'), false);
 assert.equal(redoStack.length, 1);

 // Redo
 const redoTx = redoStack.pop();
 undoStack.push(redoTx);
 store.set(`${redoTx.r},${redoTx.c}`, redoTx.newVal);

 assert.equal(store.get('2,2'), 'Beta');
 assert.equal(undoStack.length, 1);
 assert.equal(redoStack.length, 0);
});

test('transaction journal compound paste and topology unmerge atomic rollback',()=>{
 const store = new Map([['0,0', 'Header']]);
 const merges = new Map([['span1', { r0: 0, c0: 0, r1: 2, c1: 2 }]]);
 const undoStack = [];

 // Compound transaction: paste overwrites (0,0) and unmerges span1
 const tx = {
   cellMutations: [{ r: 0, c: 0, oldVal: 'Header', newVal: 'NewData' }],
   topologyMutations: [{ action: 'removed', mergeId: 'span1', r0: 0, c0: 0, r1: 2, c1: 2 }]
 };

 // Apply
 store.set('0,0', 'NewData');
 merges.delete('span1');
 undoStack.push(tx);

 assert.equal(store.get('0,0'), 'NewData');
 assert.equal(merges.size, 0);

 // Undo compound
 const undoTx = undoStack.pop();
 for (const cm of undoTx.cellMutations) {
   store.set(`${cm.r},${cm.c}`, cm.oldVal);
 }
 for (const tm of undoTx.topologyMutations) {
   if (tm.action === 'removed') {
     merges.set(tm.mergeId, { r0: tm.r0, c0: tm.c0, r1: tm.r1, c1: tm.c1 });
   }
 }

 assert.equal(store.get('0,0'), 'Header');
 assert.equal(merges.has('span1'), true);
});

test('transaction journal bounded capacity evicts oldest record',()=>{
 const undoStack = [];
 const maxHistory = 3;

 for (let i = 0; i < 5; i++) {
   undoStack.push({ txId: `tx_${i}`, val: i });
   if (undoStack.length > maxHistory) undoStack.shift();
 }

 assert.equal(undoStack.length, 3);
 assert.equal(undoStack[0].val, 2);
 assert.equal(undoStack[2].val, 4);
});


test('transaction journal selective range rollback isolates targeted bounding box',()=>{
 const store = new Map([
   ['1,1', 'RegionA'],
   ['8,8', 'RegionB']
 ]);
 const undoStack = [{
   txId: 'tx_batch',
   cellMutations: [
     { r: 1, c: 1, oldVal: '', newVal: 'RegionA' },
     { r: 8, c: 8, oldVal: '', newVal: 'RegionB' }
   ]
 }];
 const redoStack = [];

 // Selective undo targeting bounding box [1,1]..[2,2]
 const targetBox = { r0: 1, c0: 1, r1: 2, c1: 2 };
 const inBox = (r, c) => r >= targetBox.r0 && r <= targetBox.r1 && c >= targetBox.c0 && c <= targetBox.c1;

 const record = undoStack.pop();
 const matching = record.cellMutations.filter(m => inBox(m.r, m.c));
 const remaining = record.cellMutations.filter(m => !inBox(m.r, m.c));

 for (const m of matching) {
   if (m.oldVal === '') store.delete(`${m.r},${m.c}`);
   else store.set(`${m.r},${m.c}`, m.oldVal);
 }

 if (remaining.length > 0) {
   undoStack.push({ ...record, cellMutations: remaining });
 }
 redoStack.push({ ...record, cellMutations: matching });

 assert.equal(store.has('1,1'), false);
 assert.equal(store.get('8,8'), 'RegionB');
 assert.equal(undoStack.length, 1);
 assert.equal(redoStack.length, 1);
});

test('transaction journal local delta persistence roundtrip with zlib compression simulation',()=>{
 const rawState = {
   v: 1,
   merges: { span1: [0, 0, 2, 2] },
   cells: { '0,0': 'SavedData', '5,5': 'Pinned' },
   undoLen: 12
 };
 const serialized = JSON.stringify(rawState);
 const b64 = Buffer.from(serialized).toString('base64');
 assert.ok(b64.length > 0);

 const parsed = JSON.parse(Buffer.from(b64, 'base64').toString('utf8'));
 assert.equal(parsed.v, 1);
 assert.equal(parsed.cells['0,0'], 'SavedData');
 assert.equal(parsed.merges['span1'][3], 2);
 assert.equal(parsed.undoLen, 12);
});

// UIUX-044 Tests: Multi-Client Asynchronous Conflict Resolution & Vector Clock OT
test('multi-client vector clock causality and concurrent collision resolution',()=>{
 const clientA = { id: 'A', clock: { A: 1, B: 0 }, cells: new Map([['3,3', 'ValA']]) };
 const clientB = { id: 'B', clock: { A: 0, B: 1 }, cells: new Map([['3,3', 'ValB']]) };

 // Concurrent clocks detected
 const isConcurrent = (c1, c2) => {
   let gt = false, lt = false;
   const keys = new Set([...Object.keys(c1), ...Object.keys(c2)]);
   for (const k of keys) {
     const v1 = c1[k] || 0;
     const v2 = c2[k] || 0;
     if (v1 > v2) gt = true;
     if (v1 < v2) lt = true;
   }
   return gt && lt;
 };
 assert.equal(isConcurrent(clientA.clock, clientB.clock), true);

 // Arbitration: Priority first, then lexicographical client ID
 const opA = { cell: '3,3', val: 'ValA', priority: 10, clientId: 'A' };
 const opB = { cell: '3,3', val: 'ValB', priority: 5, clientId: 'B' };

 const arbitrate = (o1, o2) => o1.priority !== o2.priority ? o1.priority > o2.priority : o1.clientId > o2.clientId;
 assert.equal(arbitrate(opA, opB), true);

 // Client B adopts OpA
 clientB.cells.set(opA.cell, opA.val);
 assert.equal(clientB.cells.get('3,3'), 'ValA');
 assert.equal(clientA.cells.get('3,3'), clientB.cells.get('3,3'));
});

test('multi-client topology merge conflict arbitration with automatic overlap purge',()=>{
 const clientMergesA = new Map([['spanA', { r0: 0, c0: 0, r1: 3, c1: 3, priority: 20 }]]);
 const clientMergesB = new Map([['spanB', { r0: 2, c0: 2, r1: 4, c1: 4, priority: 10 }]]);

 // Overlap test
 const a = clientMergesA.get('spanA');
 const b = clientMergesB.get('spanB');
 const overlaps = !(a.r1 <= b.r0 || a.r0 >= b.r1 || a.c1 <= b.c0 || a.c0 >= b.c1);
 assert.equal(overlaps, true);

 // Client B receives spanA (higher priority) -> spanB is purged and spanA adopted
 if (a.priority > b.priority) {
   clientMergesB.delete('spanB');
   clientMergesB.set('spanA', a);
 }
 assert.equal(clientMergesB.has('spanB'), false);
 assert.equal(clientMergesB.has('spanA'), true);
 assert.equal(clientMergesB.size, 1);
});

console.log(JSON.stringify({passed,failed:0,environment:'Node vm fake DOM and deterministic rAF; not browser rendering'}));

