const vm=require('node:vm'),fs=require('node:fs'),assert=require('node:assert/strict');
function element(){return {textContent:'',listeners:{},addEventListener(name,fn){this.listeners[name]=fn},getContext(){return {}}}}
const canvas=element(),button=element(),status=element(),document=element(),window=element();let arena;
document.querySelector=s=>({'#arena':canvas,'#pause-arena':button,'#arena-status':status}[s]);document.hidden=false;
class Arena{constructor(){arena=this;this.reset()}reset(){this.paused=true}}
const context={document,window,TrailArena:Arena,Image:class{},requestAnimationFrame(){},Map,Set,Math};vm.createContext(context);
vm.runInContext(fs.readFileSync(__dirname+'/arena-view.js','utf8'),context);
const controller=context.mountArena({},()=>{},[{id:'currency.coin',icon:'coin.png'}],{});
button.onclick();assert.equal(arena.paused,false);
window.listeners.blur();assert.equal(arena.paused,true);assert.equal(button.textContent,'전투 재개');
button.onclick();document.hidden=true;document.listeners.visibilitychange();assert.equal(arena.paused,true);
document.hidden=false;document.listeners.visibilitychange();assert.equal(arena.paused,true);
button.onclick();assert.equal(arena.paused,false);controller.pause();assert.equal(arena.paused,true);
controller.reset();assert.equal(button.textContent,'전투 시작');
console.log('PASS window blur, hidden tab, manual resume, shared pause and reset');
