// Two resident textures: the visible observation and the next observation.
export const EARTH_FRAMES=Array.from({length:6},(_,i)=>`./assets/space/earth-${String(i+1).padStart(2,'0')}.jpg`);
export const EARTH_INTERVAL_MS=10000,EARTH_FADE_MS=1500;
export function createEarthSequence(loadTexture,display){
 let current=null,next=null,index=0,loading=null,initial=null,lastTick=null,elapsed=0,fadeStart=null,retryAt=0;
 function preload(){
  if(loading||next||!current)return;
  loading=loadTexture(EARTH_FRAMES[(index+1)%EARTH_FRAMES.length]).then(texture=>{next=texture;}).catch(()=>{retryAt=elapsed+EARTH_INTERVAL_MS;}).finally(()=>{loading=null;});
 }
 return {
  load(){
   if(initial)return initial;
   initial=loadTexture(EARTH_FRAMES[0]).then(texture=>{current=texture;display(current,null,0);preload();return true;}).catch(()=>{initial=null;return false;});
   return initial;
  },
  resetClock(){lastTick=null;},
  update(now){
   if(!current)return;
   if(lastTick===null){lastTick=now;return;}
   elapsed+=Math.max(0,now-lastTick);lastTick=now;
   if(!next&&!loading&&elapsed>=retryAt)preload();
   if(fadeStart===null&&elapsed>=EARTH_INTERVAL_MS&&next)fadeStart=elapsed;
   if(fadeStart!==null){
    const mix=Math.min(1,(elapsed-fadeStart)/EARTH_FADE_MS);
    // Smooth opacity only; never rotate or distort a photographed Earth disk.
    display(current,next,mix*mix*(3-2*mix));
    if(mix===1){
     const old=current;current=next;next=null;index=(index+1)%EARTH_FRAMES.length;
     elapsed-=fadeStart;fadeStart=null;display(current,null,0);old.dispose();preload();
    }
   }
  }
 };
}
