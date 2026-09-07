import * as THREE from './vendor/three.module.js';

// Model geometry is a virtual exhibition prop; no photographic cutout is used.
export function createMicroscopeModel(){
 const root=new THREE.Group();root.name='virtual-hand-microscope';
 const metal=new THREE.MeshStandardMaterial({color:0x9daeb9,metalness:.72,roughness:.3});
 const housing=new THREE.MeshStandardMaterial({color:0x263d50,metalness:.25,roughness:.48});
 const rubber=new THREE.MeshStandardMaterial({color:0x14212d,roughness:.88});
 const glove=new THREE.MeshStandardMaterial({color:0xa2b9c7,roughness:.78,metalness:.03});
 const lens=new THREE.MeshStandardMaterial({color:0x235a79,emissive:0x14425a,emissiveIntensity:.35,metalness:.45,roughness:.12});
 const light=new THREE.MeshStandardMaterial({color:0xbbeaf3,emissive:0x66b7d3,emissiveIntensity:.5,roughness:.3});
 function mesh(geometry,material,position,parent=root){const m=new THREE.Mesh(geometry,material);m.position.set(...position);parent.add(m);return m;}
 function sphere(position,scale,material,parent=root){const m=mesh(new THREE.SphereGeometry(1,20,12),material,position,parent);m.scale.set(...scale);return m;}
 function segment(from,to,radius,material,parent=root){
  const a=new THREE.Vector3(...from),b=new THREE.Vector3(...to),delta=b.clone().sub(a);
  const m=mesh(new THREE.CapsuleGeometry(radius,Math.max(.001,delta.length()-2*radius),6,12),material,a.clone().add(b).multiplyScalar(.5).toArray(),parent);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),delta.normalize());return m;
 }
 const scope=new THREE.Group();scope.name='microscope';root.add(scope);
 // The optical axis points toward the crystal (-Z); the whole grip lifts in Y.
 function tube(radius,length,z,material){const m=mesh(new THREE.CylinderGeometry(radius,radius,length,32),material,[0,0,z],scope);m.rotation.x=Math.PI/2;return m;}
 tube(.033,.145,.055,housing);tube(.036,.046,.062,rubber);tube(.028,.055,-.045,metal);tube(.026,.012,-.077,rubber);tube(.019,.003,-.084,lens);
 const rim=mesh(new THREE.TorusGeometry(.023,.003,8,32),light,[0,0,-.084],scope);
 rim.name='objective-ring';
 tube(.030,.009,.134,metal);
 sphere([0,.033,.107],[.009,.003,.013],rubber,scope);sphere([0,.036,.107],[.002,.001,.003],light,scope);
 const dial=mesh(new THREE.CylinderGeometry(.015,.015,.01,24),metal,[.037,0,.102],scope);dial.rotation.z=Math.PI/2;
 for(let i=0;i<20;i++){const a=i*Math.PI/10;const rib=mesh(new THREE.BoxGeometry(.002,.002,.028),metal,[Math.sin(a)*.036,Math.cos(a)*.036,.062],scope);rib.rotation.z=-a;}
 const hand=new THREE.Group();hand.name='modelled-gloved-hand';root.add(hand);
 sphere([.054,-.052,.063],[.029,.052,.045],glove,hand);
 segment([.063,-.205,.109],[.054,-.098,.077],.027,glove,hand);
 const cuff=mesh(new THREE.CylinderGeometry(.029,.032,.027,20),housing,[.063,-.186,.103],hand);cuff.rotation.x=-.25;
 // Four rounded, jointed fingers curl over the barrel; the thumb opposes below it.
 for(let i=0;i<4;i++){
  const z=.016+i*.025,r=i===3?.009:.0105;
  const points=[[.056,-.036,z],[.042,.017,z],[.014,.039,z],[-.018,.020,z]];
  for(let j=0;j<points.length-1;j++)segment(points[j],points[j+1],r,glove,hand);
  for(const p of points.slice(1,-1))sphere(p,[r,r,r],glove,hand);
 }
 const thumb=[[.054,-.074,.026],[.020,-.049,-.003],[-.015,-.029,.008]];
 for(let i=0;i<2;i++)segment(thumb[i],thumb[i+1],.013,glove,hand);
 root.visible=false;return root;
}

// A straight vertical lift, with easing but no sideways slide across the glass.
export function microscopePose(t,start,end){const p=Math.min(1,Math.max(0,t)),v=p*p*(3-2*p);return new THREE.Vector3(end.x,THREE.MathUtils.lerp(start.y,end.y,v),end.z);}
export function createMicroscopeMotion(scene,camera,{requestFrame=callback=>requestAnimationFrame(callback),cancelFrame=id=>cancelAnimationFrame(id)}={}){
 let prop=null,frame=0,generation=0;
 const load=()=>{if(!prop){prop=createMicroscopeModel();scene.add(prop);}return Promise.resolve(prop);};
 function stop(){generation++;cancelFrame(frame);if(prop)prop.visible=false;}
 return {stop,prepare:load,
  async start(crystal,index,{reduced=false,onComplete=()=>{},onError=()=>{}}={}){
   stop();const id=generation;if(reduced){onComplete();return;}
   try{const model=await load();if(id!==generation)return;
    crystal.updateMatrixWorld(true);
    const points=[new THREE.Vector3(-.055,.235,.033),new THREE.Vector3(.045,.20,.033),new THREE.Vector3(-.01,.13,.033)];
    crystal.getWorldQuaternion(model.quaternion);
    const clearance=new THREE.Vector3(0,0,.115).applyQuaternion(model.quaternion);
    const end=crystal.localToWorld(points[index].clone()).add(clearance),start=end.clone().add(new THREE.Vector3(0,-.36,0));
    model.position.copy(start);model.visible=true;let begin=null;
    const tick=now=>{if(id!==generation)return;if(begin===null)begin=now;const elapsed=(now-begin)/1000;
     model.position.copy(microscopePose(elapsed/2.2,start,end));
     if(elapsed>=2.8){model.visible=false;onComplete();return;}frame=requestFrame(tick);
    };frame=requestFrame(tick);
   }catch(error){if(id===generation)onError(error);}
  },
  dispose(){stop();if(prop){scene.remove(prop);const geometries=new Set(),materials=new Set();prop.traverse(m=>{if(m.isMesh){geometries.add(m.geometry);materials.add(m.material);}});geometries.forEach(g=>g.dispose());materials.forEach(m=>m.dispose());prop=null;}}
 };
}
