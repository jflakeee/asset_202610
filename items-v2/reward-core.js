(function(root){
'use strict';
class RewardState {
 constructor(ids,config={healAmount:30,chestCoins:10,damageAmount:25,recipes:[]}){this.config=config;this.ids=new Set(ids);this.reset();}
 reset(){this.inventory=Object.fromEntries([...this.ids].map(id=>[id,0]));this.claimed=new Set();this.hp=40;this.maxHp=100;}
 claim(drop){
  if(!drop||typeof drop.id!=='string'||!drop.id||!this.ids.has(drop.item)||!Number.isSafeInteger(drop.quantity)||drop.quantity<1)return {ok:false,reason:'invalid'};
  if(this.claimed.has(drop.id))return {ok:false,reason:'duplicate'};
  const total=this.inventory[drop.item]+drop.quantity;
  if(!Number.isSafeInteger(total))return {ok:false,reason:'overflow'};
  this.inventory[drop.item]=total;this.claimed.add(drop.id);return {ok:true};
 }
 damage(){this.hp=Math.max(0,this.hp-this.config.damageAmount);return {ok:true};}
 craft(id){
 const recipe=this.config.recipes.find(r=>r.id===id);if(!recipe)return {ok:false,reason:"unknown_recipe"};
 const next={...this.inventory};
 for(const [item,qty] of Object.entries(recipe.costs)){if(!this.ids.has(item)||!Number.isSafeInteger(qty)||qty<1)return {ok:false,reason:"invalid_recipe"};if(next[item]<qty)return {ok:false,reason:"insufficient"};next[item]-=qty;}
 const out=recipe.output;if(!this.ids.has(out.item)||!Number.isSafeInteger(out.quantity)||out.quantity<1||!Number.isSafeInteger(next[out.item]+out.quantity))return {ok:false,reason:"invalid_output"};
 next[out.item]+=out.quantity;this.inventory=next;return {ok:true};
 }
 heal(){const id='consumable.health_potion';if(!(this.inventory[id]>0))return {ok:false,reason:'empty'};
  if(this.hp>=this.maxHp)return {ok:false,reason:'full'};
  this.inventory[id]--;this.hp=Math.min(this.maxHp,this.hp+this.config.healAmount);return {ok:true};}
 openChest(){const id='reward.chest',coin='currency.coin';if(!(this.inventory[id]>0))return {ok:false,reason:'empty'};
  if(!this.ids.has(coin)||!Number.isSafeInteger(this.inventory[coin]+this.config.chestCoins))return {ok:false,reason:'invalid_reward'};
  this.inventory[id]--;this.inventory[coin]+=this.config.chestCoins;return {ok:true,coins:this.config.chestCoins};}
}
if(typeof module!=='undefined')module.exports=RewardState;else root.RewardState=RewardState;
})(globalThis);

