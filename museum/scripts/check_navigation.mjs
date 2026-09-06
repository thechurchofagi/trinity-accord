import assert from 'node:assert/strict';
import fs from 'node:fs';
import * as T from '../dist/vendor/three.module.js';
import {travelVector,turnView,stickVector} from '../dist/movement-controls.js';
import {galleryCamera,observationView} from '../dist/observation-view.js';
import {createFootsteps,footstepSamples,FOOTSTEP_GAIN} from '../dist/footsteps.js';
import {exhibitLabel} from '../dist/exhibit-label.js';
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-6,`${a} != ${b}`);
let view=turnView(0,0,195,0,390);near(view.yaw,-Math.PI);
let travel=travelVector(0,1,view.yaw);near(travel.z,1);
view=turnView(view.yaw,0,390,0,390);near(view.yaw,-3*Math.PI);
for(const yaw of [0,Math.PI/2,Math.PI,3*Math.PI/2]){const v=travelVector(1,1,yaw);near(Math.hypot(v.x,v.z),1);}
near(stickVector(0,0,30).y,0);near(stickVector(0,-30,30).y,1);
for(const [width,height,top,bottom] of [[390,844,105,436],[320,640,105,232],[1363,936,125,505],[600,390,85,160]]){
 const fit=galleryCamera(width,height,top,bottom),view=observationView(2.17,2.44,fit.fov,width/height,width<650,{height,top,bottom});
 const distance=Math.min(6.3,Math.max(2.2,view.distance)),camera=new T.PerspectiveCamera(fit.fov,width/height,.06,220);
 camera.setViewOffset(width,height,0,fit.offsetY,width,height);camera.position.set(0,1.65,distance);camera.lookAt(0,2.74,0);camera.updateMatrixWorld();
 for(const y of [1.72,3.82])for(const x of [-.968,.968]){const p=new T.Vector3(x,y,0).project(camera),py=(1-p.y)*height/2;assert.ok(py>=top&&py<=bottom,'Frame or plaque overlaps UI');assert.ok(Math.abs(p.x)<.96,'Frame clips horizontally');}
 assert.ok(camera.rotation.x>0,'Looking slightly upward');
}
// Exercise actual Web Audio node scheduling with an injected context, including resume.
let played=0,resumed=0,context;
class AudioNode {constructor(){this.playbackRate={};this.gain={};}connect(){return this;}disconnect(){}start(){played++;}}
class Context {constructor(){context=this;this.state='suspended';this.sampleRate=24000;this.destination={};}resume(){resumed++;this.state='running';return Promise.resolve();}createBuffer(){return {copyToChannel(){}};}createBufferSource(){return new AudioNode();}createGain(){return new AudioNode();}}
const feet=createFootsteps({Context});feet.unlock();await Promise.resolve();assert.equal(resumed,1);
feet.update(.01,true);assert.equal(played,1,'First real movement makes a step');
feet.update(.71,true);assert.equal(played,2,'Distance cadence');feet.update(0,false);feet.update(0,true);assert.equal(played,2,'No sound while still');
context.state='interrupted';feet.unlock();await Promise.resolve();assert.equal(resumed,2);
feet.update(.01,true);assert.equal(played,3);const samples=footstepSamples();const rms=Math.sqrt(samples.reduce((s,x)=>s+x*x,0)/samples.length)*FOOTSTEP_GAIN;assert.ok(rms>.001&&rms<.012,'Footsteps must remain quiet, below the previous thudding level');
const data=JSON.parse(fs.readFileSync(new URL('../dist/data/sources.json',import.meta.url)));
for(const e of data.items){const label=exhibitLabel(e);assert.ok(label.includes('Number '+String(e.ordinal).padStart(2,'0'))&&label.includes(e.date.slice(0,10))&&!label.includes('NFT'));}
console.log('PASS: unrestricted turning, view-relative normalized travel, four projected viewport sizes, upward gaze, gesture audio resume, first step/cadence/stopping, all NFT date labels. Hardware listening remains a separate check.');
