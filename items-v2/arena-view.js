'use strict';
function mountArena(state,render,items){
 const arena=new TrailArena(),canvas=document.querySelector('#arena'),ctx=canvas.getContext('2d'),status=document.querySelector('#arena-status'),keys=new Set();let pointer=null,origin=null,stick={x:0,y:0},last=0;
 const coin=new Image();coin.src=items.find(item=>item.id==='currency.coin').icon;
 const point=e=>{const r=canvas.getBoundingClientRect();return {x:(e.clientX-r.left)*800/r.width,y:(e.clientY-r.top)*400/r.height};};
 canvas.addEventListener('pointerdown',e=>{if(pointer!==null)return;pointer=e.pointerId;origin=point(e);stick={x:0,y:0};canvas.setPointerCapture(pointer);canvas.focus();});
 canvas.addEventListener('pointermove',e=>{if(e.pointerId!==pointer)return;const p=point(e);stick={x:(p.x-origin.x)/55,y:(p.y-origin.y)/55};});
 const clear=()=>{pointer=null;origin=null;stick={x:0,y:0};keys.clear();};
 for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,clear);
 canvas.addEventListener('keydown',e=>{if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight','w','a','s','d'].includes(e.key)){e.preventDefault();keys.add(e.key);}});
 canvas.addEventListener('keyup',e=>keys.delete(e.key));canvas.addEventListener('blur',clear);window.addEventListener('blur',clear);document.addEventListener('visibilitychange',()=>{clear();last=0;});
 const pause=document.querySelector('#pause-arena');pause.onclick=()=>{arena.paused=!arena.paused;clear();pause.textContent=arena.paused?'전투 재개':'전투 일시정지';};
 function circle(x,y,r,color){ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fillStyle=color;ctx.fill();}
 function frame(time){const dt=last?(time-last)/1000:0;last=time;
  if(!document.hidden&&state.hp>0){const oldKills=arena.kills,oldPicked=arena.picked,oldHp=state.hp;arena.step(dt,{x:stick.x+(keys.has('ArrowRight')||keys.has('d')?1:0)-(keys.has('ArrowLeft')||keys.has('a')?1:0),y:stick.y+(keys.has('ArrowDown')||keys.has('s')?1:0)-(keys.has('ArrowUp')||keys.has('w')?1:0)},drop=>state.claim(drop),amount=>{state.hp=Math.max(0,state.hp-amount);});if(arena.kills!==oldKills||arena.picked!==oldPicked||state.hp!==oldHp)render();}
  ctx.fillStyle='#172b23';ctx.fillRect(0,0,800,400);ctx.strokeStyle='#294337';for(let x=0;x<800;x+=40){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,400);ctx.stroke();}for(let y=0;y<400;y+=40){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(800,y);ctx.stroke();}
  ctx.beginPath();ctx.arc(arena.player.x,arena.player.y,115,0,Math.PI*2);ctx.strokeStyle='#70986a';ctx.stroke();
  for(const e of arena.enemies)if(e.hp>0){circle(e.x,e.y,18,'#c26e60');ctx.fillStyle='#fff';ctx.font='16px sans-serif';ctx.fillText(e.hp+'/5',e.x-22,e.y-26);}
  for(const d of arena.drops){if(coin.complete&&coin.naturalWidth>0)ctx.drawImage(coin,d.x-22,d.y-22,44,44);else circle(d.x,d.y,10,'#e6bd59');ctx.fillStyle='#fff';ctx.fillText('+3',d.x-10,d.y-16);}
  circle(arena.player.x,arena.player.y,14,arena.invulnerable>0?'#f4ad9c':'#8fc9db');
  ctx.font='bold 16px sans-serif';for(const e of arena.effects){ctx.fillStyle=e.color;ctx.fillText(e.text,e.x-12,e.y-30-(.7-e.life)*18);}if(origin){const length=Math.max(1,Math.hypot(stick.x,stick.y));circle(origin.x,origin.y,42,'#ffffff22');circle(origin.x+stick.x/length*30,origin.y+stick.y/length*30,14,'#bac8bb');}
  const text=`처치 ${arena.kills}/3 · 획득 ${arena.picked}/3 · ${state.hp===0?'체력 0: 회복약을 사용하세요':arena.paused?'일시정지':arena.picked===3?'완료! 처음부터 버튼으로 다시 체험':'범위 안 자동 공격 / 동전에 접근하면 획득'}`;
  if(status.textContent!==text)status.textContent=text;requestAnimationFrame(frame);
 }
 requestAnimationFrame(frame);return {pause(){arena.paused=true;clear();pause.textContent='전투 재개';},reset(){arena.reset();clear();last=0;pause.textContent='전투 시작';}};
}
