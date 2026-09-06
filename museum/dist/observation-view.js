// Frame an exhibit with breathing room, keeping its centre above the mobile dock.
export function observationView(width,height,fov,aspect,mobile=false,viewport=null){
 const tan=Math.tan(fov*Math.PI/360);
 if(viewport){
  const available=Math.max(80,viewport.bottom-viewport.top),fraction=available/viewport.height;
  const distance=Math.max(width/(2*tan*aspect*.8),height/(2*tan*fraction*.86));
  return {distance,aimOffset:0};
 }
 const distance=Math.max(width/(2*tan*aspect*.78),height/(2*tan*(mobile?.52:.62)));
 return {distance,aimOffset:mobile?distance*tan*.16:0};
}
export function galleryCamera(width,height,top,bottom){
 const available=Math.max(80,bottom-top),fraction=available/height;
 const fov=Math.max(width<650?76:66,2*Math.atan(2.04/(2*6.3*fraction*.82))*180/Math.PI);
 return {fov:Math.min(115,fov),offsetY:height/2-(top+bottom)/2};
}
