'use strict';
async function start(){
const [itemsResponse,configResponse]=await Promise.all([fetch('items.json'),fetch('game-config.json')]);
if(!itemsResponse.ok||!configResponse.ok)throw new Error('데이터 파일을 불러오지 못했습니다.');
const ITEMS=await itemsResponse.json(),config=await configResponse.json();
const state=new RewardState(ITEMS.map(x=>x.id),config);let wave=0;const cards=new Map();
const sound=new TrailSound(),soundButton=document.querySelector('#sound');
soundButton.onclick=async()=>{soundButton.disabled=true;const enabled=await sound.toggle();soundButton.textContent=enabled?'소리 끄기':'소리 켜기';soundButton.setAttribute('aria-pressed',String(enabled));soundButton.disabled=false;if(enabled)sound.play('pickup');else if(!sound.context||sound.context.state!=='running')notice.textContent='이 브라우저에서 소리를 시작하지 못했습니다. 소리 켜기를 다시 눌러 주세요.';};
document.addEventListener('visibilitychange',()=>sound.visibility(document.hidden));
const notice=document.querySelector('#notice');
let arenaController=null,previewRequest=0;
const dialog=document.querySelector('#item-dialog');
document.querySelector('#item-close').onclick=()=>dialog.close();
dialog.addEventListener('close',()=>previewRequest++);
for(const item of ITEMS){
 const card=document.createElement('article');card.className='card';
 const image=document.createElement('img');image.src=item.icon;image.alt=item.label;
 const heading=document.createElement('h2');heading.textContent=item.label;heading.style.fontSize='18px';
 const qty=document.createElement('p');const button=document.createElement('button');button.textContent='획득 +1';
 button.addEventListener('click',()=>{const r=state.claim({id:wave+':'+item.id,item:item.id,quantity:1});notice.textContent=r.ok?item.label+' 획득!':'이미 획득한 드롭입니다.';render();if(r.ok){sound.play('pickup');card.classList.remove('pulse');void card.offsetWidth;card.classList.add('pulse');}});
 const preview=document.createElement('button');preview.textContent='3D 보기';preview.setAttribute('aria-label',item.label+' 3D 보기');
 preview.onclick=async()=>{
  const request=++previewRequest;arenaController?.pause();
  document.querySelector('#item-title').textContent=item.label+' 3D 미리보기';
  document.querySelector('#item-status').textContent='모델을 불러오는 중입니다.';
  document.querySelector('#item-viewport').hidden=true;
  document.querySelector('#item-download').href=item.model;
  dialog.showModal();
  try{const viewer=await import('./item-viewer.js?v=7');if(request===previewRequest&&dialog.open)await viewer.showItem(item);}
  catch{if(request===previewRequest&&dialog.open)document.querySelector('#item-status').textContent='3D 뷰어를 불러오지 못했습니다. 닫은 후 다시 시도해 주세요.';}
 };
 card.append(image,heading,qty,button,preview);document.querySelector('#cards').append(card);cards.set(item.id,{qty,button});
}
function render(){document.querySelector('#health').textContent='체력 '+state.hp+' / 100';document.querySelector('#bar').value=state.hp;
 for(const [id,c] of cards){c.qty.textContent='보유 '+state.inventory[id];c.button.disabled=state.claimed.has(wave+':'+id);c.button.textContent=c.button.disabled?'획득 완료':'획득 +1';}
 document.querySelector('#damage').disabled=state.hp===0;
 document.querySelector('#ingredients').textContent=Object.entries(config.recipes[0].costs).map(([id,q])=>ITEMS.find(x=>x.id===id).label+' '+state.inventory[id]+'/'+q).join(' · ');
 for(const button of document.querySelectorAll('[data-heal]'))button.disabled=state.hp>=state.maxHp||state.inventory['consumable.health_potion']<1;
 document.querySelector('#arena-health').textContent='체력 '+state.hp+'/'+state.maxHp;
 document.querySelector('#arena-coins').textContent='동전 '+state.inventory['currency.coin'];
 document.querySelector('#arena-heal-label').textContent='회복약 '+state.inventory['consumable.health_potion']+'개 · +'+config.healAmount;
 document.querySelector('#chest').disabled=state.inventory['reward.chest']<1;
}
document.querySelector('#wave').onclick=()=>{wave++;notice.textContent='새 드롭이 준비되었습니다. 보유 아이템은 유지됩니다.';render();};
document.querySelector('#reset').onclick=()=>{state.reset();wave=0;arenaController?.reset();notice.textContent='초기화했습니다.';render();};render();


document.querySelector('#damage').onclick=()=>{state.damage();sound.play('hurt');notice.textContent='시험 피해 '+config.damageAmount+' 적용';render();};
document.querySelector('#craft').onclick=()=>{const r=state.craft('chest');if(r.ok)sound.play('craft');notice.textContent=r.ok?'재료를 소비하여 보물상자 1개를 제작했습니다.':'재료가 부족하거나 제작할 수 없습니다. 재료는 소비되지 않았습니다.';render();};
document.querySelector('#heal').textContent='회복약 사용 +'+config.healAmount;
document.querySelector('#chest').textContent='상자 열기 · 동전 '+config.chestCoins;
document.querySelector('#damage').textContent='피해 받기 −'+config.damageAmount;
for(const button of document.querySelectorAll('[data-heal]'))button.onclick=()=>{const r=state.heal();if(r.ok)sound.play('heal');notice.textContent=r.ok?'회복약 1개 사용 · 체력 회복':'사용할 수 없습니다.';render();};
const rewardDialog=document.querySelector('#reward-dialog');
document.querySelector('#reward-close').onclick=()=>rewardDialog.close();
rewardDialog.addEventListener('close',()=>rewardDialog.classList.remove('revealing'));
document.querySelector('#chest').onclick=()=>{
 if(rewardDialog.open)return;
 const r=state.openChest();
 notice.textContent=r.ok?'상자 1개 사용 · 동전 '+r.coins+'개 획득':'상자를 열 수 없습니다.';render();
 if(!r.ok)return;
 arenaController?.pause();sound.play('chest');
 document.querySelector('#reward-amount').textContent='동전 +'+r.coins;
 document.querySelector('#reward-balance').textContent='보유 동전 '+state.inventory['currency.coin']+'개 · 남은 상자 '+state.inventory['reward.chest']+'개';
 rewardDialog.showModal();rewardDialog.classList.remove('revealing');void rewardDialog.offsetWidth;rewardDialog.classList.add('revealing');
};
for(const image of document.querySelectorAll('[data-item-icon]'))image.src=ITEMS.find(item=>item.id===image.dataset.itemIcon).icon;
const recipe=config.recipes.find(recipe=>recipe.id==='chest');
document.querySelector('#recipe').textContent=Object.entries(recipe.costs).map(([id,q])=>ITEMS.find(item=>item.id===id).label+' '+q).join(' + ')+' → '+ITEMS.find(item=>item.id===recipe.output.item).label+' '+recipe.output.quantity;
arenaController=mountArena(state,render,ITEMS,sound);
document.querySelectorAll('button').forEach(button=>button.disabled=false);render();
notice.textContent='아래 아이템을 누르면 인벤토리에 추가됩니다. 회복약을 준비하고 전투를 시작하세요.';
}
start().catch(error=>{document.querySelector('#notice').textContent='초기화 실패: '+error.message+' 새로고침해 주세요.';document.querySelectorAll('button').forEach(b=>b.disabled=true);});
