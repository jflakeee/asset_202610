(function(root){
'use strict';
class RewardState {
 constructor(ids){this.ids=new Set(ids);this.reset();}
 reset(){this.inventory=Object.fromEntries([...this.ids].map(id=>[id,0]));this.claimed=new Set();this.hp=40;this.maxHp=100;}
 claim(drop){
  if(!drop||typeof drop.id!=='string'||!drop.id||!this.ids.has(drop.item)||!Number.isSafeInteger(drop.quantity)||drop.quantity<1)return {ok:false,reason:'invalid'};
  if(this.claimed.has(drop.id))return {ok:false,reason:'duplicate'};
  const total=this.inventory[drop.item]+drop.quantity;
  if(!Number.isSafeInteger(total))return {ok:false,reason:'overflow'};
  this.inventory[drop.item]=total;this.claimed.add(drop.id);return {ok:true};
 }
 heal(){const id='consumable.health_potion';if(!(this.inventory[id]>0))return {ok:false,reason:'empty'};
  if(this.hp>=this.maxHp)return {ok:false,reason:'full'};
  this.inventory[id]--;this.hp=Math.min(this.maxHp,this.hp+30);return {ok:true};}
 openChest(){const id='reward.chest',coin='currency.coin';if(!(this.inventory[id]>0))return {ok:false,reason:'empty'};
  if(!this.ids.has(coin)||!Number.isSafeInteger(this.inventory[coin]+10))return {ok:false,reason:'invalid_reward'};
  this.inventory[id]--;this.inventory[coin]+=10;return {ok:true,coins:10};}
}
if(typeof module!=='undefined')module.exports=RewardState;else root.RewardState=RewardState;
})(globalThis);
