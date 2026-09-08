import * as THREE from './vendor/three.module.js';
import {mineralMaterial} from './surface-materials.js';

// Each plaque follows the actual outer frame width, including portrait artworks.
export const WALL_PLAQUE=Object.freeze({width:1.936,height:.72,gap:.085,centerY:1.313});
export function makeWallPlaque(group,texture,width=1.9,height=1.7){
 const plaqueHeight=texture.userData.plaqueHeight||WALL_PLAQUE.height,outer=width+.036,centerY=height/2+.018+WALL_PLAQUE.gap+plaqueHeight/2;
 const body=new THREE.Mesh(new THREE.BoxGeometry(outer,plaqueHeight,.024),mineralMaterial('#adbcc3',{metal:true,roughness:.32}));
 body.name='Satin titanium plaque';body.position.set(0,centerY,.015);group.add(body);
 const face=new THREE.Mesh(new THREE.PlaneGeometry(outer-.018,plaqueHeight-.018),new THREE.MeshBasicMaterial({map:texture,toneMapped:false}));
 face.position.set(0,centerY,.029);group.add(face);face.userData.body=body;
 return face;
}
export function resizeWallPlaque(face,width,height){
 const plaqueHeight=face.material.map?.userData.plaqueHeight||WALL_PLAQUE.height,outer=width+.036,cy=height/2+.018+WALL_PLAQUE.gap+plaqueHeight/2,body=face.userData.body;
 body.geometry.dispose();body.geometry=new THREE.BoxGeometry(outer,plaqueHeight,.024);body.position.y=cy;
 face.geometry.dispose();face.geometry=new THREE.PlaneGeometry(outer-.018,plaqueHeight-.018);face.position.y=cy;
}

// Old baked architecture retained fixed mounts from an earlier exhibition layout.
// Keep its architecture, but replace every obsolete wall mount with one current frame.
export function removeLegacyWallMounts(root){
 root.updateMatrixWorld(true);let hiddenMeshes=0,removedTriangles=0;
 root.traverse(o=>{
  if(!o.isMesh)return;
  const name=o.material?.name;
  if(['Archival mount','Satin aluminium frame'].includes(name)){o.visible=false;hiddenMeshes++;return;}
  if(!['Shadow recess','Porcelain / satin mineral'].includes(name))return;
  const g=o.geometry,p=g.attributes.position,idx=g.index,kept=[],v=new THREE.Vector3();
  const eligible=new Uint8Array(p.count);
  for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);const x=Math.abs(v.x);eligible[i]=x>4.20&&x<4.415&&(name==='Shadow recess'?v.y>.84&&v.y<3.06:v.y>.50&&v.y<.81);}
  const n=idx?idx.count:p.count;
  for(let i=0;i<n;i+=3){const a=idx?idx.getX(i):i,b=idx?idx.getX(i+1):i+1,c=idx?idx.getX(i+2):i+2;if(eligible[a]&&eligible[b]&&eligible[c])removedTriangles++;else kept.push(a,b,c);}
  g.setIndex(kept);g.computeBoundingSphere();
 });return {hiddenMeshes,removedTriangles};
}

