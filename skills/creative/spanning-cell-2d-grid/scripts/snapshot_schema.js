// Contract: decoded JSON records, not adversarial objects with getters/proxies.
function validateSnapshot(d) {
 const fail=()=>{throw new TypeError('Invalid bounded grid snapshot');};
 const check=x=>{if(!x)fail();};
 const record=x=>x!==null&&typeof x==='object'&&!Array.isArray(x)&&Object.getPrototypeOf(x)===Object.prototype;
 const keys=(x,ks)=>record(x)&&Object.keys(x).length===ks.length&&ks.every(k=>Object.hasOwn(x,k));
 const int=(x,l,h)=>Number.isSafeInteger(x)&&x>=l&&x<=h;
 const pixel=x=>typeof x==='number'&&Number.isFinite(x)&&Math.abs(x)<=1e9;
 check(keys(d,['rows','cols','window','width','height','cells','owners']));
 check(int(d.rows,1,2147483647)&&int(d.cols,1,2147483647));
 check(Array.isArray(d.window)&&d.window.length===4&&d.window.every(x=>int(x,0,2147483647)));
 const [r0,c0,r1,c1]=d.window;
 check(r0<=r1&&r1<=d.rows&&c0<=c1&&c1<=d.cols);
 const area=(r1-r0)*(c1-c0);check(area<=4096);
 check(pixel(d.width)&&d.width>=0&&pixel(d.height)&&d.height>=0);
 check(Array.isArray(d.cells)&&d.cells.length<=area&&record(d.owners)&&Object.keys(d.owners).length===area);
 check((d.width===0)===(c0===c1)&&(d.height===0)===(r0===r1));
 if(!area)return d;
 const rh=d.height/(r1-r0),cw=d.width/(c1-c0), expected=new Map(),ids=new Set();
 for(const cell of d.cells){
  check(keys(cell,['id','row','col','rowspan','colspan','left','top','width','height']));
  check(typeof cell.id==='string'&&cell.id.length<=80&&/^(?:merge-[0-9]+|cell-[0-9]+-[0-9]+)$/.test(cell.id)&&!ids.has(cell.id));ids.add(cell.id);
  check(int(cell.row,0,2147483647)&&int(cell.col,0,2147483647)&&int(cell.rowspan,1,2147483647)&&int(cell.colspan,1,2147483647));
  const a=cell.row,b=cell.col,z=a+cell.rowspan,t=b+cell.colspan;
  check(z<=d.rows&&t<=d.cols&&a<r1&&z>r0&&b<c1&&t>c0);
  const geom={left:(b-c0)*cw,top:(a-r0)*rh,width:cell.colspan*cw,height:cell.rowspan*rh};
  check(Object.entries(geom).every(([k,v])=>pixel(cell[k])&&Math.abs(cell[k]-v)<=1e-6));
  for(let r=Math.max(a,r0);r<Math.min(z,r1);r++)for(let c=Math.max(b,c0);c<Math.min(t,c1);c++){
   const key=r+','+c;check(!expected.has(key));expected.set(key,cell.id);
  }
 }
 check(expected.size===area&&Object.entries(d.owners).every(([k,v])=>expected.has(k)&&expected.get(k)===v));
 return d;
}
