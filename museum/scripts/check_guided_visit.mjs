import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import {tourStops,tourDuration,tourPosition} from '../dist/tour-plan.js';
assert.equal(tourDuration,580);
assert.equal(tourPosition(580),null);
let time=0;for(let i=0;i<tourStops.length;i++){assert.equal(tourPosition(time).index,i);assert.equal(tourPosition(time+tourStops[i].seconds-.001).index,i);time+=tourStops[i].seconds;}
assert.deepEqual(tourStops.filter(s=>s.inspectFlaw!==undefined).map(s=>s.inspectFlaw),[0]);
const app=fs.readFileSync(new URL('../dist/museum.js',import.meta.url),'utf8');
const manifest=JSON.parse(fs.readFileSync(new URL('../dist/data/public-flaws.json',import.meta.url)));
for(const f of manifest.items){const data=fs.readFileSync(new URL('../dist/'+f.file,import.meta.url));assert.equal(crypto.createHash('sha256').update(data).digest('hex'),f.sha256);}
const calls=[],elements=new Map();function $(id){if(!elements.has(id))elements.set(id,{hidden:false,ended:true,textContent:'',replaceChildren(){},pause(){calls.push('pause');}});return elements.get(id);}
const context={pendingTourView:null,document:{hidden:false},manualUntil:0,keys:new Set(),joystick:null,guideStop:0,inspectionPhase:'idle',tourInspectionComplete:false,tourShotIndex:0,reduced:false,spatialReady:false,tourLookChanged:false,tourInspectionStarted:false,flawIndex:-1,showFlaw(i){context.flawIndex=i;context.tourInspectionComplete=true;},touring:false,tourElapsed:0,tourLast:0,tourStep:-1,tourMusicStarted:false,guideResume:null,recordedGuide:{state:'playing',currentTime:0,paint(){},setMuted(){this.state='playing';}},tourDuration,tourPosition,performance:{now:()=>1000},tourTimer:null,tourStops,lang:'zh',guideSound:false,musicPlayback:{state:'idle',waiting:false,recovering:false},cancelMusic(){context.playRequest++;context.musicPlayback.state='idle';context.musicPlayback.waiting=false;},resumeAudio(){if(context.musicPlayback.waiting){context.musicPlayback.waiting=false;context.musicPlayback.state='playing';}else context.recordedGuide.setMuted(false);},roomData:{},motion:null,playRequest:0,$,time:String,tx:(zh)=>zh,window:{},closePanel(){},closeFlaws(){context.flawIndex=-1;calls.push('closeFlaws');},silenceGuide(){calls.push('silence');},clearLyrics(){},updateUI(){calls.push('ui');},updateTourStatus(){},toast(){},setTimeout(){return 1;},clearTimeout(){},enterTourStop(p){context.tourStep=p.index;context.tourMusicStarted=false;calls.push(['stop',p.index]);},exhibits:new Map([...tourStops.map(s=>[s.exhibit,{id:s.exhibit}]),['eth-049',{id:'eth-049'}]]),focusExhibit(){},soundFor:e=>e,playTrack(e,art,toggle,keep){assert.equal(keep,true);calls.push(['music',e.id]);}};
vm.createContext(context);
function load(name,next){vm.runInContext(app.slice(app.indexOf('function '+name+'('),app.indexOf('function '+next+'(')),context);}
load('audioWaiting','syncAudioHold');load('stopTour','updateTourStatus');load('tourTick','startTour');load('startTour','showHelp');
context.startTour(true);assert.equal(context.touring,true);assert.deepEqual(calls.find(Array.isArray),['stop',0]);
for(let t=1200;t<=581400;t+=200)context.tourTick(t);
assert.equal(context.touring,false);assert.deepEqual(calls.filter(x=>Array.isArray(x)&&x[0]==='stop').map(x=>x[1]),tourStops.map((_,i)=>i));assert.equal(calls.filter(x=>Array.isArray(x)&&x[0]==='music').length,1);
context.tourElapsed=123;context.startTour();context.stopTour();assert.equal(context.tourElapsed,123);assert.equal(context.touring,false);const before=calls.length;context.tourTick(999999);assert.equal(calls.length,before,'stale timer must not advance after pause');
// A no-op stop must not rebuild menu buttons while a click is underway.
const count=calls.filter(x=>x==='ui').length;context.stopTour();assert.equal(calls.filter(x=>x==='ui').length,count);
// Blocked narration must hold the clock and all automatic stop/music changes.
context.tourElapsed=0;context.tourStep=-1;context.guideSound=true;context.startTour(true);
context.recordedGuide.state='blocked';const stopped=calls.filter(Array.isArray).length;
for(let t=2000;t<620000;t+=200)context.tourTick(t);
assert.equal(context.tourElapsed,0);assert.equal(calls.filter(Array.isArray).length,stopped);
context.resumeAudio();assert.equal(context.touring,true);assert.equal(context.recordedGuide.state,'playing');
context.tourTick(620200);assert.ok(context.tourElapsed>0);context.stopTour();
assert.ok(!app.includes('yaw=Math.PI;camera.rotation.order'));
console.log('PASS: full 580-second runtime, all stops and music transitions, three exact public photos, pause/resume, stale timer cancellation, stable menu no-op, inward initial view.');

// Later song rejection holds both the stop and its clock for as long as needed.
context.tourElapsed=tourStops.slice(0,tourStops.findIndex(s=>s.musicAt!==undefined)).reduce((sum,s)=>sum+s.seconds,0)+tourStops.find(s=>s.musicAt!==undefined).musicAt+1;context.startTour(true);
const heldTime=context.tourElapsed,heldStop=context.tourStep;context.musicPlayback.state='blocked';context.musicPlayback.waiting=true;
for(let t=700000;t<800000;t+=200)context.tourTick(t);
assert.equal(context.tourElapsed,heldTime);assert.equal(context.tourStep,heldStop);
context.resumeAudio();assert.equal(context.touring,true);assert.equal(context.musicPlayback.state,'playing');context.tourTick(800200);assert.ok(context.tourElapsed>heldTime);context.stopTour();

// Completion must remain distinct from a visitor pause in the visible status.
context.guideRecovery=false;context.guideRate=1;context.flawIndex=-1;
$('guide-speed').setAttribute=()=>{};
load('updateTourStatus','enterTourStop');
context.tourElapsed=580;context.updateTourStatus();
assert.match($('tour-progress').textContent,/已完成/);
assert.doesNotMatch($('tour-progress').textContent,/暂停/);
context.tourElapsed=120;context.updateTourStatus();
assert.match($('tour-progress').textContent,/暂停/);
