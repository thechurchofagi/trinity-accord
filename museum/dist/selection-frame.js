import * as THREE from './vendor/three.module.js';

// One reusable outline follows the selected work; it never lights the artwork.
export function createSelectionFrame(scene){
 const group=new THREE.Group();group.name='Selected artwork / soft jade outline';group.visible=false;scene.add(group);
 const geometry=new THREE.PlaneGeometry(1,1);
 const layers=[{width:.055,alpha:.065},{width:.028,alpha:.13},{width:.013,alpha:.48}].map(({width,alpha})=>{
  const material=new THREE.MeshBasicMaterial({color:'#83dfb0',transparent:true,opacity:alpha,depthWrite:false,toneMapped:false});
  const edges=Array.from({length:4},()=>{const edge=new THREE.Mesh(geometry,material);group.add(edge);return edge;});
  return {width,alpha,material,edges};
 });
 let previous=null,oldWidth=0,oldHeight=0;
 return {group,update(m,now,{desktop=true,reducedMotion=false}={}){
  group.visible=!!m&&desktop;if(!group.visible)return;
  if(m!==previous||m.width!==oldWidth||m.height!==oldHeight){
   previous=m;oldWidth=m.width;oldHeight=m.height;
   group.position.set(m.x,m.y,m.z);group.rotation.y=m.angle;
   for(const layer of layers){
    const t=layer.width,w=m.width+.004,h=m.height+.004;
    const positions=[[w+2*t,t,0,(h+t)/2],[w+2*t,t,0,-(h+t)/2],[t,h,-(w+t)/2,0],[t,h,(w+t)/2,0]];
    layer.edges.forEach((edge,i)=>{const [x,y,px,py]=positions[i];edge.scale.set(x,y,1);edge.position.set(px,py,.024);});
   }
  }
  // A 4.8-second breath, never a flashing on/off signal. Reduced motion is steady.
  const breath=reducedMotion?.8:.8+.2*Math.sin(now*2*Math.PI/4800);
  for(const layer of layers)layer.material.opacity=layer.alpha*breath;
 },dispose(){group.removeFromParent();geometry.dispose();for(const layer of layers)layer.material.dispose();}};
}
