import * as THREE from 'three';
import { GLTFLoader } from './vendor/GLTFLoader.js';
import { OrbitControls } from './vendor/OrbitControls.js';
import { SoftwareRenderer } from './software-renderer.js';

const $ = (id) => document.getElementById(id);
const names = {TREE_ROUND_SMALL:'둥근 작은 나무',TREE_ROUND_BROAD:'넓은 둥근 나무',TREE_TIERED_SLIM:'가느다란 침엽수',TREE_TIERED_WIDE:'넓은 침엽수',TREE_DEAD_FORK:'갈라진 고사목',TREE_DEAD_LEAN:'기울어진 고사목',ROCK_LOW_WEDGE:'낮은 쐐기 바위',ROCK_UPRIGHT:'세로 바위',ROCK_FLAT_SLAB:'납작한 바위',ROCK_SPLIT_MASS:'갈라진 바위',ROCK_CLUSTER_SMALL:'작은 바위 무리',ROCK_CLUSTER_LARGE:'큰 바위 무리',VEG_BUSH_ROUND:'둥근 덤불',VEG_BUSH_LONG:'긴 덤불',VEG_BUSH_SPARSE:'성긴 덤불',VEG_GRASS_LOW:'낮은 풀',VEG_GRASS_FAN:'부채 풀',VEG_GRASS_TUFT:'풀 무더기',PROP_STUMP_ROUND:'둥근 그루터기',PROP_STUMP_SPLIT:'갈라진 그루터기',PROP_LOG_STRAIGHT:'곧은 통나무',PROP_LOG_BROKEN:'부러진 통나무',PROP_BRANCH_FORK:'갈라진 가지',PROP_BRANCH_PILE:'가지 더미',WOOD_RAIL_1M:'목재 울타리 1m',WOOD_RAIL_2M:'목재 울타리 2m',WOOD_RAIL_4M:'목재 울타리 4m',WOOD_CORNER_L90:'목재 왼쪽 모서리',WOOD_CORNER_R90:'목재 오른쪽 모서리',WOOD_END_CAP:'목재 끝단',WOOD_END_BROKEN:'부서진 목재 끝단',WOOD_POST:'목재 기둥',WOOD_GATE_FRAME:'목재 문틀',WOOD_GATE_LEAF:'목재 문짝',STONE_WALL_1M:'돌담 1m',STONE_WALL_2M:'돌담 2m',STONE_WALL_4M:'돌담 4m',STONE_CORNER_L90:'돌담 왼쪽 모서리',STONE_CORNER_R90:'돌담 오른쪽 모서리',STONE_END_CAP:'돌담 끝단',STONE_END_RUIN:'무너진 돌담 끝단',STONE_POST:'돌 기둥'};
const categories={TREE:'나무',ROCK:'바위',VEG:'덤불·풀',PROP:'숲 소품',WOOD:'목재 경계',STONE:'석재 경계'};
let records=Object.keys(names).flatMap(f=>['A','B'].map(v=>({id:`TW_${f}_${v}`,name:`${names[f]} ${v}`,category:categories[f.split('_')[0]]})));
let theme='MOSS_01',mode='scene',selected=records[0],category='전체',version=0;
let renderer,scene,camera,controls,group,ground,light,hasView=false;
const loader=new GLTFLoader();
const path=(id,t=theme)=>`standalone_assets/${t}/models/${/_LOD[0-9]+$/.test(id)||id==='TW_TERMINAL_POST'?id:id+'_LOD0'}.glb`;
const placements=[['TREE_ROUND_SMALL_A',-2.4,0,-1.2,0],['TREE_TIERED_SLIM_A',.1,0,-2,0],['TREE_ROUND_SMALL_B',2.4,0,-.8,.6],['ROCK_LOW_WEDGE_A',-2,0,1.2,.4],['ROCK_UPRIGHT_A',2.6,0,1,.4],['VEG_BUSH_ROUND_A',-3,0,.15,0],['VEG_BUSH_LONG_B',1.5,0,-.8,.5],['PROP_LOG_STRAIGHT_A',.8,0,1.3,-.4],['WOOD_RAIL_2M_A',-2.9,0,-2.5,0],['WOOD_RAIL_2M_A',-.9,0,-2.5,0],['VEG_GRASS_LOW_A',-1,0,.6,0],['VEG_GRASS_FAN_A',2,0,2,0],['VEG_GRASS_TUFT_B',-.7,0,2.1,0],['VEG_GRASS_LOW_B',-2.8,0,1.9,0]];
function dispose(object){const geometries=new Set(),materials=new Set(),textures=new Set();object.traverse(o=>{if(o.geometry)geometries.add(o.geometry);if(o.material)for(const m of [].concat(o.material)){materials.add(m);for(const value of Object.values(m))if(value?.isTexture)textures.add(value);}});geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());textures.forEach(t=>t.dispose());}
function fail(message){$('loading').hidden=true;$('error').hidden=false;$('errorDetail').textContent=message;}
function init(){
  try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});}catch{renderer=new SoftwareRenderer();document.querySelector('.live').textContent='CPU 3D';document.querySelector('.note').textContent='WebGL을 지원하지 않아 호환 모드로 표시합니다. 실제 모델의 회전·확대·테마 변경을 지원하며 그림자는 생략합니다.';}
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.2;
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;$('viewport').append(renderer.domElement);
  scene=new THREE.Scene();camera=new THREE.PerspectiveCamera(38,1,.05,100);controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.07;controls.maxPolarAngle=Math.PI*.49;controls.minDistance=1;controls.maxDistance=30;controls.autoRotateSpeed=.6;controls.enablePan=false;
  scene.add(new THREE.HemisphereLight(0xfff8e5,0x728365,2.6));light=new THREE.DirectionalLight(0xfff3d6,3);light.position.set(-4,8,5);light.castShadow=true;light.shadow.mapSize.set(1024,1024);Object.assign(light.shadow.camera,{left:-7,right:7,top:7,bottom:-7,near:.1,far:25});light.shadow.normalBias=.04;scene.add(light);
  ground=new THREE.Mesh(new THREE.CylinderGeometry(4.5,4.5,.18,64),new THREE.MeshStandardMaterial({color:0xa4b28a,roughness:1}));ground.position.y=-.11;ground.receiveShadow=true;scene.add(ground);
  const resize=()=>{const box=$('viewport').getBoundingClientRect();renderer.setSize(box.width,box.height);camera.aspect=box.width/box.height;camera.updateProjectionMatrix();};new ResizeObserver(resize).observe($('viewport'));resize();
  renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();fail('그래픽 연결이 중단되었습니다. 페이지를 새로고침해 주세요.');});
  renderer.setAnimationLoop(()=>{if(document.hidden)return;controls.update();renderer.render(scene,camera);});
  loadView();
}
function reset(){if(!group)return;const box=new THREE.Box3().setFromObject(group),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());const radius=size.length()/2;const angle=Math.min(camera.fov*Math.PI/180,2*Math.atan(Math.tan(camera.fov*Math.PI/360)*camera.aspect));const distance=Math.max(radius/Math.sin(angle/2)*1.15,2);controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(1,.7,1.3).normalize().multiplyScalar(distance));controls.maxDistance=Math.max(distance*3,10);controls.update();}
async function loadView(){
  if(!renderer)return;const ticket=++version;const requestedTheme=theme,requestedMode=mode,requestedAsset=selected;let fresh=new THREE.Group();
  $('loading').hidden=false;$('error').hidden=true;$('download').hidden=true;
  const entries=requestedMode==='scene'?placements:[[requestedAsset.id.slice(3),0,0,0,0]];
  const results=await Promise.allSettled(entries.map(async ([id,x,y,z,r])=>{const gltf=await loader.loadAsync(path('TW_'+id,requestedTheme));const obj=gltf.scene;obj.position.set(x,y,z);obj.rotation.y=r;obj.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});return obj;}));
  for(const r of results)if(r.status==='fulfilled')fresh.add(r.value);
  if(ticket!==version){dispose(fresh);return;}
  if(results.some(r=>r.status==='rejected')){dispose(fresh);fail('모델 파일을 불러오지 못했습니다. 연결 상태를 확인한 뒤 다시 시도해 주세요.');return;}
  if(group){scene.remove(group);dispose(group);}group=fresh;scene.add(group);
  let triangleCount=0;group.traverse(o=>{if(o.isMesh)triangleCount+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;});
  $('modelName').textContent=requestedMode==='scene'?'작은 숲길':requestedAsset.name;$('modelId').textContent=requestedMode==='scene'?'나무, 바위, 풀, 목재 경계를 조합한 예제':requestedAsset.id;
  $('lodLabel').textContent=requestedMode==='scene'?'LOD 0':(requestedAsset.lod==null?'연결 부품':`LOD ${requestedAsset.lod}`);
  $('count').textContent=`${entries.length}개`;$('triangles').textContent=triangleCount.toLocaleString();
  $('download').hidden=requestedMode!=='asset';$('download').href=path(requestedAsset.id,requestedTheme);
  ground.material.color.set({MOSS_01:0xa4b28a,DRY_01:0xc5b887,DUSK_01:0x9795a9}[requestedTheme]);
  const box=new THREE.Box3().setFromObject(group),size=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());const scale=requestedMode==='scene'?1:Math.max(size.x,size.z,.8)/6;
  ground.scale.set(scale,1,scale);ground.position.set(center.x,box.min.y-.11,center.z);
  reset();hasView=true;$('loading').hidden=true;renderer.domElement.dataset.loaded=`${requestedTheme}:${requestedMode}:${entries.length}`;
}
function setMode(value){mode=value;$('sceneMode').classList.toggle('active',mode==='scene');$('assetMode').classList.toggle('active',mode==='asset');$('sceneMode').setAttribute('aria-pressed',mode==='scene');$('assetMode').setAttribute('aria-pressed',mode==='asset');renderCards();loadView();}
let filteredRows=[],imageIndex=0;
function showImage(index){imageIndex=(index+filteredRows.length)%filteredRows.length;const r=filteredRows[imageIndex];$('largeImage').src=r.themes[theme].thumbnail;$('largeImage').alt=r.name+' '+theme+' 미리보기';$('imageTitle').textContent=r.name;$('imageMeta').textContent=`${r.id} · ${theme} · ${r.themes[theme].triangles.toLocaleString()} triangles`;
 if(!$('imageDialog').open)$('imageDialog').showModal();}
