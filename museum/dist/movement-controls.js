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
