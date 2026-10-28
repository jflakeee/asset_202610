import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
if(!process.argv[2])throw new Error('Pass a directory containing matched Three.js and GLTFLoader test modules');
const runtime=pathToFileURL(resolve(process.argv[2])+'/');
const {GLTFLoader}=await import(new URL('GLTFLoader.js',runtime));
const {AnimationMixer,Box3,Vector3,LoopOnce}=await import(new URL('three.module.js',runtime));
const root=new URL('./',import.meta.url);
const manifest=JSON.parse(readFileSync(new URL('manifest.json',root)));
for(const record of manifest){
 const b=readFileSync(new URL(`models/${record.id}.glb`,root));
 const g=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'');
 let triangles=0,primitives=0;const materials=new Set();
 g.scene.traverse(o=>{if(o.isMesh){primitives++;triangles+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;materials.add(o.material);assert(o.material.vertexColors);const colors=o.geometry.attributes.color;assert(colors&&colors.count===o.geometry.attributes.position.count);for(let i=0;i<colors.count;i++)for(const x of [colors.getX(i),colors.getY(i),colors.getZ(i)])assert(Number.isFinite(x)&&x>=0&&x<=1);}});
 assert.equal(triangles,record.triangles);assert.equal(primitives,record.primitives);assert.equal(materials.size,record.materials);
 const bounds=new Box3().setFromObject(g.scene);assert(Math.abs(bounds.min.y)<1e-6);assert(bounds.getSize(new Vector3()).length()>.2);
 if(record.animated){const mixer=new AnimationMixer(g.scene);const action=mixer.clipAction(g.animations[0]);action.setLoop(LoopOnce,1);action.clampWhenFinished=true;action.play();for(const [t,d] of [[0,0],[.3,52.5],[.6,105]]){mixer.setTime(t);assert(Math.abs(g.scene.getObjectByName('LidHinge').rotation.x*180/Math.PI-d)<.01);}}
 console.log('PASS',record.id,triangles,'triangles',primitives,'primitives',materials.size,'materials');
}
