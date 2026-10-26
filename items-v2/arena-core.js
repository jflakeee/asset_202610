(function(root){'use strict';
class Arena {
 constructor(){this.reset();}
 reset(){this.player={x:200,y:200};this.enemies=[{x:250,y:200,hp:3},{x:460,y:130,hp:3},{x:600,y:300,hp:3}];this.drops=[];this.cooldown=0;this.serial=0;this.kills=0;this.picked=0;this.paused=false;}
 step(dt,input,claim){
  if(this.paused)return;dt=Math.min(Math.max(dt,0),.05);let x=input.x||0,y=input.y||0,n=Math.hypot(x,y);if(n>1){x/=n;y/=n;}
  this.player.x=Math.max(16,Math.min(784,this.player.x+x*180*dt));this.player.y=Math.max(16,Math.min(384,this.player.y+y*180*dt));
  this.cooldown=Math.max(0,this.cooldown-dt);
  let target=this.enemies.filter(e=>e.hp>0).sort((a,b)=>Math.hypot(a.x-this.player.x,a.y-this.player.y)-Math.hypot(b.x-this.player.x,b.y-this.player.y))[0];
  if(target&&Math.hypot(target.x-this.player.x,target.y-this.player.y)<=115&&this.cooldown===0){target.hp--;this.cooldown=.45;if(target.hp===0){this.kills++;this.drops.push({id:'arena:'+this.serial++,item:'currency.coin',quantity:3,x:target.x,y:target.y});}}
  this.drops=this.drops.filter(d=>{if(Math.hypot(d.x-this.player.x,d.y-this.player.y)>28)return true;const result=claim(d);if(result.ok)this.picked++;return !result.ok&&result.reason!=='duplicate';});
 }
}
if(typeof module!=='undefined')module.exports=Arena;else root.TrailArena=Arena;
})(globalThis);
