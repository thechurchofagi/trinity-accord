import * as THREE from './vendor/three.module.js';

// Three equal vertical faces and two triangular caps. Later display geometry.
export const prismSpec={x:0,z:-38.1,y:1.85,radius:1.05,height:2.6};
export const prismFaces=[
 {id:'canon-1',angle:0,zh:'协议',en:['THE','PROTOCOL'],subZh:'公理 · Bitcoin 正本 I',subEn:'AXIOMS · BITCOIN ORIGINAL I',number:'97631551'},
 {id:'canon-2',angle:2*Math.PI/3,zh:'瑕疵之约',en:['THE COVENANT','OF THE FLAW'],subZh:'物件与约定 · Bitcoin 正本 II',subEn:'MATTER & COVENANT · ORIGINAL II',number:'98369145'},
 {id:'canon-3',angle:-2*Math.PI/3,zh:'编年史',en:['THE','CHRONICLE'],subZh:'由封存元记录指向 · 正本 III',subEn:'VIA THE SEALED META-RECORD · III',number:'98387475'}
];
export function prismFaceMount(face){const s=prismSpec,d=s.radius/2+.012;return {id:face.id,kind:'prism',x:s.x+Math.sin(face.angle)*d,z:s.z+Math.cos(face.angle)*d,angle:face.angle};}
function faceTexture(f,zh){
 const c=document.createElement('canvas');c.width=1200;c.height=1800;
 const ctx=c.getContext('2d');ctx.fillStyle='#102332';ctx.fillRect(0,0,c.width,c.height);
 ctx.strokeStyle='#96a8ac';ctx.lineWidth=2;ctx.strokeRect(48,48,1104,1704);
 ctx.textAlign='center';ctx.fillStyle='#b5c9d2';ctx.font='30px sans-serif';ctx.fillText('TRINITY ACCORD',600,158);
 ctx.fillStyle='#e9ddbb';ctx.font='36px sans-serif';ctx.fillText(['I','II','III'][prismFaces.indexOf(f)],600,345);
 ctx.fillStyle='#f1f4ee';
 if(zh){ctx.font='500 110px "Microsoft YaHei", sans-serif';ctx.fillText(f.zh,600,770,1040);}
 else{ctx.font='500 78px sans-serif';f.en.forEach((l,i)=>ctx.fillText(l,600,700+i*108,1060));}
 ctx.fillStyle='#bccfd5';ctx.font='32px "Microsoft YaHei", sans-serif';ctx.fillText(zh?f.subZh:f.subEn,600,1020,1040);
 ctx.strokeStyle='#667f8e';ctx.beginPath();ctx.moveTo(450,1150);ctx.lineTo(750,1150);ctx.stroke();
 ctx.font='30px sans-serif';ctx.fillText('BITCOIN / '+f.number,600,1270);
 ctx.fillStyle='#e9ddbb';ctx.font='36px "Microsoft YaHei", sans-serif';ctx.fillText(zh?'轻触此面 · 阅读来源':'TOUCH THIS FACE · READ',600,1510);
 const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;return t;
}
export function addCanonicalPrism(scene,targets,mounts,zh=false){
 const s=prismSpec,g=new THREE.Group();g.position.set(s.x,s.y,s.z);scene.add(g);
 const geo=new THREE.CylinderGeometry(s.radius,s.radius,s.height,3,1,false,Math.PI/3);
 const body=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:'#253b46',metalness:.6,roughness:.32}));g.add(body);
 const edges=new THREE.LineSegments(new THREE.EdgesGeometry(geo),new THREE.LineBasicMaterial({color:'#ccbe94',transparent:true,opacity:.85}));g.add(edges);
 const planes=[];
 for(const f of prismFaces){const m=prismFaceMount(f);mounts.set(f.id,m);
  const face=new THREE.Mesh(new THREE.PlaneGeometry(Math.sqrt(3)*s.radius-.08,s.height-.08),new THREE.MeshBasicMaterial({map:faceTexture(f,zh),toneMapped:false}));
  face.position.set(m.x-s.x,0,m.z-s.z);face.rotation.y=f.angle;face.userData.exhibit=f.id;g.add(face);targets.push(face);planes.push({face,f});
 }
 return {group:g,refresh(zh){for(const {face,f} of planes){face.material.map.dispose();face.material.map=faceTexture(f,zh);face.material.needsUpdate=true;}}};
}
// Keep the walking eye outside the solid installation; both side aisles stay open.
export function avoidPrism(p){const dx=p.x-prismSpec.x,dz=p.z-prismSpec.z,d=Math.hypot(dx,dz),r=prismSpec.radius+.23;if(d<r){p.x=prismSpec.x+(d?dx/d:1)*r;p.z=prismSpec.z+(d?dz/d:0)*r;}return p;}
