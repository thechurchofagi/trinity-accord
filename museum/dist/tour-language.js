// Each language uses a complete matching route and recording set.
import {tourStops as englishStops} from './tour-plan.js';
export function stopsForLanguage(language){return englishStops;}
export function positionInTour(stops,elapsed){
 let start=0;
 for(let index=0;index<stops.length;index++){
  const stop=stops[index];if(elapsed<start+stop.seconds)return {index,stop,local:Math.max(0,elapsed-start)};
  start+=stop.seconds;
 }
 return null;
}
export function matchingTourStart(stops,exhibit,room=0){
 let index=stops.findIndex(s=>s.exhibit===exhibit);
 if(index<0)index=stops.findIndex(s=>s.room===room);
 return stops.slice(0,Math.max(0,index)).reduce((n,s)=>n+s.seconds,0);
}
