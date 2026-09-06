import * as THREE from './vendor/three.module.js';

// All plaques share one wall datum, independent of image aspect ratio/loading.
export const WALL_PLAQUE=Object.freeze({width:1.55,height:.46,centerY:1.16});
export function makeWallPlaque(group,texture){
 const {width,height,centerY}=WALL_PLAQUE;
 const body=new THREE.Mesh(new THREE.BoxGeometry(width,height,.018),new THREE.MeshStandardMaterial({color:'#89979e',metalness:.85,roughness:.34}));
 body.name='Satin titanium plaque';body.position.set(0,centerY,.015);group.add(body);
 // The diffuse lettering stays readable even when the metallic edge reflects light.
 const face=new THREE.Mesh(new THREE.PlaneGeometry(width-.018,height-.018),new THREE.MeshBasicMaterial({map:texture,toneMapped:false}));
 face.position.set(0,centerY,.025);group.add(face);return face;
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
const railMaterial=new THREE.MeshStandardMaterial({color:'#a7b1b3',metalness:.55,roughness:.5});
export function makeWallFrame(group,width=1.9,height=1.7){
 const frame=new THREE.Group();frame.name='Thin original-art frame';group.add(frame);
 const border=.018;
 for(const [w,h,x,y] of [[width+2*border,border,0,(height+border)/2],[width+2*border,border,0,-(height+border)/2],[border,height,-(width+border)/2,0],[border,height,(width+border)/2,0]]){
  const edge=new THREE.Mesh(new THREE.BoxGeometry(w,h,.016),railMaterial);edge.position.set(x,y,-.002);frame.add(edge);
 }
 return {frame,dispose(){frame.removeFromParent();for(const edge of frame.children)edge.geometry.dispose();}};
}
