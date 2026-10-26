(function(root){'use strict';
// Original synthesized cues; no downloaded recordings or external audio files.
const tones={pickup:[660,990],heal:[392,523,784],craft:[330,440,660],chest:[523,659,784,1047],attack:[180,100],hurt:[110,65],kill:[220,440]};
class TrailSound{
 constructor(){this.context=null;this.master=null;this.enabled=false;this.voices=0;this.last=new Map();}
 async toggle(){
  if(this.enabled){this.enabled=false;this.master.gain.value=0;return false;}
  try{
   if(!this.context){const Context=root.AudioContext||root.webkitAudioContext;if(!Context)throw Error('unsupported');this.context=new Context();this.master=this.context.createGain();this.master.gain.value=0;this.master.connect(this.context.destination);}
   await this.context.resume();if(this.context.state!=='running')throw Error('suspended');
   this.enabled=true;this.master.gain.value=.12;return true;
  }catch{this.enabled=false;if(this.master)this.master.gain.value=0;return false;}
 }
 visibility(hidden){if(this.master)this.master.gain.value=(this.enabled&&!hidden) ? .12 : 0;}
 play(name){
  const notes=tones[name],ctx=this.context;
  if(!this.enabled||!notes||!ctx||ctx.state!=='running'||root.document?.hidden||this.voices+notes.length>12)return false;
  const now=ctx.currentTime;if(now-(this.last.get(name)??-Infinity)<.08)return false;this.last.set(name,now);
  try{
   notes.forEach((frequency,i)=>{
    const oscillator=ctx.createOscillator(),gain=ctx.createGain(),start=now+i*.065;
    oscillator.type=name==='hurt'?'triangle':'sine';oscillator.frequency.setValueAtTime(frequency,start);
    gain.gain.setValueAtTime(0,start);gain.gain.linearRampToValueAtTime(.7,start+.008);gain.gain.exponentialRampToValueAtTime(.001,start+.12);
    oscillator.connect(gain);gain.connect(this.master);this.voices++;
    oscillator.onended=()=>{oscillator.disconnect();gain.disconnect();this.voices--;};oscillator.start(start);oscillator.stop(start+.13);
   });return true;
  }catch{return false;}
 }
}
if(typeof module!=='undefined')module.exports=TrailSound;else root.TrailSound=TrailSound;
})(globalThis);
