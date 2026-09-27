(async()=>{
  const checks=[];const check=(name,pass,details={})=>{checks.push({name,pass:!!pass,...details});if(!pass)throw Error(name);};
  const a=new FlowAudio({lifecycle:false});
  check('silent default',!a.ctx&&!a.enabled&&!a.cue('success','silent'));
  check('invalid event',!a.cue('unknown','bad'));
  a.setVolume(9);check('volume clamp',a.volume===0.15);
  let rejected=false;try{a.setVolume(NaN);}catch{rejected=true;}check('invalid volume rejected',rejected);
  const unavailable=new FlowAudio({factory:()=>{throw Error('unsupported');},lifecycle:false});
  try{await unavailable.enable();}catch{}check('unsupported stays off',!unavailable.enabled);await unavailable.close();
  for(const kind of ['success','failure']){
    const ctx=new OfflineAudioContext(1,24000,48000),master=ctx.createGain();master.gain.value=.08;master.connect(ctx.destination);
    FlowAudio.schedule(ctx,master,kind,.01);const data=(await ctx.startRendering()).getChannelData(0);
    let peak=0,energy=0,tail=0;for(let i=0;i<data.length;i++){peak=Math.max(peak,Math.abs(data[i]));energy+=data[i]*data[i];if(i>14400)tail=Math.max(tail,Math.abs(data[i]));}
    check(kind+' renders bounded signal',peak>0&&peak<=.04001&&energy>0&&tail===0,{peak,rms:Math.sqrt(energy/data.length),tail});
  }
  await a.close();check('closed controller cannot enable',!await a.enable());
  return {browser:navigator.userAgent,checks};
})()
