import * as THREE from 'three';
import { GLTFLoader } from '../web/vendor/GLTFLoader.js';
import { OrbitControls } from '../web/vendor/OrbitControls.js';
import { SoftwareRenderer } from '../web/software-renderer.js';

const dialog=document.querySelector('#item-dialog'),viewport=document.querySelector('#item-viewport'),status=document.querySelector('#item-status');
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(38,1,.01,100),loader=new GLTFLoader();
let renderer,controls,model,version=0,compatibility=false;
function dispose(object){object.traverse(o=>{o.geometry?.dispose();for(const m of [].concat(o.material||[]))m.dispose();});}
function draw(){if(dialog.open&&renderer)renderer.render(scene,camera);}
function reset(){
 if(!model)return;model.rotation.set(0,0,0);
 const box=new THREE.Box3().setFromObject(model),center=box.getCenter(new THREE.Vector3()),radius=box.getSize(new THREE.Vector3()).length()/2;
 const angle=Math.min(camera.fov*Math.PI/180,2*Math.atan(Math.tan(camera.fov*Math.PI/360)*camera.aspect));
 const distance=Math.max(.1,radius/Math.sin(angle/2)*1.2);
 controls.target.copy(center);camera.position.copy(center).add(new THREE.Vector3(1,.7,1.3).normalize().multiplyScalar(distance));
 controls.minDistance=distance*.35;controls.maxDistance=distance*3;camera.near=distance/100;camera.far=distance*20;camera.updateProjectionMatrix();controls.update();draw();
}
function resize(){const {width,height}=viewport.getBoundingClientRect();if(!width||!height)return;renderer.setSize(width,height);camera.aspect=width/height;camera.updateProjectionMatrix();reset();draw();}
function init(){
 try{renderer=new THREE.WebGLRenderer({antialias:true,alpha:true});}catch{renderer=new SoftwareRenderer();compatibility=true;}
 renderer.setPixelRatio(Math.min(devicePixelRatio,2));viewport.replaceChildren(renderer.domElement);
 controls=new OrbitControls(camera,renderer.domElement);controls.enablePan=false;controls.addEventListener('change',draw);
 scene.add(new THREE.HemisphereLight(0xfff8e5,0x728365,2.6));const light=new THREE.DirectionalLight(0xffffff,2.5);light.position.set(-3,5,4);scene.add(light);
 new ResizeObserver(resize).observe(viewport);
 document.querySelector('#item-reset').onclick=reset;
 document.querySelector('#item-turn').onclick=()=>{if(model){model.rotation.y+=Math.PI/4;draw();}};
 for(const [id,scale] of [['item-in',.8],['item-out',1.25]])document.getElementById(id).onclick=()=>{const offset=camera.position.clone().sub(controls.target);offset.setLength(THREE.MathUtils.clamp(offset.length()*scale,controls.minDistance,controls.maxDistance));camera.position.copy(controls.target).add(offset);controls.update();draw();};
 renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();status.textContent='3D 그래픽 연결이 중단되었습니다. 페이지를 새로고침해 주세요.';});
 dialog.addEventListener('close',()=>{version++;if(model){scene.remove(model);dispose(model);model=null;}viewport.hidden=true;});
}
export async function showItem(item){
 if(!dialog.open)return;
 const ticket=++version;
 try{
  if(!renderer)init();
  if(model){scene.remove(model);dispose(model);model=null;}
  viewport.hidden=true;
  const gltf=await loader.loadAsync(item.model);
  if(ticket!==version||!dialog.open){dispose(gltf.scene);return;}
  model=gltf.scene;scene.add(model);viewport.hidden=false;resize();
  status.textContent=item.label+' · '+item.triangles+' 삼각형 · '+(compatibility?'CPU 호환 3D':'WebGL 3D');
 }catch(error){if(ticket===version&&dialog.open){viewport.hidden=true;status.textContent='모델을 불러오지 못했습니다. 닫은 후 다시 시도하거나 GLB를 다운로드해 주세요.';}}
}
