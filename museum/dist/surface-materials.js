import * as THREE from './vendor/three.module.js';
import {architectureGeometry} from './spatial-layout.js';

// Metre-scaled surface detail stays crisp close up, without stretching a room-sized image.
export function mineralMaterial(color,{metal=false,roughness=.48}={}){
 const material=new THREE.MeshPhysicalMaterial({color,roughness,metalness:metal?.82:.04,envMapIntensity:metal?.8:.42,clearcoat:metal?0:.12,clearcoatRoughness:.5});
 material.name=metal?'Fine brushed titanium':'Honed pale mineral';if(!metal){material.specularIntensity=.12;material.clearcoat=0;}
 material.onBeforeCompile=shader=>{
  shader.vertexShader=shader.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 surfacePosition;').replace('#include <begin_vertex>','#include <begin_vertex>\nsurfacePosition=(modelMatrix*vec4(position,1.0)).xyz;');
  shader.fragmentShader=shader.fragmentShader.replace('#include <common>',`#include <common>
   varying vec3 surfacePosition;
   float grain(vec3 p){return fract(sin(dot(p,vec3(12.9898,78.233,37.719)))*43758.5453);}
  `).replace('#include <color_fragment>',`#include <color_fragment>
   // Fine, low-contrast mineral variation; no oversized speckles or repeated tiles.
   vec3 cell=floor(surfacePosition*180.0);
   float fade=1.0-smoothstep(.002,.018,length(fwidth(surfacePosition)));
   float micro=grain(cell)-.5;
   diffuseColor.rgb*=1.0+micro*.035*fade;
  `).replace('#include <roughnessmap_fragment>',`#include <roughnessmap_fragment>
   roughnessFactor=clamp(roughnessFactor+micro*.08*fade,.18,.85);
  `);
 };
 material.customProgramCacheKey=()=>`museum-fine-surface-${metal}`;
 return material;
}
export function addMineralFloors(scene,layout){
 const group=new THREE.Group();group.name='Fine mineral floor finish';const materials=new Map();
 for(const part of layout.architecture){
  if(!part.floor)continue;
  const def=layout.materials[part.material];if(!materials.has(part.material))materials.set(part.material,tileMaterial(def.color));
  const mesh=new THREE.Mesh(architectureGeometry(part),materials.get(part.material));mesh.name=part.name+' / fine finish';mesh.position.set(...(part.position||[0,0,0]));mesh.position.y+=.004;mesh.rotation.y=part.rotationY||0;group.add(mesh);
 }
 scene.add(group);return group;
}

// 80 cm warm ivory porcelain tiles, with narrow grout and derivative antialiasing.
export function tileMaterial(color='#d9d5c9'){
 const m=mineralMaterial(color,{roughness:.78}),base=m.onBeforeCompile;
 m.name='Warm ivory porcelain tiles';m.specularIntensity=.18;m.clearcoat=0;
 m.onBeforeCompile=s=>{base(s);s.fragmentShader=s.fragmentShader.replace('// Fine, low-contrast mineral variation; no oversized speckles or repeated tiles.',`vec2 tileUV=surfacePosition.xz/.8;
 vec2 edge=min(fract(tileUV),1.0-fract(tileUV));
 vec2 aa=max(fwidth(tileUV),vec2(.0005));
 vec2 seam=1.0-smoothstep(vec2(.0018),vec2(.0018)+aa,edge);
 float grout=max(seam.x,seam.y);
 float tileTone=grain(vec3(floor(tileUV),1.0));
 diffuseColor.rgb*=mix(.97+tileTone*.05,.72,grout);
 // Subtle mineral texture below.`);};m.customProgramCacheKey=()=> 'museum-ivory-tiles-v134';return m;
}
