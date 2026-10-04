"""Bounded fixed-size viewport adapter; not a production grid widget."""
import json
from spanning_grid import SpanIndex


def snapshot(index, window, row_px=32, col_px=96, budget=4096):
    index._validate(*window)
    if any(type(x) is not int or x <= 0 for x in (row_px, col_px, budget)):
        raise ValueError('Positive integer sizes and budget required')
    r0, c0, r1, c1 = window
    if (r1-r0)*(c1-c0) > budget:
        raise ValueError('Viewport exceeds cell budget')
    owners = {}
    cells = []
    for hit in index.query(*window):
        a,b,c,d = hit['bounds']
        x,y,z,w = hit['clip']
        ident = 'merge-' + str(hit['id'])
        cells.append(dict(id=ident, row=a, col=b, rowspan=c-a, colspan=d-b,
                          left=(b-c0)*col_px, top=(a-r0)*row_px,
                          width=(d-b)*col_px, height=(c-a)*row_px))
        for r in range(x,z):
            for col in range(y,w):
                owners[f'{r},{col}'] = ident
    for r in range(r0,r1):
        for c in range(c0,c1):
            key=f'{r},{c}'
            if key not in owners:
                ident=f'cell-{r}-{c}'
                owners[key]=ident
                cells.append(dict(id=ident,row=r,col=c,rowspan=1,colspan=1,
                                  left=(c-c0)*col_px,top=(r-r0)*row_px,
                                  width=col_px,height=row_px))
    return dict(rows=index.rows, cols=index.cols, window=list(window),
                width=(c1-c0)*col_px, height=(r1-r0)*row_px,
                cells=sorted(cells,key=lambda c:(c['row'],c['col'])), owners=owners)


def render_html(data):
    from pathlib import Path
    from snapshot_schema import validate_snapshot
    validate_snapshot(data)
    validator = Path(__file__).with_name('snapshot_schema.js').read_text()
    payload=json.dumps(data).replace('<','\\u003c')
    return '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Merged grid verification fixture</title>
