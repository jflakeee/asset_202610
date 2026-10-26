const assert=require('node:assert/strict'),Arena=require('./arena-core');let n=0;function test(name,fn){fn();n++;console.log('PASS',name)}
test('kill produces one drop',()=>{let a=new Arena();for(let i=0;i<200;i++)a.step(.05,{},()=>({ok:true}));assert.equal(a.kills,1);assert.equal(a.drops.length,1)});
test('approach grants once',()=>{let a=new Arena(),grants=0;for(let i=0;i<30;i++)a.step(.05,{},()=>({ok:true}));for(let i=0;i<12;i++)a.step(.05,{x:1},()=>{grants++;return {ok:true}});assert.equal(grants,1);assert.equal(a.picked,1)});
test('paused scene does not progress',()=>{let a=new Arena();a.paused=true;a.step(.05,{x:1},()=>({ok:true}));assert.equal(a.player.x,200);assert.equal(a.enemies[0].hp,3)});
test('boundaries and diagonal speed',()=>{let a=new Arena();a.step(.05,{x:1,y:1},()=>({ok:true}));assert(Math.abs(Math.hypot(a.player.x-200,a.player.y-200)-9)<1e-8);for(let i=0;i<1000;i++)a.step(.05,{x:-1},()=>({ok:true}));assert.equal(a.player.x,16)});
test('failed grant remains recoverable',()=>{let a=new Arena();a.drops=[{id:'x',x:200,y:200}];a.step(.05,{},()=>({ok:false,reason:'overflow'}));assert.equal(a.drops.length,1);a.step(.05,{},()=>({ok:true}));assert.equal(a.drops.length,0)});
test('reset restores training enemies',()=>{let a=new Arena();a.enemies[0].hp=0;a.kills=1;a.reset();assert.equal(a.kills,0);assert.equal(a.enemies[0].hp,3)});console.log(n+' passed');
