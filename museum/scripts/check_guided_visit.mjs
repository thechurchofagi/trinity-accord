import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {tourStops,tourDuration,tourPosition} from '../dist/tour-plan.js';
assert.equal(tourDuration,600);
assert.equal(tourPosition(600),null);
let time=0;for(let i=0;i<tourStops.length;i++){assert.equal(tourPosition(time).index,i);assert.equal(tourPosition(time+tourStops[i].seconds-.001).index,i);time+=tourStops[i].seconds;}
assert.deepEqual(tourStops.filter(s=>s.flaw!==undefined).map(s=>s.flaw),[0,1,2]);
const app=fs.readFileSync(new URL('../dist/museum.js',import.meta.url),'utf8');
const manifest=JSON.parse(fs.readFileSync(new URL('../dist/data/public-flaws.json',import.meta.url)));
for(const f of manifest.items){const data=fs.readFileSync(new URL('../dist/'+f.file,import.meta.url));assert.equal(crypto.createHash('sha256').update(data).digest('hex'),f.sha256);}
const calls=[],elements=new Map();function $(id){if(!elements.has(id))elements.set(id,{hidden:false,textContent:'',replaceChildren(){},pause(){calls.push('pause');}});return elements.get(id);}
const context={touring:false,tourElapsed:0,tourLast:0,tourStep:-1,tourMusicStarted:false,guideResume:null,recordedGuide:{currentTime:0,paint(){}},tourDuration,tourPosition,performance:{now:()=>1000},tourTimer:null,tourStops,lang:'zh',guideSound:false,roomData:{},motion:null,playRequest:0,$,time:String,tx:(zh)=>zh,window:{},closePanel(){},closeFlaws(){calls.push('closeFlaws');},silenceGuide(){calls.push('silence');},clearLyrics(){},updateUI(){calls.push('ui');},updateTourStatus(){},toast(){},setTimeout(){return 1;},clearTimeout(){},enterTourStop(p){context.tourStep=p.index;context.tourMusicStarted=false;calls.push(['stop',p.index]);},exhibits:new Map(tourStops.map(s=>[s.exhibit,{id:s.exhibit}])),soundFor:e=>e,playTrack(e,art,toggle,keep){assert.equal(keep,true);calls.push(['music',e.id]);}};
vm.createContext(context);
function load(name,next){vm.runInContext(app.slice(app.indexOf('function '+name+'('),app.indexOf('function '+next+'(')),context);}
load('stopTour','updateTourStatus');load('tourTick','startTour');load('startTour','showHelp');
context.startTour(true);assert.equal(context.touring,true);assert.deepEqual(calls.find(Array.isArray),['stop',0]);
for(let t=1200;t<=601400;t+=200)context.tourTick(t);
assert.equal(context.touring,false);assert.deepEqual(calls.filter(x=>Array.isArray(x)&&x[0]==='stop').map(x=>x[1]),tourStops.map((_,i)=>i));assert.equal(calls.filter(x=>Array.isArray(x)&&x[0]==='music').length,3);
context.tourElapsed=123;context.startTour();context.stopTour();assert.equal(context.tourElapsed,123);assert.equal(context.touring,false);const before=calls.length;context.tourTick(999999);assert.equal(calls.length,before,'stale timer must not advance after pause');
// A no-op stop must not rebuild menu buttons while a click is underway.
const count=calls.filter(x=>x==='ui').length;context.stopTour();assert.equal(calls.filter(x=>x==='ui').length,count);
assert.ok(!app.includes('yaw=Math.PI;camera.rotation.order'));
console.log('PASS: full 600-second runtime, all stops and music transitions, three exact public photos, pause/resume, stale timer cancellation, stable menu no-op, inward initial view.');
