/* Opt-in build sonification. No dependencies, network, or microphone. */
(function (root) {
  'use strict';
  class FlowAudio {
    constructor({ factory = () => new AudioContext({latencyHint:'interactive'}), visible = () => !document.hidden, clock = () => performance.now(), lifecycle = true } = {}) {
      this.factory=factory; this.visible=visible; this.clock=clock;
      this.ctx=null; this.master=null; this.enabled=false; this.disposed=false;
      this.volume=0.08; this.epoch=0; this.nodes=new Set(); this.seen=new Set(); this.last=-Infinity;
      this.onHidden=()=>{ if(!this.visible()) void this.mute().catch(()=>{}); };
      this.onHide=()=>{void this.mute().catch(()=>{});};
      this.lifecycle=lifecycle;
      if(lifecycle){document.addEventListener('visibilitychange',this.onHidden); window.addEventListener('pagehide',this.onHide);}
    }
    async enable(){
      if(this.disposed || !this.visible()) return false;
      const epoch=++this.epoch;
      try {
        if(!this.ctx){this.ctx=this.factory();this.master=this.ctx.createGain();this.master.gain.value=this.volume;this.master.connect(this.ctx.destination);}
        await this.ctx.resume();
        if(epoch!==this.epoch || this.disposed || !this.visible()) return false;
        this.enabled=this.ctx.state==='running'; return this.enabled;
      } catch(error){this.enabled=false;throw error;}
    }
    setVolume(value){
      if(!Number.isFinite(value)) throw new TypeError('Volume must be finite');
      this.volume=Math.max(0,Math.min(0.15,value));
      if(this.master && this.ctx.state!=='closed') this.master.gain.setTargetAtTime(this.volume,this.ctx.currentTime,0.015);
    }
    static schedule(ctx,destination,kind,when=ctx.currentTime+0.01){
      if(!['success','failure'].includes(kind)) throw new TypeError('Unknown cue');
      const osc=ctx.createOscillator(), gain=ctx.createGain();
      osc.type='sine';
      osc.frequency.setValueAtTime(kind==='success'?440:330,when);
      osc.frequency.setValueAtTime(kind==='success'?660:220,when+0.10);
      gain.gain.setValueAtTime(0,when);
      gain.gain.linearRampToValueAtTime(0.5,when+0.012);
      gain.gain.setValueAtTime(0.5,when+0.16);
      gain.gain.linearRampToValueAtTime(0,when+0.22);
      osc.connect(gain);gain.connect(destination);
      osc.start(when);osc.stop(when+0.23);
      return {osc,gain};
    }
    cue(kind,id){
      if(!['success','failure'].includes(kind) || typeof id!=='string' || !id || id.length>256) return false;
      if(this.seen.has(id)) return false;
      this.seen.add(id);if(this.seen.size>128)this.seen.delete(this.seen.values().next().value);
      if(!this.enabled || this.disposed || !this.visible() || this.ctx?.state!=='running')return false;
      const now=this.clock();if(now-this.last<500 || this.nodes.size) return false;
      this.last=now;
      const node=FlowAudio.schedule(this.ctx,this.master,kind);
      this.nodes.add(node);
      node.osc.onended=()=>{node.osc.disconnect();node.gain.disconnect();this.nodes.delete(node);};
      return true;
    }
    clear(){for(const node of this.nodes){node.osc.onended=null;try{node.osc.stop();}catch{}node.osc.disconnect();node.gain.disconnect();}this.nodes.clear();}
    async mute(){++this.epoch;this.enabled=false;this.clear();if(this.ctx && this.ctx.state!=='closed')await this.ctx.suspend();}
    async close(){if(this.disposed)return;this.disposed=true;++this.epoch;this.enabled=false;this.clear();if(this.lifecycle){document.removeEventListener('visibilitychange',this.onHidden);window.removeEventListener('pagehide',this.onHide);}if(this.ctx && this.ctx.state!=='closed')await this.ctx.close();}
  }
  root.FlowAudio=FlowAudio;
})(globalThis);
