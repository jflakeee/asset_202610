const assert=require('node:assert/strict'),Arena=require('./arena-core'),Reward=require('./reward-core');
const ids=['resource.wood','resource.iron_ore','material.rope','reward.chest','currency.coin','consumable.health_potion'];
const config={healAmount:30,chestCoins:10,damageAmount:25,recipes:[{id:'chest',costs:{'resource.wood':2,'resource.iron_ore':1,'material.rope':1},output:{item:'reward.chest',quantity:1}}]};
let count=0;function test(name,fn){fn();count++;console.log('PASS',name)}
test('walk, collect, craft and open produces ten coins',()=>{
 const arena=new Arena(),state=new Reward(ids,config);arena.paused=false;arena.enemies=[];
 for(const node of [...arena.resources]){for(let i=0;i<100&&arena.resources.includes(node);i++){const dx=node.x-arena.player.x,dy=node.y-arena.player.y,n=Math.hypot(dx,dy);arena.step(.05,{x:dx/n,y:dy/n},drop=>state.claim(drop));}assert(!arena.resources.includes(node));}
 assert.equal(arena.gathered,3);assert.equal(state.inventory['resource.wood'],2);assert(state.craft('chest').ok);assert(state.openChest().ok);assert.equal(state.inventory['currency.coin'],10);assert.equal(state.inventory['resource.wood'],0);assert(!state.craft('chest').ok);
});
test('distant and paused resources cannot be collected',()=>{const a=new Arena();let calls=0;a.step(.05,{x:-1},()=>{calls++;return {ok:true}});a.paused=false;a.step(.05,{},()=>{calls++;return {ok:true}});assert.equal(calls,0);assert.equal(a.resources.length,3)});
test('overflow keeps resource, then retry grants once',()=>{const a=new Arena();a.paused=false;a.player={x:120,y:200};a.step(.05,{},()=>({ok:false,reason:'overflow'}));assert.equal(a.resources.length,3);let calls=0;for(let i=0;i<5;i++)a.step(.05,{},()=>{calls++;return {ok:true}});assert.equal(calls,1);assert.equal(a.gathered,1)});
test('duplicate resource is removed without recounting',()=>{const a=new Arena();a.paused=false;a.player={x:120,y:200};a.step(.05,{},()=>({ok:false,reason:'duplicate'}));assert.equal(a.resources.length,2);assert.equal(a.gathered,0)});
test('joint reset restores resource claims and inventory',()=>{const a=new Arena(),s=new Reward(ids,config);a.paused=false;a.player={x:120,y:200};a.step(.05,{},d=>s.claim(d));s.reset();a.reset();assert.equal(a.resources.length,3);assert.equal(a.gathered,0);assert.equal(s.inventory['resource.wood'],0);assert(s.claim(a.resources[0]).ok)});
console.log(count+' passed');
