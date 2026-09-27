import test from 'node:test';
import assert from 'node:assert/strict';
import * as m from '../stream.mjs';
const collect = async s => {const a=[]; for await(const x of s)a.push(x);return a;};
test('empty, error and deterministic recovery',async()=>{
 assert.deepEqual(await collect(m.mockStream({scenario:'empty',delay:0})),[]);
 await assert.rejects(()=>collect(m.mockStream({scenario:'error',delay:0})),/Synthetic failure/);
 assert.equal((await collect(m.mockStream({delay:0}))).length,8);
});
test('abort wakes pending read and pre-abort rejects',async()=>{
 const ac=new AbortController(); const r=m.mockStream({signal:ac.signal,delay:1000}).getReader();
 const pending=r.read();ac.abort();await assert.rejects(pending,{name:'AbortError'});
 await assert.rejects(()=>m.mockStream({signal:ac.signal}).getReader().read(),{name:'AbortError'});
});
test('reader cancellation and backpressure bound generation',async()=>{
 let n=0; const s=m.mockStream({delay:0,count:100,onEmit:()=>n++});
 await new Promise(r=>setTimeout(r,30));assert.equal(n,1);
 const r=s.getReader();await r.cancel();await new Promise(r=>setTimeout(r,20));assert.equal(n,1);
 const pending=m.mockStream({delay:50}).getReader();const read=pending.read();await pending.cancel();assert.equal((await read).done,true);
});
test('bad input rejected',()=>{
 for(const o of [{count:-1},{count:10001},{seed:NaN},{delay:Infinity},{scenario:'oops'}])assert.throws(()=>m.mockStream(o));
});
test('latest run fences old callbacks, reset replays and view is bounded',async()=>{
 assert.equal(typeof m.createRunner,'function');const states=[];
 const runner=m.createRunner(s=>states.push(s));
 const old=runner.run({seed:1,count:20,delay:30}); const fresh=runner.run({seed:7,count:30,delay:0});
 await Promise.all([old,fresh]);const last=states.at(-1);assert.equal(last.status,'done');assert.equal(last.rows.length,20);assert.equal(last.rows.at(-1).id,30);
 assert.ok(states.filter(s=>s.rows.length).every(s=>s.runId===2));
 await runner.reset({seed:7,count:30,delay:0}); assert.deepEqual(states.at(-1).rows,last.rows);
 const pending=runner.run({delay:1000});runner.cancel();await pending;assert.equal(states.at(-1).status,'aborted');
});
