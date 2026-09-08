// Shared metre-scale architecture and navigation; all coordinates come from gallery-layout.json.
import * as THREE from './vendor/three.module.js';
const RADIUS=.22;
export function roomAt(layout,z){return layout.rooms.find(r=>-z>=r.start&&-z<=r.start+r.length)||layout.rooms[z>0?0:layout.rooms.length-1];}
export function floorAt(layout,p){
 const ramp=layout.ramp;
 if(ramp&&-p.z>=ramp.start&&-p.z<=ramp.end){
  const t=(-p.z-ramp.start)/(ramp.end-ramp.start);
  return Math.abs(p.x)<=ramp.width/2?ramp.rise*t:ramp.rise*Math.min(3,Math.ceil(t*3))/3;
 }
 return roomAt(layout,p.z).floor||0;
}
function inside(poly,x,z,margin=0){
 // Convex footprints are counter-clockwise in X/depth (-Z).
 const y=-z;
 for(let i=0;i<poly.length;i++){
  const a=poly[i],b=poly[(i+1)%poly.length],dx=b[0]-a[0],dy=b[1]-a[1];
  if(dx*(y-a[1])-dy*(x-a[0])<margin*Math.hypot(dx,dy)-1e-6)return false;
 }
 return true;
}
export function isWalkable(layout,p,margin=RADIUS){
 if(!Number.isFinite(p.x)||!Number.isFinite(p.z)||p.z>-.30||p.z<layout.endZ+.30)return false;
 const r=roomAt(layout,p.z);
 // Portal ends are excluded from polygon shrinkage; side-wall clearance stays enforced.
 if(!inside(r.footprint,p.x,p.z,0))return false;
 for(let i=0;i<r.footprint.length;i++){const a=r.footprint[i],b=r.footprint[(i+1)%r.footprint.length];if(Math.abs(a[1]-b[1])<1e-5&&(Math.abs(a[1]-r.start)<1e-5||Math.abs(a[1]-r.start-r.length)<1e-5))continue;const dx=b[0]-a[0],dy=b[1]-a[1];if(dx*(-p.z-a[1])-dy*(p.x-a[0])<margin*Math.hypot(dx,dy))return false;}
 for(const door of layout.portals)if(!door.visualOnly&&Math.abs(p.z+door.depth)<margin+.16&&Math.abs(p.x-door.x)>door.width/2-margin)return false;
 const crystal=layout.crystal;
 if(crystal&&Math.hypot(p.x-crystal.x,p.z-crystal.z)<(crystal.pedestalRadius||.34)+margin)return false;
 return true;
}
export function constrainStep(layout,start,end){
 const result={x:start.x,z:start.z},steps=Math.max(1,Math.ceil(Math.hypot(end.x-start.x,end.z-start.z)/.09));
 for(let i=0;i<steps;i++){
  const dx=(end.x-start.x)/steps,dz=(end.z-start.z)/steps;
  if(isWalkable(layout,{x:result.x+dx,z:result.z+dz})){result.x+=dx;result.z+=dz;}
  else {if(isWalkable(layout,{x:result.x+dx,z:result.z}))result.x+=dx;if(isWalkable(layout,{x:result.x,z:result.z+dz}))result.z+=dz;}
 }
 return result;
}
function visible(layout,a,b){
 if(!isWalkable(layout,a)||!isWalkable(layout,b))return false;
 const dx=b.x-a.x,dz=b.z-a.z;
 function range(lo,hi){if(Math.abs(dz)<1e-12)return a.z>=lo&&a.z<=hi?[0,1]:null;const t0=(lo-a.z)/dz,t1=(hi-a.z)/dz,l=Math.max(0,Math.min(t0,t1)),h=Math.min(1,Math.max(t0,t1));return l<=h?[l,h]:null;}
 for(const door of layout.portals){if(door.visualOnly)continue;const times=range(-door.depth-RADIUS-.16,-door.depth+RADIUS+.16);if(times&&times.some(t=>Math.abs(a.x+dx*t-door.x)>door.width/2-RADIUS+1e-7))return false;}
 const c=layout.crystal;if(c){const denom=dx*dx+dz*dz,t=denom?Math.max(0,Math.min(1,((c.x-a.x)*dx+(c.z-a.z)*dz)/denom)):0;if(Math.hypot(a.x+dx*t-c.x,a.z+dz*t-c.z)<(c.pedestalRadius||.34)+RADIUS)return false;}
 for(const r of layout.rooms){const times=range(-r.start-r.length,-r.start);if(!times)continue;
  for(const t of times){const x=a.x+dx*t,z=a.z+dz*t;if(!inside(r.footprint,x,z,0))return false;
   for(let i=0;i<r.footprint.length;i++){const p=r.footprint[i],q=r.footprint[(i+1)%r.footprint.length];if(Math.abs(p[1]-q[1])<1e-5&&(Math.abs(p[1]-r.start)<1e-5||Math.abs(p[1]-r.start-r.length)<1e-5))continue;const ex=q[0]-p[0],ey=q[1]-p[1];if(ex*(-z-p[1])-ey*(x-p[0])<RADIUS*Math.hypot(ex,ey)-1e-7)return false;}
  }
 }
 return true;
}
export function routeBetween(layout,start,end){
 start={x:start.x,z:start.z};end={x:end.x,z:end.z};
 if(!isWalkable(layout,start)||!isWalkable(layout,end))return null;
 if(visible(layout,start,end))return [start,end];
 const nodes=[start,end];
 for(const d of layout.portals)for(const side of [-1,1])nodes.push({x:d.x,z:-d.depth+side*.55});
 const c=layout.crystal;if(c)for(const x of [-1.2,1.2])for(const z of [-1.2,1.2])nodes.push({x:c.x+x,z:c.z+z});
 const cost=nodes.map(()=>Infinity),prev=nodes.map(()=>-1),visited=new Set();cost[0]=0;
 for(let i=0;i<nodes.length;i++){
  let best=-1;for(let j=0;j<nodes.length;j++)if(!visited.has(j)&&(best<0||cost[j]<cost[best]))best=j;
  if(best<0||!Number.isFinite(cost[best]))break;if(best===1)break;visited.add(best);
  for(let j=0;j<nodes.length;j++)if(!visited.has(j)&&visible(layout,nodes[best],nodes[j])){const c=cost[best]+Math.hypot(nodes[j].x-nodes[best].x,nodes[j].z-nodes[best].z);if(c<cost[j]){cost[j]=c;prev[j]=best;}}
 }
 if(!Number.isFinite(cost[1]))return null;
 const result=[];for(let i=1;i>=0;i=prev[i])result.unshift(nodes[i]);return result;
}
export function routeLength(route){let n=0;for(let i=1;i<route.length;i++)n+=Math.hypot(route[i].x-route[i-1].x,route[i].z-route[i-1].z);return n;}
export function routePoint(route,t){let left=routeLength(route)*Math.max(0,Math.min(1,t));for(let i=1;i<route.length;i++){const a=route[i-1],b=route[i],length=Math.hypot(b.x-a.x,b.z-a.z);if(left<=length){const f=length?left/length:0;return {x:a.x+(b.x-a.x)*f,z:a.z+(b.z-a.z)*f};}left-=length;}return route.at(-1);}
export function architectureGeometry(part){
 if(part.vertices){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(part.vertices.flat(),3));g.setIndex(part.indices);g.computeVertexNormals();return g;}
 if(part.material==='gold'){
  const [w,h,d]=part.size,b=.018,s=new THREE.Shape();s.moveTo(-w/2+b,-h/2+b);s.lineTo(w/2-b,-h/2+b);s.lineTo(w/2-b,h/2-b);s.lineTo(-w/2+b,h/2-b);s.closePath();
  const g=new THREE.ExtrudeGeometry(s,{depth:d-2*b,bevelEnabled:true,bevelSize:b,bevelThickness:b,bevelSegments:3,steps:1});g.translate(0,0,-d/2+b);return g;
 }
 return new THREE.BoxGeometry(...part.size);
}
export function createSpatialShell(layout,{picking=false}={}){
 const group=new THREE.Group();group.name=picking?'Spatial picking floors':'Six-room immediate architecture';
 const materials=new Map();
 for(const part of layout.architecture){
  if(picking&&!part.floor)continue;
  const key=picking?'pick':part.material;
  if(!materials.has(key)){const def=layout.materials[key];materials.set(key,picking?new THREE.MeshBasicMaterial({visible:false,side:THREE.DoubleSide}):def.emission?new THREE.MeshBasicMaterial({color:def.color,toneMapped:false,transparent:!!def.opacity,opacity:def.opacity??1,depthWrite:!def.opacity}):new THREE.MeshStandardMaterial({name:'Spatial '+key,color:def.color,roughness:def.roughness??.88,metalness:def.metalness??0}));}
  const mesh=new THREE.Mesh(architectureGeometry(part),materials.get(key));mesh.name=part.name;mesh.userData={surface:part.material,passThrough:!!part.passThrough};mesh.position.set(...(part.position||[0,0,0]));mesh.rotation.y=part.rotationY||0;group.add(mesh);
 }
 return {group,dispose(){group.traverse(o=>o.geometry?.dispose());materials.forEach(m=>m.dispose());group.removeFromParent();}};
}
