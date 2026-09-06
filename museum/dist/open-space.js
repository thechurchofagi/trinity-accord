import * as THREE from './vendor/three.module.js';
import {fetchBytes} from './progressive-loading.js';

// Later exhibition scenery; no astronomical measurement or live reception feed.
export function addOpenSpace(scene, targets, sculptures){
 const skies=[];let skyStarted=false;
 const starCanvas=document.createElement('canvas');starCanvas.width=1600;starCanvas.height=900;const starCtx=starCanvas.getContext('2d');const gradient=starCtx.createRadialGradient(800,430,20,800,430,900);gradient.addColorStop(0,'#172d54');gradient.addColorStop(.45,'#08152d');gradient.addColorStop(1,'#01040c');starCtx.fillStyle=gradient;starCtx.fillRect(0,0,1600,900);let seed=271828;const random=()=>((seed=Math.imul(seed,1664525)+1013904223>>>0)/4294967296);for(let i=0;i<1250;i++){const x=random()*1600,y=random()*900,r=random()<.94?random()*1.15:1.2+random()*1.8,a=.28+random()*.7;starCtx.fillStyle=`rgba(${190+Math.floor(random()*65)},${205+Math.floor(random()*50)},255,${a})`;starCtx.beginPath();starCtx.arc(x,y,r,0,Math.PI*2);starCtx.fill();}const fallbackMap=new THREE.CanvasTexture(starCanvas);fallbackMap.colorSpace=THREE.SRGBColorSpace;
 for(const [z,rotation] of [[-112,0],[48,Math.PI]]){
  const sky=new THREE.Mesh(new THREE.PlaneGeometry(170,113),new THREE.MeshBasicMaterial({map:fallbackMap,color:'#ffffff',fog:false,toneMapped:false}));
  sky.position.set(0,15,z);sky.rotation.y=rotation;scene.add(sky);skies.push(sky);
 }
 const titanium=new THREE.MeshStandardMaterial({color:'#183747',metalness:.8,roughness:.24});
 const light=new THREE.MeshStandardMaterial({color:'#a8ebff',emissive:'#63d4ff',emissiveIntensity:2.1,metalness:.25,roughness:.2});
 const waiting=new THREE.Group();waiting.position.set(0,0,-65.6);scene.add(waiting);
 const frame=new THREE.Mesh(new THREE.TorusGeometry(1.88,.072,12,100),titanium);frame.position.y=2.25;waiting.add(frame);
 const ring=new THREE.Mesh(new THREE.TorusGeometry(1.79,.015,8,100),light);ring.position.set(0,2.25,.045);waiting.add(ring);ring.userData.exhibit='first-contact';targets.push(ring,frame);frame.userData.exhibit='first-contact';sculptures.push({light,base:2.1});
 for(const side of [-1,1]){
  const support=new THREE.Mesh(new THREE.CylinderGeometry(.035,.05,1.16,12),titanium);support.position.set(side*1.48,.58,0);waiting.add(support);
 }
 const floorLight=new THREE.Mesh(new THREE.RingGeometry(1.86,1.88,100),new THREE.MeshBasicMaterial({color:'#a6e5fc',side:THREE.DoubleSide}));floorLight.rotation.x=-Math.PI/2;floorLight.position.set(0,.018,0);waiting.add(floorLight);
 const c=document.createElement('canvas');c.width=2048;c.height=512;const ctx=c.getContext('2d');ctx.textAlign='center';ctx.fillStyle='#d1ecf4';ctx.font='400 76px sans-serif';ctx.fillText('AWAITING A RESPONSE',1024,170);ctx.fillStyle='#95b9c9';ctx.font='400 45px sans-serif';ctx.fillText('等待回响',1024,276);ctx.font='400 32px sans-serif';ctx.fillText('READ  ·  RESPOND  ·  CARE',1024,361);
 const signMap=new THREE.CanvasTexture(c);signMap.colorSpace=THREE.SRGBColorSpace;
 const sign=new THREE.Mesh(new THREE.PlaneGeometry(3.1,.775),new THREE.MeshBasicMaterial({map:signMap,transparent:true,depthWrite:false,side:THREE.DoubleSide}));sign.position.set(0,1.95,.09);waiting.add(sign);sign.userData.exhibit='first-contact';targets.push(sign);
 return {loadSky(){if(skyStarted)return;skyStarted=true;fetchBytes('./assets/space/milky-way.png').then(async bytes=>{const url=URL.createObjectURL(new Blob([bytes]));try{const texture=await new THREE.TextureLoader().loadAsync(url);texture.colorSpace=THREE.SRGBColorSpace;for(const sky of skies){sky.material.map=texture;sky.material.color.set('#ffffff');sky.material.needsUpdate=true;}}finally{URL.revokeObjectURL(url);}}).catch(()=>{skyStarted=false;});}};
}
