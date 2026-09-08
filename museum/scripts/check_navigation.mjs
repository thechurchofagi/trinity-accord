import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as T from '../dist/vendor/three.module.js';
import {travelVector,turnView,stickVector,createWheelWalk,movementKey} from '../dist/movement-controls.js';
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
 const fit=galleryCamera(width,height,top,bottom),view=observationView(2.05,2.34,fit.fov,width/height,width<650,{height,top,bottom});
 const distance=Math.min(6.3,Math.max(2.2,view.distance)),camera=new T.PerspectiveCamera(fit.fov,width/height,.06,220);
 camera.setViewOffset(width,height,0,fit.offsetY,width,height);camera.position.set(0,2.87,distance);camera.lookAt(0,2.87,0);camera.updateMatrixWorld();
 for(const y of [1.72,3.99])for(const x of [-.968,.968]){const p=new T.Vector3(x,y,0).project(camera),py=(1-p.y)*height/2;assert.ok(py>=top&&py<=bottom,'Frame or plaque overlaps UI');assert.ok(Math.abs(p.x)<.96,'Frame clips horizontally');}
 near(camera.rotation.x,0);
 const topWidth=new T.Vector3(.95,3.45,0).project(camera).x-new T.Vector3(-.95,3.45,0).project(camera).x;
 const bottomWidth=new T.Vector3(.95,1.75,0).project(camera).x-new T.Vector3(-.95,1.75,0).project(camera).x;
 near(topWidth,bottomWidth); // Parallel picture edges: no automatic upward keystone distortion.
}
class Surface extends EventTarget {innerHeight=800;hidden=false;}
const canvas=new Surface(),win=new Surface(),doc=new Surface();let started=0;
const wheel=createWheelWalk(canvas,()=>started++,win,doc);
function scroll(deltaY,deltaMode=0,ctrlKey=false,deltaX=0){const e=new Event('wheel',{cancelable:true});Object.assign(e,{deltaY,deltaMode,ctrlKey,deltaX});canvas.dispatchEvent(e);return e;}
assert.equal(scroll(-100).defaultPrevented,true);near(wheel.consume(.1),.1);near(wheel.consume(1),.3);near(wheel.consume(1),0);
scroll(-100);scroll(100);near(wheel.consume(1),-.4); // Reverse immediately, without a forward backlog.
scroll(-3,1);near(wheel.consume(1),.192);scroll(-1,2);near(wheel.consume(1),.8);
for(let i=0;i<20;i++)scroll(-100);near(wheel.consume(10),1.6);
assert.equal(scroll(-100,0,true).defaultPrevented,false);near(wheel.consume(1),0);
assert.equal(scroll(-10,0,false,100).defaultPrevented,false);near(wheel.consume(1),0);
scroll(-100);win.dispatchEvent(new Event('blur'));near(wheel.consume(1),0);
scroll(-100);doc.hidden=true;doc.dispatchEvent(new Event('visibilitychange'));near(wheel.consume(1),0);
for(const fps of [20,60,120]){scroll(-100);let metres=0;for(let i=0;i<fps;i++)metres+=wheel.consume(1.38/fps);near(metres,.4);}
assert.ok(started>0);
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
assert.ok(FOOTSTEP_GAIN<=.065,'Shoe contact amplitude stays at most half the previous edition');
for(const e of data.items){for(const zh of [false,true]){const label=exhibitLabel(e,zh);assert.ok(label.startsWith(`No. ${String(e.ordinal).padStart(2,'0')}  ·  ${e.date.slice(0,10)}`));assert.ok(label.includes(zh?'事件:':'Event:'));}}
// Run the actual selection handler: approach/play once, then open details without restarting audio.
const app=fs.readFileSync(new URL('../dist/museum.js',import.meta.url),'utf8'),calls=[];
const selectionContext={touring:false,spatialReady:true,approachedExhibit:null,showExhibit:id=>calls.push(['details',id]),stopTour(){},focusExhibit:id=>calls.push(['approach',id]),$:()=>({hidden:false}),exhibits:new Map([['eth-001',{id:'eth-001'}],['eth-020',{id:'eth-020'}]]),soundFor:e=>e,playTrack:e=>calls.push(['play',e.id]),musicItem:null};
vm.createContext(selectionContext);vm.runInContext(app.slice(app.indexOf('function approachExhibit('),app.indexOf('function roomView(')),selectionContext);
selectionContext.approachExhibit('eth-001');selectionContext.approachExhibit('eth-001');selectionContext.approachExhibit('eth-020');
assert.deepEqual(calls,[['approach','eth-001'],['play','eth-001'],['details','eth-001'],['approach','eth-020'],['play','eth-020']]);
selectionContext.spatialReady=false;selectionContext.approachExhibit('eth-001');assert.deepEqual(calls.at(-1),['details','eth-001']);
console.log('PASS: wheel travel/reversal/units/zoom isolation/focus cleanup/frame-rate independence, unrestricted turning, normalized travel, four projected viewports, parallel artwork edges, quieter footsteps and compact historical labels.');

for(const event of [{key:'W',code:'KeyW'},{key:'w',code:'KeyW'},{key:'ц',code:'KeyW'}])assert.equal(movementKey(event),'w');
assert.equal(movementKey({key:'ArrowUp'}),'ArrowUp');assert.equal(movementKey({key:'Tab'}),null);
assert.ok(!app.includes('followDesktopMouse'),'Hover must never rotate the camera');
const navigation=app.slice(app.indexOf('function bindNavigation('),app.indexOf('function animate('));assert.ok(!navigation.includes('stopTour('));assert.ok(!navigation.includes('INPUT|BUTTON|A|TEXTAREA'),'Button focus must not disable walking');
