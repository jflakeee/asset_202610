'use strict';
async function start(){
const [itemsResponse,configResponse]=await Promise.all([fetch('items.json'),fetch('game-config.json')]);
if(!itemsResponse.ok||!configResponse.ok)throw new Error('데이터 파일을 불러오지 못했습니다.');
const ITEMS=await itemsResponse.json(),config=await configResponse.json();
const state=new RewardState(ITEMS.map(x=>x.id),config);let wave=0;const cards=new Map();
const notice=document.querySelector('#notice');
let arenaController=null;
for(const item of ITEMS){
 const card=document.createElement('article');card.className='card';
 const image=document.createElement('img');image.src=item.icon;image.alt=item.label;
 const heading=document.createElement('h2');heading.textContent=item.label;heading.style.fontSize='18px';
 const qty=document.createElement('p');const button=document.createElement('button');button.textContent='획득 +1';
 button.addEventListener('click',()=>{const r=state.claim({id:wave+':'+item.id,item:item.id,quantity:1});notice.textContent=r.ok?item.label+' 획득!':'이미 획득한 드롭입니다.';render();if(r.ok){card.classList.remove('pulse');void card.offsetWidth;card.classList.add('pulse');}});
 card.append(image,heading,qty,button);document.querySelector('#cards').append(card);cards.set(item.id,{qty,button});
}
function render(){document.querySelector('#health').textContent='체력 '+state.hp+' / 100';document.querySelector('#bar').value=state.hp;
 for(const [id,c] of cards){c.qty.textContent='보유 '+state.inventory[id];c.button.disabled=state.claimed.has(wave+':'+id);c.button.textContent=c.button.disabled?'획득 완료':'획득 +1';}
 document.querySelector('#damage').disabled=state.hp===0;
 document.querySelector('#ingredients').textContent=Object.entries(config.recipes[0].costs).map(([id,q])=>ITEMS.find(x=>x.id===id).label+' '+state.inventory[id]+'/'+q).join(' · ');
 document.querySelector('#heal').disabled=state.hp>=100||state.inventory['consumable.health_potion']<1;
 document.querySelector('#chest').disabled=state.inventory['reward.chest']<1;
}
document.querySelector('#wave').onclick=()=>{wave++;notice.textContent='새 드롭이 준비되었습니다. 보유 아이템은 유지됩니다.';render();};
document.querySelector('#reset').onclick=()=>{state.reset();wave=0;arenaController?.reset();notice.textContent='초기화했습니다.';render();};render();


document.querySelector('#damage').onclick=()=>{state.damage();notice.textContent='시험 피해 '+config.damageAmount+' 적용';render();};
document.querySelector('#craft').onclick=()=>{const r=state.craft('chest');notice.textContent=r.ok?'재료를 소비하여 보물상자 1개를 제작했습니다.':'재료가 부족하거나 제작할 수 없습니다. 재료는 소비되지 않았습니다.';render();};
document.querySelector('#heal').textContent='회복약 사용 +'+config.healAmount;
document.querySelector('#chest').textContent='상자 열기 · 동전 '+config.chestCoins;
document.querySelector('#damage').textContent='피해 받기 −'+config.damageAmount;
document.querySelector('#heal').onclick=()=>{const r=state.heal();notice.textContent=r.ok?'회복약 1개 사용 · 체력 회복':'사용할 수 없습니다.';render();};
document.querySelector('#chest').onclick=()=>{const r=state.openChest();notice.textContent=r.ok?'상자 1개 사용 · 동전 '+r.coins+'개 획득':'상자를 열 수 없습니다.';render();};
arenaController=mountArena(state,render);
}
start().catch(error=>{document.querySelector('#notice').textContent='초기화 실패: '+error.message+' 새로고침해 주세요.';document.querySelectorAll('button').forEach(b=>b.disabled=true);});
