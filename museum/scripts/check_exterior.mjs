import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as T from '../dist/vendor/three.module.js';
import {addOpenSpace,starDirection} from '../dist/open-space.js';
const catalog=JSON.parse(fs.readFileSync(new URL('../dist/data/bright-stars.json',import.meta.url)));
assert.equal(catalog.stars.length,925);
assert(catalog.stars.every(([id,ra,dec,mag])=>id>0&&ra>=0&&ra<24&&Math.abs(dec)<=90&&mag<=4.5));
assert(starDirection(6,0).distanceTo(new T.Vector3(0,0,-1))<1e-12);
assert(starDirection(0,0).distanceTo(new T.Vector3(1,0,0))<1e-12);
// Canvas is used only for the existing invitation sign, never the exterior.
globalThis.document={createElement:()=>({getContext:()=>({fillText(){}})})};
const scene=new T.Scene(),targets=[],sculptures=[];
const exterior=addOpenSpace(scene,targets,sculptures,catalog);
const earth=scene.getObjectByName('NASA EPIC Earth'),stars=scene.getObjectByName('HYG naked-eye bright stars');
assert.equal(earth.material.toneMapped,false);assert.equal(earth.material.fog,false);
assert.equal(stars.material.depthTest,true);assert.equal(stars.material.depthWrite,false);
assert(stars.material.fragmentShader.includes('\n#include <colorspace_fragment>\n'));
let counts=[];
for(const [w,h] of [[390,844],[430,932],[1440,900],[1920,1080]]){
 const camera=new T.PerspectiveCamera(w<650?76:66,w/h,.06,220);
 let initial;
 for(const p of [[0,1.65,-2],[2.5,1.65,-30],[-2.5,2.87,-65]]){
  camera.position.fromArray(p);exterior.update(camera,2);scene.updateMatrixWorld(true);
  const relative=earth.getWorldPosition(new T.Vector3()).sub(camera.position);
  if(initial)assert(relative.distanceTo(initial)<1e-10);else initial=relative;
  assert(relative.x<0&&relative.y>0,'Earth must sit off the entrance axis');assert(relative.z>0&&relative.z<camera.far);
  const projectedWidth=earth.scale.x/(2*179*Math.tan(T.MathUtils.degToRad(camera.fov/2))*camera.aspect);
  assert(projectedWidth<=.831,'Earth square exceeds narrow viewport');
  const horizontalSpan=2*179*Math.tan(T.MathUtils.degToRad(camera.fov/2))*camera.aspect;
  const centre=.5-relative.x/horizontalSpan;
  assert(centre>=.60&&centre<=.661,'Earth remains visibly off-centre');
  // EPIC globe radius is at most 40% of its black square canvas width.
  assert(centre+projectedWidth*.4<1,'Earth limb clips a narrow viewport');
  assert(scene.getObjectByName('NASA EPIC Earth transition').position.distanceTo(earth.position)<1e-10);
  assert.equal(scene.getObjectByName('Distant exterior').rotation.y,0);
 }
 const pos=stars.geometry.getAttribute('position');let visible=0;
 camera.position.set(0,1.65,-65);camera.rotation.set(0,0,0);camera.updateMatrixWorld();exterior.update(camera,2);scene.updateMatrixWorld(true);
 for(let i=0;i<pos.count;i++){
  const v=new T.Vector3().fromBufferAttribute(pos,i);assert(v.z<0);assert(Math.abs(v.length()-185)<.00002);
  v.applyMatrix4(stars.matrixWorld).project(camera);if(Math.abs(v.x)<1&&Math.abs(v.y)<1&&v.z<1)visible++;
 }
 assert(visible>=45&&visible<=200,'Unexpected star density');counts.push([w,h,visible]);
}
assert.equal(sculptures[0].base,.65);assert.equal(targets.length,3);
console.log('PASS: fixed celestial orientation, zero translation parallax, off-centre Earth and unclipped phone framing, magnitude-layered catalog stars',JSON.stringify(counts));
