(async () => {
const checks=[];const check=(name,pass)=>{checks.push({name,pass:!!pass});if(!pass)throw Error(name)};
const status=document.querySelector('#status'),input=document.querySelector('#source'),button=document.querySelector('#validate');
input.value='{';button.click();check('real JSON syntax error',status.dataset.kind==='error');
input.value='{"fixed":true}';button.click();check('real editor recovery',status.dataset.kind==='success' && document.querySelector('#output').textContent.includes('true'));
check('motion default off',status.getAnimations().length===0);
document.querySelector('#motion').click(); await new Promise(r=>setTimeout(r,1510));
cue.update('error','Error readable');check('one bounded effect',status.getAnimations().length===1 && status.textContent==='Error readable');
for(let i=0;i<100;i++)cue.update('success','Latest '+i);
check('burst latest wins and cooldown',status.textContent==='Latest 99' && status.getAnimations().length===0);
await new Promise(r=>setTimeout(r,1510));cue.update('success','Success');await new Promise(r=>setTimeout(r,350));check('effect naturally terminates',status.getAnimations().length===0 && cue.animation===null);
cue.update('error','<img src=x onerror=alert(1)>');check('diagnostics are text',status.children.length===0);
check('semantic status',status.getAttribute('role')==='status' && status.getAttribute('aria-live')==='polite');
const original=status.animate;status.animate=undefined;await new Promise(r=>setTimeout(r,1510));check('unsupported API graceful',cue.update('success','Fallback') && status.textContent==='Fallback');status.animate=original;
cue.setEnabled(false);cue.update('error','Static error');check('manual disable',status.getAnimations().length===0);
let rejected=false;try{cue.update('bogus','x')}catch{rejected=true}check('invalid kind rejected',rejected);
cue.dispose();check('disposed rejects updates',cue.update('success','No')===false && status.getAnimations().length===0);
window.cue=new KineticStatus(status);return {checks,passed:checks.length,userAgent:navigator.userAgent};
})()
