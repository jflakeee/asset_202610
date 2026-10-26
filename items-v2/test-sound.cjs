const assert=require('node:assert/strict'),Sound=require('./sound');
let created=0,ended=[];
class AudioContext{
 constructor(){created++;this.state='suspended';this.currentTime=0;this.destination={};}
 async resume(){this.state='running';}
 createGain(){return {gain:{value:0,setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){},disconnect(){}};}
 createOscillator(){const o={frequency:{setValueAtTime(){}},connect(){},disconnect(){},start(){},stop(){ended.push(()=>o.onended());}};return o;}
}
(async()=>{
 global.AudioContext=AudioContext;
 const sound=new Sound();assert.equal(created,0);assert.equal(sound.play('pickup'),false);console.log('PASS silent until enabled');
 assert.equal(await sound.toggle(),true);assert.equal(created,1);assert.equal(sound.master.gain.value,.12);console.log('PASS opt-in creates one context');
 for(const event of ['pickup','heal','craft','chest','attack','hurt','kill']){sound.context.currentTime+=1;assert(sound.play(event));ended.splice(0).forEach(fn=>fn());assert.equal(sound.voices,0);}console.log('PASS seven cues release their audio nodes');
 assert(!sound.play('unknown'));assert(!sound.play('kill'));console.log('PASS invalid and duplicate cues suppressed');
 sound.context.currentTime+=1;assert(sound.play('chest'));assert(sound.play('heal'));assert(sound.play('craft'));assert(sound.play('attack'));assert.equal(sound.voices,12);assert(!sound.play('hurt'));console.log('PASS overlapping sounds bounded');
 sound.visibility(true);assert.equal(sound.master.gain.value,0);sound.visibility(false);assert.equal(sound.master.gain.value,.12);
 await sound.toggle();assert.equal(sound.master.gain.value,0);assert(!sound.play('pickup'));sound.visibility(false);assert.equal(sound.master.gain.value,0);console.log('PASS background and explicit mute');
 await sound.toggle();assert.equal(created,1);console.log('PASS context reused');
 global.AudioContext=class extends AudioContext{async resume(){throw Error('blocked')}};const blocked=new Sound();assert.equal(await blocked.toggle(),false);assert.equal(blocked.enabled,false);console.log('PASS rejected audio permission is nonfatal');
 delete global.AudioContext;assert.equal(await new Sound().toggle(),false);console.log('PASS unsupported browser stays silent');
})().catch(e=>{console.error(e);process.exitCode=1});
