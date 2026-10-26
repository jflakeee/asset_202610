const assert=require('node:assert/strict'),Arena=require('./arena-core');let count=0;
function test(name,fn){fn();console.log('PASS',name);count++}
function active(){const a=new Arena();a.paused=false;return a}
const grant=()=>({ok:true});
test('starts paused and reset prevents unattended combat',()=>{const a=new Arena();a.step(.05,{x:1},grant);assert.equal(a.player.x,200);assert.equal(a.enemies[0].hp,5);a.paused=false;a.reset();assert(a.paused)});
test('nearby enemies pursue while distant enemies wait',()=>{const a=active();a.step(.05,{},grant);assert(a.enemies[0].x<290);assert.equal(a.enemies[2].x,600)});
test('contact damage is shared across enemies with one second protection',()=>{const a=active();a.enemies=[{x:232,y:200,hp:100},{x:200,y:232,hp:100}];let damage=0;for(let i=0;i<20;i++)a.step(.05,{},grant,n=>damage+=n);assert.equal(damage,8);a.step(.05,{},grant,n=>damage+=n);assert.equal(damage,16)});
test('kill produces exactly one drop and dead enemy cannot strike',()=>{const a=active();a.enemies=[{x:232,y:200,hp:1}];let damage=0;for(let i=0;i<100;i++)a.step(.05,{},grant,n=>damage+=n);assert.equal(a.kills,1);assert.equal(a.drops.length,1);assert.equal(damage,0)});
test('approach grants once and records pickup effect',()=>{const a=active();a.enemies=[];a.drops=[{id:'test',x:230,y:200}];let grants=0;for(let i=0;i<6;i++)a.step(.05,{x:1},()=>{grants++;return {ok:true}});assert.equal(grants,1);assert.equal(a.picked,1);assert(a.effects.some(e=>e.text==='+3 동전'))});
test('paused frame freezes movement damage and effects',()=>{const a=active();a.effects=[{life:.5}];a.paused=true;a.step(.05,{x:1},grant,()=>assert.fail());assert.equal(a.player.x,200);assert.equal(a.effects[0].life,.5)});
test('normalized diagonal movement and bounds',()=>{const a=active();a.enemies=[];a.step(.05,{x:1,y:1},grant);assert(Math.abs(Math.hypot(a.player.x-200,a.player.y-200)-9)<1e-8);for(let i=0;i<1000;i++)a.step(.05,{x:-1},grant);assert.equal(a.player.x,16)});
test('failed grant remains recoverable; duplicate is removed without count',()=>{const a=active();a.drops=[{id:'x',x:200,y:200}];a.step(.05,{},()=>({ok:false,reason:'overflow'}));assert.equal(a.drops.length,1);a.step(.05,{},()=>({ok:false,reason:'duplicate'}));assert.equal(a.drops.length,0);assert.equal(a.picked,0)});
test('effects expire and long frame does not teleport enemies',()=>{const a=active();a.effects=[{life:.01}];a.step(50,{},grant);assert.equal(a.enemies[0].x,286.5);assert(!a.effects.some(e=>!e.text))});
console.log(count+' passed');
