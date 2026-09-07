// Keep the tour waiting for an audible recording, including later interruptions.
export function createMusicPlayback(audio,{onState=()=>{}}={}){
 let state='idle',request=0,recovering=false;
 function setState(next){
  state=next;
  if(['blocked','error'].includes(next))recovering=true;
  if(['idle','playing','paused','ended'].includes(next))recovering=false;
  onState(next);
 }
 audio.addEventListener('playing',()=>{if(!['idle','paused'].includes(state))setState('playing');});
 audio.addEventListener('pause',()=>{if(state==='playing'&&!audio.ended)setState('blocked');});
 audio.addEventListener('ended',()=>{if(state!=='idle')setState('ended');});
 audio.addEventListener('error',()=>{if(!['idle','paused'].includes(state))setState('error');});
 for(const event of ['waiting','stalled'])audio.addEventListener(event,()=>{
  if(state==='playing'){recovering=true;setState('loading');}
 });
 return {
  get state(){return state;},get recovering(){return recovering;},
  get waiting(){return ['loading','blocked','error','paused'].includes(state);},
  async play(){
   const id=++request;setState('loading');
   try{await audio.play();if(id!==request)return false;setState('playing');return true;}
   catch(error){if(id!==request)return false;setState(error.name==='NotAllowedError'?'blocked':'error');return false;}
  },
  pause(){request++;setState('paused');audio.pause();},
  stop(){request++;setState('idle');audio.pause();}
 };
}
