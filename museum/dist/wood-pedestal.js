import * as THREE from './vendor/three.module.js';
// Cylindrical walnut support at physical scale. The navigation radius comes from the same layout.
export function addWoodPedestal(scene,layout,targets){
 const c=layout.crystal,floor=layout.rooms.find(r=>r.id==='originals').floor;
 const mat=new THREE.MeshPhysicalMaterial({color:'#49301f',roughness:.68,metalness:0,specularIntensity:.22,envMapIntensity:.22});
 mat.onBeforeCompile=shader=>{
  shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 woodPosition; varying float woodCap;').replace('#include <begin_vertex>','#include <begin_vertex>\nwoodPosition=position; woodCap=abs(normal.y);');
  shader.fragmentShader=shader.fragmentShader.replace('#include <common>','#include <common>\nvarying vec3 woodPosition; varying float woodCap;').replace('#include <color_fragment>',`#include <color_fragment>
  float angle=atan(woodPosition.z,woodPosition.x);
  float veins=sin(angle*62.0+sin(woodPosition.y*3.1+angle*5.0)*1.6);
  float pores=sin(angle*390.0+woodPosition.y*5.0);
  // End grain on horizontal caps; long grain on the vertical barrel.
  // A low-contrast, off-centre ring avoids radial stripes converging at the centre.
  float rings=sin(length(woodPosition.xz+vec2(.16,.09))*190.0+sin(woodPosition.x*19.0)*.45);
  float cap=smoothstep(.65,.9,woodCap);
  diffuseColor.rgb*=mix(.94+.045*veins+.012*pores,.94+.04*rings,cap);
  `);
 };
 const plinth=new THREE.Mesh(new THREE.CylinderGeometry(c.pedestalRadius,c.pedestalRadius,c.pedestalHeight,96,1),mat);
 plinth.name='Walnut cylindrical support / 1.45m';plinth.position.set(c.x,floor+c.pedestalHeight/2,c.z);plinth.userData.exhibit='physical-alpha';scene.add(plinth);targets.push(plinth);
 const top=new THREE.Mesh(new THREE.CylinderGeometry(c.pedestalRadius-.008,c.pedestalRadius,.012,96),mat);top.position.set(c.x,c.baseY-.006,c.z);scene.add(top);return plinth;
}
