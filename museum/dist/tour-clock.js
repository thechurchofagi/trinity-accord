// Display estimates use measured media, never the sequencing budget in tour-plan.js.
export function tourClock(stops,guides,{language='en',rate=1,step=0,guideTime=0,inspectionIndex=-1,inspectionTime=0,musicTime=0,musicStarted=false,inspectionStarted=false,inspectionComplete=false,walkRemaining=0,complete=false}={}){
 const pace=Number.isFinite(rate)&&rate>0?rate:1;
 const lengths=stops.map((s,i)=>(guides.tracks.find(t=>t.stop===i&&t.language===language)?.duration||0)/pace);
 const flaws=[0,1,2].map(i=>(guides.inspectionTracks?.find(t=>t.flaw===i&&t.language===language)?.duration||0)/pace+2.8);
 const cost=(s,i)=>lengths[i]+(s.musicDuration||0)+(s.inspectAt!==undefined?flaws.reduce((a,b)=>a+b,0):0);
 const total=stops.reduce((n,s,i)=>n+cost(s,i),0);
 if(complete)return {total,remaining:0};
 step=Math.max(0,Math.min(stops.length-1,step));const s=stops[step];
 let current=Math.max(0,lengths[step]-Math.max(0,guideTime)/pace,walkRemaining);
 if(musicStarted||inspectionStarted)current=Math.max(0,walkRemaining);
 if(s.musicDuration)current+=Math.max(0,s.musicDuration-(musicStarted?musicTime:0));
 if(s.inspectAt!==undefined&&!inspectionComplete){
  current+=flaws.reduce((n,d,i)=>n+(inspectionStarted&&i<inspectionIndex?0:inspectionStarted&&i===inspectionIndex?Math.max(0,d-2.8-inspectionTime/pace):d),0);
 }
 return {total,remaining:current+stops.slice(step+1).reduce((n,s,j)=>n+cost(s,step+1+j),0)};
}
