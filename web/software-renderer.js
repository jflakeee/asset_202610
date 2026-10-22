import * as THREE from 'three';

// Small Canvas2D fallback for browsers without WebGL. It uses the actual GLB
// triangles and embedded palette; no screenshot or placeholder geometry.
export class SoftwareRenderer {
  constructor(){this.domElement=document.createElement('canvas');this.ctx=this.domElement.getContext('2d');this.shadowMap={};this.materials=new WeakMap();this.ratio=1;}
  setPixelRatio(r){this.ratio=Math.min(r,1.5);}
  setSize(w,h){this.w=w;this.h=h;this.domElement.width=Math.round(w*this.ratio);this.domElement.height=Math.round(h*this.ratio);this.domElement.style.width=w+'px';this.domElement.style.height=h+'px';}
  setAnimationLoop(fn){let last=0;const frame=t=>{if(t-last>65){last=t;fn();}requestAnimationFrame(frame);};requestAnimationFrame(frame);}
  palette(material){if(this.materials.has(material))return this.materials.get(material);let data=null;const image=material.map?.image;if(image){const c=document.createElement('canvas');c.width=image.width;c.height=image.height;const ctx=c.getContext('2d');ctx.drawImage(image,0,0);data={pixels:ctx.getImageData(0,0,c.width,c.height).data,width:c.width,height:c.height};}this.materials.set(material,data);return data;}
  render(scene,camera){
    scene.updateMatrixWorld();camera.updateMatrixWorld();const triangles=[];const sun=new THREE.Vector3(-.4,.8,.5).normalize();
    scene.traverse(o=>{if(!o.isMesh||!o.visible)return;const g=o.geometry,p=g.attributes.position,uv=g.attributes.uv,index=g.index,material=Array.isArray(o.material)?o.material[0]:o.material;if(!p||!material)return;const palette=this.palette(material);const vertices=[];
      for(let i=0;i<p.count;i++){const world=new THREE.Vector3().fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);const screen=world.clone().project(camera);vertices.push({world,screen});}
      for(let k=0;k<(index?index.count:p.count);k+=3){const ids=[0,1,2].map(j=>index?index.getX(k+j):k+j);const [a,b,c]=ids.map(i=>vertices[i]);if([a,b,c].some(v=>v.screen.z< -1||v.screen.z>1))continue;
        const normal=new THREE.Vector3().subVectors(b.world,a.world).cross(new THREE.Vector3().subVectors(c.world,a.world)).normalize();const facing=new THREE.Vector3().subVectors(camera.position,a.world).dot(normal);if(material.side!==THREE.DoubleSide&&facing<=0)continue;
        let color;if(palette&&uv){const u=uv.getX(ids[0]),v=uv.getY(ids[0]);const x=Math.max(0,Math.min(palette.width-1,Math.floor(u*palette.width))),y=Math.max(0,Math.min(palette.height-1,Math.floor(v*palette.height)));const off=(y*palette.width+x)*4;color=[palette.pixels[off],palette.pixels[off+1],palette.pixels[off+2]];}else{const col=material.color.clone().convertLinearToSRGB();color=[col.r*255,col.g*255,col.b*255];}
        const shade=.66+.34*Math.max(0,normal.dot(sun));triangles.push({points:[a,b,c].map(v=>[(v.screen.x+1)*this.w/2,(1-v.screen.y)*this.h/2]),z:(a.screen.z+b.screen.z+c.screen.z)/3,color:`rgb(${color.map(v=>Math.round(v*shade)).join(',')})`});
      }
    });
    triangles.sort((a,b)=>b.z-a.z);const ctx=this.ctx;ctx.setTransform(this.ratio,0,0,this.ratio,0,0);ctx.clearRect(0,0,this.w,this.h);ctx.lineWidth=.45;
    for(const t of triangles){ctx.beginPath();ctx.moveTo(...t.points[0]);ctx.lineTo(...t.points[1]);ctx.lineTo(...t.points[2]);ctx.closePath();ctx.fillStyle=t.color;ctx.strokeStyle=t.color;ctx.fill();ctx.stroke();}
  }
}
