import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {tourStops,tourDuration,tourPosition} from '../dist/tour-plan.js';
const app=fs.readFileSync(new URL('../dist/museum.js',import.meta.url),'utf8');
assert.equal(tourStops.length,12);assert.equal(tourPosition(tourDuration),null);assert.equal(tourStops.filter(s=>s.musicDuration===30).length,2);
let total=0;for(let i=0;i<tourStops.length;i++){assert.equal(tourPosition(total).index,i);total+=tourStops[i].seconds;}
const elements=new Map(),calls=[];const $=id=>{if(!elements.has(id))elements.set(id,{hidden:false,open:false,ended:false,currentTime:0,duration:100});return elements.get(id);};
const c={tourStops,tourDuration,tourPosition,$,touring:true,tourElapsed:0,tourLast:0,tourStep:0,tourMusicStarted:false,tourMusicComplete:false,tourInspectionStarted:false,tourInspectionComplete:false,tourTimer:null,guideResume:null,guideStop:0,guideSound:true,flawIndex:-1,inspectionPhase:'idle',motion:null,pendingTourView:null,manualUntil:0,keys:new Set(),joystick:null,document:{hidden:false},performance:{now:()=>1000},recordedGuide:{state:'playing',currentTime:0,paint(){}},musicPlayback:{waiting:false},audioWaiting(){return c.recordedGuide.state==='blocked'||c.musicPlayback.waiting;},setTimeout(){return 1;},cancelMusic(){calls.push('music-stopped');},clearLyrics(){},silenceGuide(){c.recordedGuide.state='idle';},playTrack(e){calls.push('music-started');},soundFor:e=>e,exhibits:new Map(tourStops.map(s=>[s.musicExhibit||s.exhibit,{id:s.musicExhibit||s.exhibit}])),updateTourStatus(){},updateUI(){},stopTour(){c.touring=false;},enterTourStop(p){calls.push(['enter',p.index]);c.tourStep=p.index;c.tourMusicStarted=false;c.tourMusicComplete=false;c.tourInspectionStarted=false;c.tourInspectionComplete=false;c.recordedGuide.state='playing';$('narration').ended=false;},showFlaw(index){calls.push(['flaw',index]);c.flawIndex=index;c.guideStop=-1;c.inspectionPhase='reading';c.recordedGuide.state='playing';$('narration').ended=false;},closeFlaws(){c.flawIndex=-1;}};
vm.createContext(c);vm.runInContext(app.slice(app.indexOf('function tourTick('),app.indexOf('function startTour(')),c);
// A completed explanation leaves immediately, with no fixed-budget dead time.
$('narration').ended=true;c.tourElapsed=1;c.tourTick(1000);assert.equal(c.tourStep,1);
// Playback must finish before transition, even after arbitrarily delayed timer ticks.
c.tourStep=0;c.tourElapsed=0;c.recordedGuide.state='playing';$('narration').ended=false;c.tourTick(999999);assert.equal(c.tourStep,0);
$('narration').ended=true;c.motion={walk:true};c.tourTick(1000199);assert.equal(c.tourStep,0,'Cross-room walking must arrive before advancing');
c.motion=null;c.tourTick(1000399);assert.equal(c.tourStep,1);
// A song ends after thirty seconds of media playback, even while still walking.
$('narration').ended=true;c.motion={walk:true};c.tourTick(1000599);assert.ok(c.tourMusicStarted);$('music').currentTime=29.9;c.tourTick(1000799);assert.equal(c.tourMusicComplete,false);
$('music').currentTime=30.01;c.tourTick(1000999);assert.ok(c.tourMusicComplete);assert.equal(c.tourStep,1);assert.ok(calls.includes('music-stopped'));
c.motion=null;c.tourTick(1001199);assert.equal(c.tourStep,2);
// Blocked audio and hidden tabs preserve the current station and progress.
const held=c.tourElapsed;c.recordedGuide.state='blocked';for(let i=0;i<10;i++)c.tourTick(2000000+i*1000);assert.equal(c.tourElapsed,held);assert.equal(c.tourStep,2);
c.recordedGuide.state='playing';c.document.hidden=true;$('narration').ended=true;c.tourTick(3000000);assert.equal(c.tourStep,2);c.document.hidden=false;
// All three distinct original-photo explanations are awaited in order.
c.tourElapsed=tourStops.slice(0,8).reduce((n,s)=>n+s.seconds,0);c.tourStep=8;$('narration').ended=true;c.tourTick(3000200);assert.equal(c.flawIndex,0);
for(let i=0;i<3;i++){$('narration').ended=true;c.tourTick(3000400+i*200);}
assert.deepEqual(calls.filter(x=>Array.isArray(x)&&x[0]==='flaw').map(x=>x[1]),[0,1,2]);assert.equal(c.tourStep,9);
// Only an explicit tour close or natural completion stops guidance.
const navigation=app.slice(app.indexOf('function bindNavigation('),app.indexOf('function animate('));assert.ok(!navigation.includes('stopTour('));
c.touring=false;const before=c.tourElapsed;c.tourTick(9999999);assert.equal(c.tourElapsed,before);
console.log('PASS: twelve event-driven stops, no idle budget waits, walking arrival, two 30-second excerpts, audio recovery and sequential flaw explanations.');
