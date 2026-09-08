import * as THREE from './vendor/three.module.js';
import {mineralMaterial} from './surface-materials.js';

// A neutral interior reflection for the gold. The crystal's blue studio reflection
// makes the exit-facing metal almost black; it is not an appropriate metal probe.
export function goldWindowMaterial(renderer){
 const interior=new THREE.Scene();interior.background=new THREE.Color('#34312b');
 for(const [x,y,z,w,h,color] of [[0,0,1.4,3.6,2.8,'#f4ead4'],[-2,1,1,1,3,'#ffffff'],[1.5,-1,1,.25,2,'#e3c99e']]){
  const panel=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color,side:THREE.DoubleSide}));
  panel.position.set(x,y,z);panel.lookAt(0,0,0);interior.add(panel);
 }
 const generator=new THREE.PMREMGenerator(renderer),reflection=generator.fromScene(interior,.025);generator.dispose();
 interior.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose();}});
 const gold=mineralMaterial('#d9ab50',{roughness:.29,metal:true});
 gold.name='Brushed gold window inlay';gold.metalness=1;gold.envMap=reflection.texture;gold.envMapIntensity=1;
 return gold;
}
