// Consume only rendered frame time. Hidden time, slow frames and modal pauses never accumulate a catch-up jump.
export function advanceWalk(distance,length,elapsed,speed=1.25){
 const seconds=Number.isFinite(elapsed)?Math.min(.1,Math.max(0,elapsed)):0;
 return Math.min(length,Math.max(0,distance)+speed*seconds);
}