// The old chapter door-posts were batched with benches/skirting/ceiling metal.
// Recover connected pieces (welding split face normals) and remove only the
// full-height narrow posts standing in front of the exhibition walls.
export function removeLegacyChapterPosts(root){
 root.updateMatrixWorld(true);let removedPosts=0,removedTriangles=0;
 root.traverse(o=>{
  if(!o.isMesh||o.material?.name!=='Brushed titanium')return;
  const g=o.geometry,p=g.attributes.position,index=g.index,n=index?index.count:p.count;
  const parents=Uint32Array.from({length:p.count},(_,i)=>i),points=[],welded=new Map();
  const find=i=>{while(parents[i]!==i){parents[i]=parents[parents[i]];i=parents[i];}return i;};
  const join=(a,b)=>{parents[find(a)]=find(b);};
  const vertex=i=>index?index.getX(i):i;
  for(let i=0;i<p.count;i++){
   const v=new THREE.Vector3().fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);points.push(v);
   const key=[v.x,v.y,v.z].map(x=>Math.round(x*10000)).join(',');
   if(welded.has(key))join(i,welded.get(key));else welded.set(key,i);
  }
  for(let i=0;i<n;i+=3){join(vertex(i),vertex(i+1));join(vertex(i),vertex(i+2));}
  const boxes=new Map();
  for(let i=0;i<p.count;i++){const id=find(i);if(!boxes.has(id))boxes.set(id,new THREE.Box3());boxes.get(id).expandByPoint(points[i]);}
  const posts=new Set();
  for(const [id,box] of boxes){
   const size=box.getSize(new THREE.Vector3()),centre=box.getCenter(new THREE.Vector3());
   if(Math.abs(centre.x)>4.30&&Math.abs(centre.x)<4.41&&size.x<.12&&size.z<.20&&size.y>3){posts.add(id);removedPosts++;}
  }
  const kept=[];
  for(let i=0;i<n;i+=3){const a=vertex(i),b=vertex(i+1),c=vertex(i+2);if(posts.has(find(a)))removedTriangles++;else kept.push(a,b,c);}
  if(posts.size){g.setIndex(kept);g.computeBoundingSphere();}
 });return {removedPosts,removedTriangles};
}

// The baked wall texture contains silhouettes of the old exhibition. Replace
// only side-wall surfaces with clean plaster; preserve the floor/ceiling bake.
export function clearBakedWallShadows(root){
 root.updateMatrixWorld(true);let cleanTriangles=0;
 const plaster=new THREE.MeshStandardMaterial({name:'Clean exhibition plaster',color:'#e0e1db',roughness:.95});
 root.traverse(o=>{
  if(!o.isMesh||o.material?.name!=='Baked architectural illumination')return;
  const g=o.geometry,p=g.attributes.position,idx=g.index,original=[],walls=[];
  const a=new THREE.Vector3(),b=new THREE.Vector3(),c=new THREE.Vector3(),normal=new THREE.Vector3(),edge=new THREE.Vector3();
  for(let i=0;i<(idx?idx.count:p.count);i+=3){
   const ids=[0,1,2].map(k=>idx?idx.getX(i+k):i+k);
   a.fromBufferAttribute(p,ids[0]).applyMatrix4(o.matrixWorld);b.fromBufferAttribute(p,ids[1]).applyMatrix4(o.matrixWorld);c.fromBufferAttribute(p,ids[2]).applyMatrix4(o.matrixWorld);
   normal.subVectors(b,a).cross(edge.subVectors(c,a)).normalize();
   const x=Math.abs((a.x+b.x+c.x)/3),y=(a.y+b.y+c.y)/3;
   const wall=x>4.36&&x<4.7&&y>.40&&y<4.76&&Math.abs(normal.x)>.9;
   (wall?walls:original).push(...ids);if(wall)cleanTriangles++;
  }
  const baked=o.material;o.material=[baked,plaster];g.setIndex([...original,...walls]);g.clearGroups();g.addGroup(0,original.length,0);g.addGroup(original.length,walls.length,1);
 });return {cleanTriangles};
}
const railMaterial=mineralMaterial('#b8c5cb',{metal:true,roughness:.3});
export function makeWallFrame(group,width=1.9,height=1.7){
 const frame=new THREE.Group();frame.name='Thin original-art frame';group.add(frame);
 const border=.018;
 for(const [w,h,x,y] of [[width+2*border,border,0,(height+border)/2],[width+2*border,border,0,-(height+border)/2],[border,height,-(width+border)/2,0],[border,height,(width+border)/2,0]]){
  const edge=new THREE.Mesh(new THREE.BoxGeometry(w,h,.016),railMaterial);edge.position.set(x,y,-.002);frame.add(edge);
 }
 return {frame,dispose(){frame.removeFromParent();for(const edge of frame.children)edge.geometry.dispose();}};
}
