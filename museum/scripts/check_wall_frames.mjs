import fs from 'node:fs';
import * as T from '../dist/vendor/three.module.js';
import {removeLegacyWallMounts,removeLegacyChapterPosts,clearBakedWallShadows,makeWallFrame,makeWallPlaque,WALL_PLAQUE} from '../dist/wall-presentation.js';
const b=fs.readFileSync(new URL('../dist/assets/gallery/memory-gallery.glb',import.meta.url));const len=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+len)),bin=b.subarray(28+len);const root=new T.Group();
function attr(id){const a=j.accessors[id],v=j.bufferViews[a.bufferView],C={5126:Float32Array,5123:Uint16Array,5125:Uint32Array}[a.componentType],n={SCALAR:1,VEC3:3,VEC2:2}[a.type];const raw=bin.subarray((v.byteOffset||0)+(a.byteOffset||0),(v.byteOffset||0)+(a.byteOffset||0)+a.count*n*C.BYTES_PER_ELEMENT);return new T.BufferAttribute(new C(raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength)),n);}
for(const n of j.nodes){if(n.mesh===undefined)continue;for(const p of j.meshes[n.mesh].primitives){const g=new T.BufferGeometry();g.setAttribute('position',attr(p.attributes.POSITION));if(p.indices!==undefined)g.setIndex(attr(p.indices));const m=new T.MeshBasicMaterial();m.name=j.materials[p.material].name;const o=new T.Mesh(g,m);if(n.matrix){o.matrix.fromArray(n.matrix);o.matrix.decompose(o.position,o.quaternion,o.scale);}else{if(n.translation)o.position.fromArray(n.translation);if(n.rotation)o.quaternion.fromArray(n.rotation);if(n.scale)o.scale.fromArray(n.scale);}root.add(o);}}
const metal=root.children.find(o=>o.material.name==='Brushed titanium');root.updateMatrixWorld(true);
const cast=(z,y)=>new T.Raycaster(new T.Vector3(0,y,z),new T.Vector3(-1,0,0),0,4.38).intersectObject(metal).length;
const before={floor:cast(-3,.18),ceiling:cast(-2,4.7)};
// A retained chapter post at z=-13.5 runs through the exhibition's display band.
if(!cast(-13.5,2.6))throw Error('Fixture no longer reproduces the black post');
const posts=removeLegacyChapterPosts(root);if(posts.removedPosts!==12)throw Error('Unexpected post count '+JSON.stringify(posts));
if(cast(-13.5,2.6))throw Error('Black post still crosses the display band');
if(cast(-3,.18)!==before.floor||cast(-2,4.7)!==before.ceiling)throw Error('Non-post metal was changed');
if(removeLegacyChapterPosts(root).removedPosts!==0)throw Error('Post cleanup is not idempotent');
console.log('Chapter post cleanup',JSON.stringify(posts));
const result=removeLegacyWallMounts(root);if(result.hiddenMeshes!==2||result.removedTriangles<100)throw Error(JSON.stringify(result));
const clean=clearBakedWallShadows(root);if(clean.cleanTriangles<100)throw Error('Old baked wall silhouettes remain');
const layout=JSON.parse(fs.readFileSync(new URL('../dist/data/gallery-layout.json',import.meta.url)));let frames=0;
for(const room of layout.rooms)for(const e of room.exhibits)for(const y of [1.75,2.6,3.99])for(let i=-8;i<=8;i++){
 const z=e.z+i*.95/8,ray=new T.Raycaster(new T.Vector3(0,y,z),new T.Vector3(Math.sign(e.x),0,0),0,4.38);
 if(ray.intersectObject(metal).length)throw Error('Metal crosses artwork/plaque sightline '+e.id);
}

for(const height of [.4,.9,1.3,1.7]){
 const group=new T.Group();makeWallFrame(group,1.2,height);const face=makeWallPlaque(group,new T.Texture());
 const body=group.children.find(o=>o.name==='Satin titanium plaque');
 if(face.position.x!==0||face.position.y!==WALL_PLAQUE.centerY)throw Error('Plaque alignment changes with image ratio');
 if(body.geometry.parameters.width!==1.55||body.geometry.parameters.height!==.46||body.material.metalness<.8)throw Error('Plaque lacks uniform metal body');
 if(WALL_PLAQUE.centerY-WALL_PLAQUE.height/2<=height/2+.018)throw Error('Plaque overlaps artwork');
}
for(const r of layout.rooms){for(const e of r.exhibits){if(-e.z<=r.start||-e.z>=r.start+r.length)throw Error('Out of room '+e.id);const g=new T.Group();g.position.set(e.x,layout.exhibitCentreHeight,e.z);g.rotation.y=e.angle;const f=makeWallFrame(g,1.2,1.7);g.updateMatrixWorld(true);const normal=new T.Vector3(0,0,1).applyQuaternion(g.quaternion);if(Math.sign(normal.x)!==-Math.sign(e.x))throw Error('Frame faces wall');if(g.children.length!==1||f.frame.children.length!==4)throw Error('Frame must have four thin edges and no backing');const box=new T.Box3().setFromObject(f.frame);if(Math.max(box.max.x-box.min.x,box.max.z-box.min.z)>1.24)throw Error('Frame does not fit image ratio');frames++;}}
if(layout.dimensions.height!==6||layout.exhibitCentreHeight!==2.6||layout.eyeHeight!==1.65)throw Error('Raised display must preserve human eye height');
for(const r of layout.rooms)for(const side of [-1,1]){const mounts=r.exhibits.filter(e=>Math.sign(e.x)===side);for(let i=1;i<mounts.length;i++)if(Math.abs(mounts[i].z-mounts[i-1].z)<2.17)throw Error('Overlapping frames '+r.id);}
console.log(JSON.stringify({...result,...clean,frames,roomBounds:'PASS',inwardNormals:'PASS'}));
