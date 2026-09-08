import * as THREE from './vendor/three.module.js';
// Cylindrical walnut support at physical scale. The navigation radius comes from the same layout.
export function addWoodPedestal(scene,layout,targets){
 const c=layout.crystal,floor=layout.rooms.find(r=>r.id==='originals').floor;
 const mat=new THREE.MeshStandardMaterial({color:'#805b38',roughness:.36,metalness:0,envMapIntensity:.4});
 mat.onBeforeCompile=shader=>{
  shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 woodPosition;').replace('#include <begin_vertex>','#include <begin_vertex>\nwoodPosition=position;');
  shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 woodPosition;').replace('#include <color_fragment>',`#include <color_fragment>
  float angle=atan(woodPosition.z,woodPosition.x);
  float veins=sin(angle*96.0+sin(woodPosition.y*3.1+angle*8.0)*1.6);
  float pores=sin(angle*390.0+woodPosition.y*5.0);
  diffuseColor.rgb*=.87+.12*veins+.025*pores;
  `);
 };
 const plinth=new THREE.Mesh(new THREE.CylinderGeometry(c.pedestalRadius,c.pedestalRadius,c.pedestalHeight,96,1),mat);
 plinth.name='Walnut cylindrical support / 1.45m';plinth.position.set(c.x,floor+c.pedestalHeight/2,c.z);plinth.userData.exhibit='physical-alpha';scene.add(plinth);targets.push(plinth);
 const top=new THREE.Mesh(new THREE.CylinderGeometry(c.pedestalRadius-.008,c.pedestalRadius,.012,96),mat);top.position.set(c.x,c.baseY-.006,c.z);scene.add(top);return plinth;
}
