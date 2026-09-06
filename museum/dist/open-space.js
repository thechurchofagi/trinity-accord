import * as THREE from './vendor/three.module.js';

// Later exhibition scenery; no astronomical measurement or live reception feed.
export function addOpenSpace(scene, targets, sculptures){
 const texture=new THREE.TextureLoader().load('./assets/space/milky-way.png');texture.colorSpace=THREE.SRGBColorSpace;
 for(const [z,rotation] of [[-112,0],[48,Math.PI]]){
  const sky=new THREE.Mesh(new THREE.PlaneGeometry(170,113),new THREE.MeshBasicMaterial({map:texture,fog:false,toneMapped:false}));
  sky.position.set(0,15,z);sky.rotation.y=rotation;scene.add(sky);
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
}
