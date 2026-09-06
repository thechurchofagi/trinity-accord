import * as THREE from './vendor/three.module.js';

// A stalled response must never hold the museum entrance indefinitely.
export async function fetchBytes(url,{timeout=15000,attempts=2,fetcher=fetch}={}){
 let last;
 for(let attempt=0;attempt<attempts;attempt++){
  const controller=new AbortController();let timer;
  try{
   return await Promise.race([
    (async()=>{const response=await fetcher(url,{signal:controller.signal});if(!response.ok)throw Error(`Resource ${response.status}: ${url}`);return response.arrayBuffer();})(),
    new Promise((_,reject)=>{timer=setTimeout(()=>{controller.abort();reject(Error(`Resource timed out: ${url}`));},timeout);})
   ]);
  }catch(error){last=error;}finally{clearTimeout(timer);}
 }
 throw last;
}

export function createResourceQueue(limit=3){
 let active=0;const pending=[];
 function pump(){pending.sort((a,b)=>a.priority()-b.priority());while(active<limit&&pending.length){const task=pending.shift();active++;Promise.resolve().then(task.work).then(task.resolve,task.reject).finally(()=>{active--;pump();});}}
 return {add(work,priority=()=>0){return new Promise((resolve,reject)=>{pending.push({work,priority,resolve,reject});pump();});}};
}

// The same corridor footprint is available before any model/image downloads.
export function createPreviewHall(layout){
 const group=new THREE.Group();group.name='Immediate corridor';
 const {width,length,height}=layout.dimensions,z=-(length-6)/2;
 const stone=new THREE.MeshStandardMaterial({color:'#b3b5b1',roughness:.86});
 const wall=new THREE.MeshStandardMaterial({color:'#d5d7d1',roughness:.9});
 for(const [w,h,d,x,y,depth,material] of [[width,.12,length,0,-.06,z,stone],[.12,height,length,-width/2-.06,height/2,z,wall],[.12,height,length,width/2+.06,height/2,z,wall],[width,.12,length,0,height+.06,z,wall]]){
  const mesh=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),material);mesh.position.set(x,y,depth);group.add(mesh);
 }
 const glow=new THREE.MeshBasicMaterial({color:'#badbe8',toneMapped:false});
 for(const side of [-1,1]){const strip=new THREE.Mesh(new THREE.BoxGeometry(.035,.035,length),glow);strip.position.set(side*(width/2-.14),height-.12,z);group.add(strip);}
 return {group,dispose(){group.traverse(o=>o.geometry?.dispose());stone.dispose();wall.dispose();glow.dispose();group.removeFromParent();}};
}
