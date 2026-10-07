'use strict';
// Same controlled promises/timer replay against VM DOM and real Chromium DOM.
module.exports = async function clipboardChecks(timerDisposal = false) {
  const api = window.historyPreview, records = [], timers = new Map();
  const check = (ok, message) => { if (!ok) throw Error(message); };
  const record = name => records.push({name, pass:true});
  const button = () => document.getElementById('dag-breadcrumbs').querySelector('.dag-breadcrumb-copy-btn');
  const label = text => check(button().textContent === text, 'expected ' + text + ', got ' + button().textContent);
  const nativeSet = globalThis.setTimeout, nativeClear = globalThis.clearTimeout;
  let next = 0;
  globalThis.setTimeout = (cb, ms) => { check(ms === 1500, 'feedback duration'); timers.set(++next, cb); return next; };
  globalThis.clearTimeout = id => timers.delete(id);
  const defer = () => { let resolve, reject; const promise = new Promise((a,b) => {resolve=a; reject=b;}); return {promise,resolve,reject}; };
  const clipboard = writeText => Object.defineProperty(navigator, 'clipboard', {configurable:true,value:writeText ? {writeText} : undefined});
  const pending = () => { const d=defer(); clipboard(() => d.promise); return {...d, result:api.copyLineage()}; };
  try {
    if (timerDisposal) {
      clipboard(() => Promise.resolve()); await api.copyLineage();
      const saved=timers.values().next().value;
      check(timers.size===1, 'timer before disposal');
      check(api.disposeClipboard(), 'first disposal');
      check(timers.size===0, 'disposal clears feedback timer');
      const before=button().textContent; saved();
      check(button().textContent===before, 'saved timer inert');
      record('dispose-active-feedback-timer'); return records;
    }
    let d=pending(); label('Menyalin…'); check(!button().classList.contains('copied') && timers.size===0, 'pending not success');
    d.resolve(); const result=await d.result;
    check(result.success && result.text===api.lineage().join(' > '), 'fulfilled result'); label('Tersalin!');
    check(timers.size===1, 'one reset timer'); const reset=timers.values().next().value; timers.clear(); reset(); label('Salin Rute'); record('pending-fulfillment-reset');

    d=pending(); d.reject(Error('denied')); check(!(await d.result).success, 'rejected result'); label('Gagal menyalin'); check(!button().classList.contains('copied'), 'failure class'); record('rejection');
    clipboard(() => {throw Error('sync');}); check(!(await api.copyLineage()).success, 'sync failure'); label('Gagal menyalin'); record('synchronous-write-throw');

    clipboard(null);
    const focus=document.getElementById('outside'); focus.focus();
    for (const mode of [true,false,'throw']) {
      const before=document.body.children.length;
      document.execCommand = command => { check(command==='copy', 'copy command'); if(mode==='throw') throw Error('fallback'); return mode; };
      const r=await api.copyLineage(); check(r.success===(mode===true), 'fallback result');
      label(mode===true?'Tersalin!':'Gagal menyalin');
      check(document.body.children.length===before && document.activeElement===focus, 'textarea cleanup and focus');
      record('fallback-'+mode);
    }
    document.execCommand=undefined;
    check(!(await api.copyLineage()).success, 'missing API'); label('Gagal menyalin'); record('unavailable');

    const oldTimer=timers.values().next().value;
    const old=pending(); check(timers.size===0,'replace timer');
    const newer=pending(); newer.resolve(); await newer.result; label('Tersalin!');
    const currentTimer=timers.values().next().value;
    old.reject(Error('late')); await old.result; oldTimer(); label('Tersalin!');
    check(timers.size===1 && timers.values().next().value===currentTimer,'old work preserves new timer'); record('overlap-and-old-timer');

    api.refresh(); check(timers.size===0, 'rerender clears active timer');
    currentTimer(); label('Salin Rute');
    const oldButton=button(), oldClick = () => oldButton.click();
    d=pending(); api.refresh(); const fresh=button(); check(fresh!==oldButton && timers.size===0,'rerender invalidates');
    const retired=oldButton.textContent; d.resolve(); await d.result; currentTimer(); oldClick();
    label('Salin Rute'); check(oldButton.textContent===retired && timers.size===0,'retired work inert'); record('rerender');

    // Disposal with both a saved timer and an outstanding write.
    clipboard(() => Promise.resolve()); await api.copyLineage(); const saved=timers.values().next().value;
    d=pending(); check(api.disposeClipboard() && !api.disposeClipboard(),'idempotent dispose');
    const text=button().textContent; saved(); d.resolve(); await d.result;
    check(button().disabled && button().textContent===text && timers.size===0,'disposed callbacks inert');
    let writes=0; clipboard(() => { writes++; return Promise.resolve(); });
    check(!(await api.copyLineage()).success && writes===0,'disposed API inert');
    api.checkout('root'); api.search('root'); check(api.state().cursor==='root' && api.searchQuery()==='root','unrelated features live');
    check(button().disabled,'rerender remains disposed'); record('disposal');
    return records;
  } finally {globalThis.setTimeout=nativeSet; globalThis.clearTimeout=nativeClear;}
};
