'use strict';
const state=new RewardState(ITEMS.map(x=>x.id));let wave=0;const cards=new Map();
const notice=document.querySelector('#notice');
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
 document.querySelector('#heal').disabled=state.hp>=100||state.inventory['consumable.health_potion']<1;
 document.querySelector('#chest').disabled=state.inventory['reward.chest']<1;
}
document.querySelector('#heal').onclick=()=>{const r=state.heal();notice.textContent=r.ok?'회복약 1개 사용 · 체력 회복':'사용할 수 없습니다.';render();};
document.querySelector('#chest').onclick=()=>{const r=state.openChest();notice.textContent=r.ok?'상자 1개 사용 · 동전 10개 획득':'상자를 열 수 없습니다.';render();};
document.querySelector('#wave').onclick=()=>{wave++;notice.textContent='새 드롭이 준비되었습니다. 보유 아이템은 유지됩니다.';render();};
document.querySelector('#reset').onclick=()=>{state.reset();wave=0;notice.textContent='초기화했습니다.';render();};render();
