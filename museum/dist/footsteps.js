// Default-on stone-floor footsteps. Unlock synchronously from a trusted gesture.
// Midrange heel/contact sound remains audible on small phone speakers.
export function footstepSamples(rate=24000){
 const data=new Float32Array(Math.ceil(rate*.22));let seed=173;
 for(let i=0;i<data.length;i++){
  const t=i/rate;seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  const noise=seed/2147483648-1;
  const heel=Math.sin(2*Math.PI*(210*t-190*t*t))*Math.exp(-t*35);
  const contact=noise*(Math.exp(-t*65)+.35*Math.exp(-Math.abs(t-.045)*100));
  data[i]=Math.min(1,t/.003)*(.52*heel+.42*contact);
 }
 return data;
}
export function createFootsteps({Context=globalThis.AudioContext||globalThis.webkitAudioContext,onState=()=>{}}={}){
 let context,buffer,distance=0,moving=false,step=0;
 function unlock(){
  try{
   if(!context&&Context){context=new Context();buffer=context.createBuffer(1,Math.ceil(context.sampleRate*.22),context.sampleRate);buffer.copyToChannel(footstepSamples(context.sampleRate),0);context.onstatechange=()=>onState(context.state);}
   if(context&&context.state!=='running')context.resume().then(()=>onState(context.state)).catch(()=>onState(context.state));
  }catch{onState('unavailable');}
 }
 function play(){
  if(context?.state!=='running')return;
  const source=context.createBufferSource(),gain=context.createGain();source.buffer=buffer;
  source.playbackRate.value=step++%2?1.04:.97;gain.gain.value=.32;
  source.connect(gain).connect(context.destination);source.onended=()=>{source.disconnect();gain.disconnect();};source.start();
 }
 return {unlock,get state(){return context?.state||'locked';},update(metres,active){
  if(!active||metres<.0001){moving=false;distance=0;return;}
  if(!moving){play();moving=true;distance=0;}
  distance+=metres;if(distance>=.72){distance%=.72;play();}
 }};
}