function choose(r){selected=r;setMode('asset');document.querySelector('.workbench').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});}
function renderCards(){const query=$('search').value.trim().toLowerCase();filteredRows=records.filter(r=>(category==='전체'||r.category===category)&&`${r.name} ${r.id} ${r.category}`.toLowerCase().includes(query));$('cards').replaceChildren();$('resultCount').textContent=`${filteredRows.length} / ${records.length} 모델·LOD·부품 · ${theme.replace('_01','')} · 전체 327개 테마별 이미지`;$('empty').hidden=!!filteredRows.length;
 for(const [i,r] of filteredRows.entries()){const card=document.createElement('article');card.className='card'+(mode==='asset'&&selected.id===r.id?' selected':'');const thumb=document.createElement('button');thumb.className='thumb thumb-open';thumb.setAttribute('aria-label',r.name+' 이미지 확대');const img=document.createElement('img');img.src=r.themes[theme].thumbnail;img.alt=r.name+' 미리보기';img.loading='lazy';thumb.append(img);thumb.onclick=()=>showImage(i);const label=document.createElement('button');label.className='card-label model-open';label.setAttribute('aria-label',r.name+' 3D 보기');const title=document.createElement('b');title.textContent=r.name;const small=document.createElement('small');small.textContent=r.category+' · '+(r.lod==null?'부품':'LOD '+r.lod)+' ↗';label.append(title,small);label.onclick=()=>choose(r);card.append(thumb,label);$('cards').append(card);}
}
$('closeImage').onclick=()=>$('imageDialog').close();$('previousImage').onclick=()=>showImage(imageIndex-1);$('nextImage').onclick=()=>showImage(imageIndex+1);$('imageTo3d').onclick=()=>{const r=filteredRows[imageIndex];$('imageDialog').close();choose(r);};
$('imageDialog').addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();showImage(imageIndex+1);}if(e.key==='ArrowLeft'){e.preventDefault();showImage(imageIndex-1);}});
for(const name of ['전체',...Object.values(categories),'기존 식생','캠프·가구','길·계단','연결 부품']){const b=document.createElement('button');b.textContent=name;b.className=name===category?'active':'';b.setAttribute('aria-pressed',name===category);b.onclick=()=>{category=name;for(const el of $('filters').children){el.classList.toggle('active',el===b);el.setAttribute('aria-pressed',el===b);}renderCards();};$('filters').append(b);}
document.querySelectorAll('[data-theme]').forEach(b=>{b.onclick=()=>{theme=b.dataset.theme;document.querySelectorAll('[data-theme]').forEach(el=>{el.classList.toggle('selected',el===b);el.setAttribute('aria-pressed',el===b);});renderCards();loadView();};});
$('sceneMode').onclick=()=>setMode('scene');$('assetMode').onclick=()=>setMode('asset');$('search').oninput=renderCards;$('reset').onclick=reset;
$('rotate').onclick=()=>{if(!controls)return;controls.autoRotate=!controls.autoRotate;$('rotate').setAttribute('aria-pressed',controls.autoRotate);};$('retry').onclick=()=>{if(renderer&&hasView)loadView();else location.reload();};
try {
 const response=await fetch('web/gallery.json');if(!response.ok)throw new Error('gallery');const data=await response.json();
 records=data.assets.map(r=>{const family=r.asset_id.replace(/^TW_/, '').replace(/_[AB]$/, '');const base=names[family];const prefix=family.split('_')[0];const group=categories[prefix]||({SHRUB:'기존 식생',GRASS:'기존 식생',STUMP:'숲 소품',LOG:'숲 소품',SIGN:'캠프·가구',CRATE:'캠프·가구',BENCH:'캠프·가구',TABLE:'캠프·가구',PAVER:'길·계단',STEPS:'길·계단',TERMINAL:'연결 부품'}[prefix])||'캠프·가구';return {...r,id:r.model,category:group,name:base?`${base} ${r.asset_id.slice(-1)}${r.lod===1?' · LOD1':''}`:r.model.replace(/^TW_/,'').replaceAll('_',' ')};});
 selected=records.find(r=>r.asset_id==='TW_TREE_ROUND_SMALL_A'&&r.lod===0)||records[0];renderCards();init();
}catch{fail('갤러리 목록을 불러오지 못했습니다. 페이지를 새로고침해 주세요.');}

