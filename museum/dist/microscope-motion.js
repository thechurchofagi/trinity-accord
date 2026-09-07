import * as THREE from './vendor/three.module.js';
// The cutout is a camera-facing prop in the 3D scene, never part of the evidence image.
export function microscopePose(t,start,end){const p=Math.min(1,Math.max(0,t)),v=p*p*(3-2*p);return start.clone().lerp(end,v);}
export function createMicroscopeMotion(scene,camera,{loadTexture=()=>new THREE.TextureLoader().loadAsync('assets/flaws/hand-microscope.png'),requestFrame=callback=>requestAnimationFrame(callback),cancelFrame=id=>cancelAnimationFrame(id)}={}){
 let sprite=null,texture=null,loading=null,frame=0,generation=0;
 const load=()=>loading||(loading=loadTexture().then(map=>{
  texture=map;map.colorSpace=THREE.SRGBColorSpace;
  sprite=new THREE.Sprite(new THREE.SpriteMaterial({map,transparent:true,depthTest:true,depthWrite:false,toneMapped:false}));
  // Objective position in the original transparent prop; place that point at the target.
  sprite.center.set(.17,.79);sprite.scale.set(.68,.68*1199/1312,1);sprite.visible=false;scene.add(sprite);return sprite;
 }).catch(error=>{loading=null;throw error;}));
 function stop(){generation++;cancelFrame(frame);if(sprite)sprite.visible=false;}
 return {stop,prepare:load,
  async start(crystal,index,{reduced=false,onComplete=()=>{},onError=()=>{}}={}){
   stop();const id=generation;
   if(reduced){onComplete();return;}
   try{const prop=await load();if(id!==generation)return;
    camera.updateMatrixWorld();crystal.updateMatrixWorld(true);
    const points=[new THREE.Vector3(-.055,.235,.033),new THREE.Vector3(.045,.20,.033),new THREE.Vector3(-.01,.13,.033)];
    const end=crystal.localToWorld(points[index].clone());
    const start=camera.localToWorld(new THREE.Vector3(.55,-.34,-1.05));
    let begin=null;prop.visible=true;prop.material.opacity=1;
    const tick=now=>{if(id!==generation)return;if(begin===null)begin=now;const elapsed=(now-begin)/1000;
     prop.position.copy(microscopePose(elapsed/2.2,start,end));
     prop.scale.setScalar(.68);prop.scale.y*=1199/1312;
     if(elapsed>=2.8){prop.visible=false;onComplete();return;}frame=requestFrame(tick);
    };frame=requestFrame(tick);
   }catch(error){if(id===generation)onError(error);}
  },
  dispose(){stop();if(sprite){scene.remove(sprite);sprite.material.dispose();}texture?.dispose();}
 };
}
