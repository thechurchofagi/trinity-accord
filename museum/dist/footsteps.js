// Quiet shoe contact: filtered friction and a short sole landing, no pitched thud.
export const FOOTSTEP_GAIN=.065;
export function footstepSamples(rate=24000){
 const data=new Float32Array(Math.ceil(rate*.19));let seed=173,low=0,high=0;
 for(let i=0;i<data.length;i++){
  const t=i/rate;seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  const noise=seed/2147483648-1;
  low+=(1-Math.exp(-2*Math.PI*260/rate))*(noise-low);
  high+=(1-Math.exp(-2*Math.PI*1900/rate))*((noise-low)-high);
  const landing=Math.exp(-(((t-.024)/.014)**2)),sole=.45*Math.exp(-(((t-.074)/.031)**2));
  data[i]=high*(landing+sole)*.75;
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
  source.playbackRate.value=step++%2?1.03:.98;gain.gain.value=FOOTSTEP_GAIN;
  source.connect(gain).connect(context.destination);source.onended=()=>{source.disconnect();gain.disconnect();};source.start();
 }
 return {unlock,get state(){return context?.state||'locked';},update(metres,active){
  if(!active||metres<.0001){moving=false;distance=0;return;}
  if(!moving){play();moving=true;distance=0;}
  distance+=metres;if(distance>=.72){distance%=.72;play();}
 }};
}
