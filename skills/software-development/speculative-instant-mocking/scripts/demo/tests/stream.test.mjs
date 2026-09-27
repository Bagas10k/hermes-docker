import test from 'node:test';
import assert from 'node:assert/strict';
const module = await import('../stream.mjs').catch(() => ({}));
test('deterministic labelled stream', async () => {
  assert.equal(typeof module.mockStream, 'function');
  const collect = async () => { const out=[]; for await (const x of module.mockStream({seed:7, count:4, delay:0})) out.push(x); return out; };
  const a=await collect(); assert.deepEqual(a,await collect());
  assert.equal(a.length,4); assert.ok(a.every(x=>x.synthetic===true));
});
