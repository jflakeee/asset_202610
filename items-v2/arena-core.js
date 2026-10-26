(function(root){'use strict';
class Arena {
 constructor(){this.reset();}
 reset(){this.player={x:200,y:200};this.enemies=[{x:290,y:200,hp:5},{x:460,y:130,hp:5},{x:600,y:300,hp:5}];this.drops=[];this.cooldown=0;this.invulnerable=0;this.effects=[];this.serial=0;this.kills=0;this.picked=0;this.paused=true;}
 step(dt,input,claim,hurt=()=>{}){
  if(this.paused)return;dt=Number.isFinite(dt)?Math.min(Math.max(dt,0),.05):0;
  this.effects=this.effects.filter(e=>(e.life-=dt)>0);
  let x=input.x||0,y=input.y||0,n=Math.hypot(x,y);if(n>1){x/=n;y/=n;}
  this.player.x=Math.max(16,Math.min(784,this.player.x+x*180*dt));this.player.y=Math.max(16,Math.min(384,this.player.y+y*180*dt));
  this.cooldown=Math.max(0,this.cooldown-dt);this.invulnerable=Math.max(0,this.invulnerable-dt);
  const distance=e=>Math.hypot(e.x-this.player.x,e.y-this.player.y);
  for(const e of this.enemies){const d=distance(e);if(e.hp>0&&d<=260&&d>32){const move=Math.min(70*dt,d-32);e.x+=(this.player.x-e.x)/d*move;e.y+=(this.player.y-e.y)/d*move;}}
  const target=this.enemies.filter(e=>e.hp>0).sort((a,b)=>distance(a)-distance(b))[0];
  if(target&&distance(target)<=115&&this.cooldown===0){target.hp--;this.cooldown=.45;this.effects.push({x:target.x,y:target.y,text:'−1',color:'#fff1b2',life:.4});if(target.hp===0){this.kills++;this.drops.push({id:'arena:'+this.serial++,item:'currency.coin',quantity:3,x:target.x,y:target.y});}}
  if(this.invulnerable===0&&this.enemies.some(e=>e.hp>0&&distance(e)<=33)){hurt(8);this.invulnerable=1;this.effects.push({x:this.player.x,y:this.player.y,text:'−8 HP',color:'#ffab9b',life:.6});}
  this.drops=this.drops.filter(d=>{if(distance(d)>28)return true;const result=claim(d);if(result.ok){this.picked++;this.effects.push({x:d.x,y:d.y,text:'+3 동전',color:'#ffe296',life:.7});}return !result.ok&&result.reason!=='duplicate';});
 }
}
if(typeof module!=='undefined')module.exports=Arena;else root.TrailArena=Arena;
})(globalThis);
