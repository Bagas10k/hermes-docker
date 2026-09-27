// SYNTHETIC data only. Object stream, not SSE or a network transport.
export function mockStream({seed=7,count=8,delay=15,scenario='success',signal,onEmit=()=>{}}={}) {
  if(!Number.isInteger(seed)||seed<0||seed>0xffffffff)throw new RangeError('seed must be uint32');
  if(!Number.isInteger(count)||count<0||count>10000)throw new RangeError('count must be 0..10000');
  if(!Number.isFinite(delay)||delay<0||delay>10000)throw new RangeError('delay must be 0..10000');
  if(!['success','empty','error'].includes(scenario))throw new RangeError('unknown scenario');
  let state=seed>>>0,index=0,stopped=false,timer,wake,controller;
  const cleanup=()=>{stopped=true;clearTimeout(timer);wake?.();signal?.removeEventListener('abort',abort);};
  const abort=()=>{if(!stopped){cleanup();controller.error(new DOMException('Synthetic run aborted','AbortError'));}};
  return new ReadableStream({
    start(c){controller=c;signal?.addEventListener('abort',abort,{once:true});if(signal?.aborted)abort();},
    async pull(c){
      if(stopped)return;
      if(scenario==='empty'||index===count){cleanup();c.close();return;}
      await new Promise(resolve=>{wake=resolve;timer=setTimeout(resolve,delay);});wake=undefined;
      if(stopped)return;
      if(scenario==='error'&&index===Math.min(2,count-1)){cleanup();c.error(new Error('Synthetic failure; retry success scenario'));return;}
      state=(Math.imul(state,1664525)+1013904223)>>>0;
      c.enqueue(Object.freeze({synthetic:true,id:++index,value:state%1000}));onEmit();
    },
    cancel(){cleanup();}
  },{highWaterMark:1});
}

// Fence every publication as well as aborting transport work.
export function createRunner(publish){
  let epoch=0,active;
  async function run(options={}){
    const runId=++epoch;active?.abort();active=new AbortController();
    let rows=[],reader;
    const emit=(status,error='')=>{if(runId===epoch)publish({runId,status,error,rows:[...rows],synthetic:true});};
    emit('loading');
    try{
      reader=mockStream({...options,signal:active.signal}).getReader();
      while(true){const {done,value}=await reader.read();if(runId!==epoch)return;if(done)break;rows=[...rows,value].slice(-20);emit('streaming');}
      emit(rows.length?'done':'empty');
    }catch(e){emit(e.name==='AbortError'?'aborted':'error',e.message);}
    finally{if(reader){await reader.cancel().catch(()=>{});reader.releaseLock();}}
  }
  return {run,reset:run,cancel(){active?.abort();}};
}
