import * as THREE from './vendor/three.module.js';

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

const railMaterial=new THREE.MeshStandardMaterial({color:'#afc0c5',metalness:.82,roughness:.29});
const mountMaterial=new THREE.MeshStandardMaterial({color:'#e1e3dc',roughness:.9});
const backMaterial=new THREE.MeshStandardMaterial({color:'#14242d',roughness:.7});
export function makeWallFrame(group){
 const backing=new THREE.Mesh(new THREE.BoxGeometry(2.16,2,.055),backMaterial);backing.position.z=-.09;group.add(backing);
 const mat=new THREE.Mesh(new THREE.PlaneGeometry(2.09,1.93),mountMaterial);mat.position.z=-.058;group.add(mat);
 for(const [w,h,x,y] of [[2.17,.034,0,.985],[2.17,.034,0,-.985],[.034,2,-1.068,0],[.034,2,1.068,0]]){
  const edge=new THREE.Mesh(new THREE.BoxGeometry(w,h,.052),railMaterial);edge.position.set(x,y,-.034);group.add(edge);
 }
 return {backing,mat};
}
