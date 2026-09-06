// Frame an exhibit with breathing room, keeping its centre above the mobile dock.
export function observationView(width,height,fov,aspect,mobile=false){
 const tan=Math.tan(fov*Math.PI/360);
 const distance=Math.max(width/(2*tan*aspect*.78),height/(2*tan*(mobile?.52:.62)));
 return {distance,aimOffset:mobile?distance*tan*.16:0};
}
