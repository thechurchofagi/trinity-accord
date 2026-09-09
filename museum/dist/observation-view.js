// Frame an exhibit with breathing room, keeping its centre above the mobile dock.
export function observationView(width,height,fov,aspect,mobile=false,viewport=null){
 const tan=Math.tan(fov*Math.PI/360);
 if(viewport){
  const available=Math.max(80,viewport.bottom-viewport.top),fraction=available/viewport.height;
  const distance=Math.max(width/(2*tan*aspect*.90),height/(2*tan*fraction*.94));
  return {distance,aimOffset:0};
 }
 const distance=Math.max(width/(2*tan*aspect*.78),height/(2*tan*(mobile?.52:.62)));
 return {distance,aimOffset:mobile?distance*tan*.16:0};
}
export function galleryCamera(width,height,top,bottom){
 const available=Math.max(80,bottom-top),fraction=available/height;
 const fov=Math.max(width<650?76:66,2*Math.atan(2.34/(2*6.3*fraction*.82))*180/Math.PI);
 return {fov:Math.min(115,fov),offsetY:height/2-(top+bottom)/2};
}

// Fit the real, upward-looking first-person view, including plaque and frame.
// Using a front-on rectangle overestimates the distance at normal eye height.
export function focusedArtworkView(width,height,centerY,eyeY,fov,aspect,viewport){
 const tan=Math.tan(fov*Math.PI/360),halfScreen=viewport.height/2;
 const available=Math.max(80,viewport.bottom-viewport.top),limit=(available/2-6)/halfScreen;
 const fits=d=>{
  const pitch=Math.atan2(centerY-eyeY,d),c=Math.cos(pitch),s=Math.sin(pitch);
  return [-1,1].every(sign=>{
   const y=centerY+sign*height/2-eyeY,depth=d*c+y*s;
   return depth>0&&Math.abs((y*c-d*s)/(depth*tan))<=limit&&width/(2*depth*tan*aspect)<=.94;
  });
 };
 let low=.65,high=12;for(let i=0;i<36;i++){const mid=(low+high)/2;if(fits(mid))high=mid;else low=mid;}
 return {distance:high};
}
