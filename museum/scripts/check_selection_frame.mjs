import assert from 'node:assert/strict';
import * as THREE from '../dist/vendor/three.module.js';
import {createSelectionFrame} from '../dist/selection-frame.js';
const scene=new THREE.Scene(),frame=createSelectionFrame(scene);
const first={x:1,y:2,z:-3,angle:Math.PI/2,width:1.7,height:1.7};
assert.equal(frame.group.visible,false);assert.equal(frame.group.children.length,12);
frame.update(first,0);assert.equal(frame.group.visible,true);assert.deepEqual(frame.group.position.toArray(),[1,2,-3]);assert.equal(frame.group.rotation.y,Math.PI/2);
for(const mesh of frame.group.children){const {x,y}=mesh.position;assert.ok(Math.abs(x)-mesh.scale.x/2>=first.width/2||Math.abs(y)-mesh.scale.y/2>=first.height/2,'Glow must not cover the original image');assert.equal(mesh.material.depthWrite,false);}
const material=frame.group.children[8].material;let previous=0;
for(let ms=0;ms<=9600;ms+=16){frame.update(first,ms);assert.ok(material.opacity>=.683&&material.opacity<=.901);if(ms)assert.ok(Math.abs(material.opacity-previous)<.003,'Slow continuous breath');previous=material.opacity;}
const second={...first,x:-4,width:1.4,height:.9};frame.update(second,0);assert.equal(scene.children.length,1,'Only one selection outline');assert.equal(frame.group.position.x,-4);
const before=frame.group.children[0].scale.x;second.width=1.8;frame.update(second,0);assert.ok(frame.group.children[0].scale.x>before,'Follow decoded image dimensions');
frame.update(second,0,{desktop:false});assert.equal(frame.group.visible,false);
frame.update(null,0);assert.equal(frame.group.visible,false);
frame.update(second,0,{reducedMotion:true});const steady=material.opacity;frame.update(second,1200,{reducedMotion:true});assert.equal(material.opacity,steady);
frame.dispose();assert.equal(scene.children.length,0);
console.log('PASS: one selected frame, no image coverage, gentle bounded pulse, resize, mobile off, reduced-motion steady and cleanup.');
