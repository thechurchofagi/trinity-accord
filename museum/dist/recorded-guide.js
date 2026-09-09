// Audio and captions share the recording's clock; never depend on installed voices.
export function guideCueAt(cues,seconds){
 let lo=0,hi=cues.length-1,found=-1;
 while(lo<=hi){const mid=(lo+hi)>>1;if(cues[mid].start<=seconds){found=mid;lo=mid+1;}else hi=mid-1;}
 const cue=cues[found];return cue&&seconds<=cue.end+.25?cue:null;
}
export function createRecordedGuide(audio,{onCaption=()=>{},onState=()=>{}}={}){
 let track=null,request=0,state='idle',rate=1;
 const paint=()=>{const cue=track?guideCueAt(track.cues,audio.currentTime):null;onCaption(cue?.text||'',track?.language,cue,audio.currentTime);};
 function setState(value){state=value;onState(value);}
 for(const event of ['timeupdate','seeked','playing','ended'])audio.addEventListener(event,paint);
 return {
  get track(){return track;},get state(){return state;},get currentTime(){return audio.currentTime||0;},
  async play(next,{muted=false,offset=0,playbackRate=rate}={}){
   const id=++request;audio.pause();track=next;onCaption('',next.language);audio.src=next.file;audio.muted=muted;rate=playbackRate;audio.playbackRate=rate;setState('loading');
   const seek=()=>{if(id===request&&offset>0)audio.currentTime=Math.min(offset,Math.max(0,next.duration-.05));};
   if(audio.readyState>=1)seek();else audio.addEventListener('loadedmetadata',seek,{once:true});
   try{await audio.play();if(id!==request)return;setState(muted?'muted':'playing');paint();}
   catch(error){
    if(id!==request)return;
    audio.pause();setState(error.name==='NotAllowedError'?'blocked':'error');
   }
  },
  async setMuted(muted){
   if(!track)return;const id=++request;audio.muted=muted;setState('loading');
   try{await audio.play();if(id===request)setState(muted?'muted':'playing');}
   catch(error){if(id===request)setState(error.name==='NotAllowedError'?'blocked':'error');}
  },
  setRate(value){rate=value;audio.playbackRate=value;},
  stop(){request++;audio.pause();track=null;setState('idle');onCaption('');},
  paint
 };
}