<style>*{box-sizing:border-box}body{margin:0;padding:8px;background:#faf8f5;color:#17212b;font:14px sans-serif}
#frame{max-width:100%;overflow:auto}#grid{position:relative;overflow:hidden;background:white}
[role=row]{position:absolute;left:0;top:0;width:100%;height:0}
[role=gridcell]{position:absolute;border:1px solid #64748b;padding:3px;overflow:hidden;background:#fff}
[role=gridcell]:focus{outline:3px solid #1669e8;outline-offset:-3px}</style>
<div id="frame"><div id="grid" role="grid" aria-label="Merged grid test"></div></div>
<script>'''+validator+'''\nlet data='''+payload+''';
const grid=document.getElementById('grid');
let nodes=new Map(),cursor=null;
function select(r,c,focus=true){const id=data.owners[r+','+c];if(!id)return;
 for(const n of nodes.values())n.tabIndex=-1;
 cursor=[r,c];const n=nodes.get(id);n.tabIndex=0;if(focus)n.focus({preventScroll:true});}
function replaceWindow(next){
 validateSnapshot(next);
 const owned=grid.contains(document.activeElement), oldCursor=cursor?cursor.slice():null;
 const [r0,c0,r1,c1]=next.window;
 const point=r0===r1||c0===c1?null:[Math.min(Math.max(oldCursor?.[0]??r0,r0),r1-1),Math.min(Math.max(oldCursor?.[1]??c0,c0),c1-1)];
 const fragment=document.createDocumentFragment(),rows=new Map(),fresh=new Map();
 
 // Phase 1: Build virtual nodes in detached fragment (can throw if hook/injection fails)
 if(window.__failCommitPhase==='create_nodes')throw new Error('Injected failure during create_nodes');
 for(const cell of next.cells){
  let row=rows.get(cell.row);
  if(!row){row=document.createElement('div');row.setAttribute('role','row');row.setAttribute('aria-rowindex',cell.row+1);fragment.append(row);rows.set(cell.row,row);}
  const n=document.createElement('div');n.id=cell.id;n.setAttribute('role','gridcell');
  for(const [attr,value] of Object.entries({'aria-rowindex':cell.row+1,'aria-colindex':cell.col+1,'aria-rowspan':cell.rowspan,'aria-colspan':cell.colspan}))n.setAttribute(attr,value);
  for(const k of ['left','top','width','height'])n.style[k]=cell[k]+'px';
  n.textContent=cell.id;n.tabIndex=-1;row.append(n);fresh.set(cell.id,n);
 }

 // Phase 2: Transactional DOM mutation and checkpoint preservation
 const oldChildren=Array.from(grid.childNodes);
 const oldWidth=grid.style.width, oldHeight=grid.style.height;
 const oldRowCount=grid.getAttribute('aria-rowcount'), oldColCount=grid.getAttribute('aria-colcount');
 const oldTabIndex=grid.tabIndex;
 const oldData=data, oldNodes=nodes;

 try {
  if(window.__failCommitPhase==='dom_mutation')throw new Error('Injected failure during dom_mutation');
  data=next;nodes=fresh;cursor=point;
  grid.style.width=data.width+'px';grid.style.height=data.height+'px';
  grid.setAttribute('aria-rowcount',data.rows);grid.setAttribute('aria-colcount',data.cols);
  grid.replaceChildren(fragment);grid.tabIndex=point?-1:0;

  // Phase 3: Focus restoration
  if(window.__failCommitPhase==='focus_restore')throw new Error('Injected failure during focus_restore');
  if(point)select(...point,owned);else if(owned)grid.focus({preventScroll:true});
 } catch(err) {
  // ATOMIC ROLLBACK: restore previous DOM children, attributes, and logical state
  grid.replaceChildren(...oldChildren);
  grid.style.width=oldWidth;grid.style.height=oldHeight;
  if(oldRowCount!==null)grid.setAttribute('aria-rowcount',oldRowCount);else grid.removeAttribute('aria-rowcount');
  if(oldColCount!==null)grid.setAttribute('aria-colcount',oldColCount);else grid.removeAttribute('aria-colcount');
  grid.tabIndex=oldTabIndex;
  data=oldData;nodes=oldNodes;cursor=oldCursor;
  if(oldCursor&&oldNodes.size>0)select(...oldCursor,owned);
  throw err;
 }

 return {cursor:cursor?.slice()??null,owner:cursor?data.owners[cursor.join(',')]:null};
}
replaceWindow(data);
grid.addEventListener('keydown',e=>{
 const dirs={ArrowRight:[0,1],ArrowLeft:[0,-1],ArrowDown:[1,0],ArrowUp:[-1,0]};
 if(!dirs[e.key]||!cursor)return;e.preventDefault();const [dr,dc]=dirs[e.key];
 let [r,c]=cursor;const id=data.owners[r+','+c];
 do{r+=dr;c+=dc;}while(data.owners[r+','+c]===id);
 select(r,c);
});
grid.addEventListener('focusin',e=>{
 if(!cursor)return;
 const id=data.owners[cursor.join(',')];if(e.target.id===id)return;
 const entry=Object.entries(data.owners).find(([,v])=>v===e.target.id);
 if(entry)select(...entry[0].split(',').map(Number),false);
});
// Tokens represent latest issued requests, not server data versions.
let issuedRevision=0,appliedRevision=0;
window.beginSnapshotRequest=()=>{
 if(issuedRevision>=Number.MAX_SAFE_INTEGER)throw new RangeError('Revision exhausted');
 return ++issuedRevision;
};
window.applySnapshot=(revision,next)=>{
 if(!Number.isSafeInteger(revision)||revision<=0)throw new TypeError('Invalid revision');
 if(revision!==issuedRevision||revision<=appliedRevision)return false;
 try {
  replaceWindow(next);
  appliedRevision=revision;
  return true;
 } catch(e) {
  // Commit failure preserves previous appliedRevision and state
  return false;
 }
};
window.revisionState=()=>({issued:issuedRevision,applied:appliedRevision});
// Direct replacement remains a trusted synchronous fixture API only.
window.replaceWindow=replaceWindow;
window.gridState=()=>({cursor:cursor?.slice()??null,owner:cursor?data.owners[cursor.join(',')]:null});
window.fixtureReady=true;
</script></html>'''


if __name__ == '__main__':
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser()
    parser.add_argument('output')
    args=parser.parse_args()
    with SpanIndex(20,20) as index:
        index.add(7,1,1,4,4)
        Path(args.output).write_text(render_html(snapshot(index,(2,2,6,6))),encoding='utf-8')
