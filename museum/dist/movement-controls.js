// Pointer-captured analogue stick; view-relative movement is shared with keyboard input.
export function stickVector(dx,dy,radius){
 const distance=Math.hypot(dx,dy),amount=Math.min(distance/radius,1);
 const speed=amount<.12?0:Math.pow((amount-.12)/.88,1.35);
 return {x:distance?dx/distance*speed:0,y:distance?-dy/distance*speed:0,px:distance?dx/distance*Math.min(distance,radius):0,py:distance?dy/distance*Math.min(distance,radius):0};
}
export function travelVector(side,forward,yaw){
 const length=Math.max(1,Math.hypot(side,forward));side/=length;forward/=length;
 return {x:-Math.sin(yaw)*forward+Math.cos(yaw)*side,z:-Math.cos(yaw)*forward-Math.sin(yaw)*side};
}
export function turnView(yaw,pitch,dx,dy,width){
 // A half-screen sweep turns 180 degrees; yaw has no artificial stop.
 return {yaw:yaw-dx*Math.PI*2/Math.max(width,240),pitch:Math.max(-1.15,Math.min(1.15,pitch-dy*.004))};
}
// Wheel input queues a short, speed-limited walk in the current viewing direction.
// Listen only on the scene: scrolling details/lyrics and Ctrl+wheel zoom stay native.
export function createWheelWalk(canvas,onStart=()=>{},win=window,doc=document){
 let remaining=0;
 const reset=()=>{remaining=0;};
 canvas.addEventListener('wheel',e=>{
  if(e.ctrlKey||!Number.isFinite(e.deltaY)||!e.deltaY||Math.abs(e.deltaX)>Math.abs(e.deltaY))return;
  e.preventDefault();onStart();
  const pixels=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?win.innerHeight:1);
  const delta=Math.max(-.8,Math.min(.8,-pixels*.004));
  if(Math.sign(delta)!==Math.sign(remaining))remaining=0;
  remaining=Math.max(-1.6,Math.min(1.6,remaining+delta));
 },{passive:false});
 win.addEventListener('blur',reset);doc.addEventListener('visibilitychange',()=>{if(doc.hidden)reset();});
 return {reset,consume(maxDistance){const step=Math.sign(remaining)*Math.min(Math.abs(remaining),Math.max(0,maxDistance));remaining-=step;return step;}};
}
export function createJoystick(pad,onStart=()=>{}){
 const state={x:0,y:0,active:false};let pointer=null;
 const reset=()=>{state.x=state.y=0;state.active=false;const old=pointer;pointer=null;if(old!==null&&pad.hasPointerCapture(old))pad.releasePointerCapture(old);pad.classList.remove('active');pad.style.setProperty('--stick-x','0px');pad.style.setProperty('--stick-y','0px');};
 const update=e=>{const r=pad.getBoundingClientRect(),v=stickVector(e.clientX-r.left-r.width/2,e.clientY-r.top-r.height/2,r.width*.3);state.x=v.x;state.y=v.y;pad.style.setProperty('--stick-x',v.px+'px');pad.style.setProperty('--stick-y',v.py+'px');};
 pad.addEventListener('pointerdown',e=>{if(pointer!==null||e.button!==0)return;e.preventDefault();onStart();pointer=e.pointerId;state.active=true;pad.setPointerCapture(pointer);pad.classList.add('active');pad.focus({preventScroll:true});update(e);});
 pad.addEventListener('pointermove',e=>{if(e.pointerId===pointer){e.preventDefault();update(e);}});
 for(const type of ['pointerup','pointercancel','lostpointercapture'])pad.addEventListener(type,e=>{if(e.pointerId===pointer)reset();});
 pad.addEventListener('contextmenu',e=>e.preventDefault());window.addEventListener('blur',reset);document.addEventListener('visibilitychange',()=>{if(document.hidden)reset();});
 return {state,reset};
}

// Physical keys work with caps lock and alternate keyboard layouts.
export function movementKey(event){
 const arrows=['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'];
 if(arrows.includes(event.key))return event.key;
 const key=/^Key[WASDQE]$/.test(event.code||'')?event.code.slice(3).toLowerCase():event.key?.toLowerCase();
 return ['w','a','s','d','q','e'].includes(key)?key:null;
}
