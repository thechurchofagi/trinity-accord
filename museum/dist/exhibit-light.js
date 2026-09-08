import * as THREE from './vendor/three.module.js';

// One wall-aligned soft light footprint complements the real overhead spotlight.
// It sits behind frames, so it never bleaches or replaces the original artwork.
export function createExhibitWash(scene){
 const canvas=document.createElement('canvas');canvas.width=256;canvas.height=384;
 const ctx=canvas.getContext('2d');ctx.translate(128,192);ctx.scale(1,1.45);
 const glow=ctx.createRadialGradient(0,0,12,0,0,123);
 glow.addColorStop(0,'rgba(255,245,221,.65)');glow.addColorStop(.55,'rgba(255,245,221,.53)');glow.addColorStop(.83,'rgba(255,245,221,.26)');glow.addColorStop(1,'rgba(255,245,221,0)');
 ctx.fillStyle=glow;ctx.fillRect(-128,-150,256,300);
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
 const mesh=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false,toneMapped:false,polygonOffset:true,polygonOffsetFactor:-1}));
 mesh.name='Soft overhead wall wash';mesh.visible=false;scene.add(mesh);
 return {update(m){mesh.visible=!!m;if(!m)return;const top=m.y+m.height/2;mesh.position.set(m.x-Math.sin(m.angle)*.005,top-.05,m.z-Math.cos(m.angle)*.005);mesh.rotation.y=m.angle;mesh.scale.set(m.width+1.65,3.7,1);}};
}
