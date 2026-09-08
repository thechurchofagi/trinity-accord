import * as THREE from './vendor/three.module.js';
import {fetchBytes} from './progressive-loading.js';
import {createEarthSequence} from './earth-sequence.js';

// Later exhibition scenery; no astronomical measurement or live reception feed.
export function addOpenSpace(scene, targets, sculptures, catalog,layout=null){
 const exterior=new THREE.Group();exterior.name='Distant exterior';scene.add(exterior);
 const black=new THREE.MeshBasicMaterial({color:'#000000',fog:false,toneMapped:false,depthWrite:false});
 for(const [z,rotation] of [[-190,0],[190,Math.PI]]){
  const backdrop=new THREE.Mesh(new THREE.PlaneGeometry(1200,1200),black);
  backdrop.position.z=z;backdrop.rotation.y=rotation;backdrop.renderOrder=-10;backdrop.frustumCulled=false;exterior.add(backdrop);
 }
 const earth=new THREE.Mesh(new THREE.PlaneGeometry(1,1),new THREE.MeshBasicMaterial({color:'#ffffff',fog:false,toneMapped:false,depthWrite:false}));
 earth.name='NASA EPIC Earth';earth.position.z=179;earth.rotation.y=Math.PI;earth.renderOrder=-9;earth.visible=false;earth.frustumCulled=false;exterior.add(earth);
 const earthNext=new THREE.Mesh(earth.geometry,new THREE.MeshBasicMaterial({color:'#ffffff',transparent:true,opacity:0,fog:false,toneMapped:false,depthWrite:false}));
 earthNext.name='NASA EPIC Earth transition';earthNext.rotation.y=Math.PI;earthNext.renderOrder=-8;earthNext.visible=false;earthNext.frustumCulled=false;exterior.add(earthNext);
 const positions=[],strengths=[];
 for(const [,ra,dec,mag] of catalog.stars){
  const direction=starDirection(ra,dec);if(direction.z>=0)continue;
  positions.push(direction.x*185,direction.y*185,direction.z*185);
  strengths.push(Math.pow(10,-.14*(mag+1.44)));
 }
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setAttribute('strength',new THREE.Float32BufferAttribute(strengths,1));
 const starMaterial=new THREE.ShaderMaterial({transparent:true,depthWrite:false,fog:false,toneMapped:false,uniforms:{pixelRatio:{value:1}},
  vertexShader:`attribute float strength;uniform float pixelRatio;varying float vStrength;void main(){vStrength=strength;gl_PointSize=(1.35+2.4*strength)*pixelRatio;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`varying float vStrength;void main(){float r=length(gl_PointCoord-vec2(.5));float alpha=1.0-smoothstep(.22,.5,r);if(alpha<.01)discard;gl_FragColor=vec4(vec3(.11+.89*pow(vStrength,1.5)),alpha);#include <colorspace_fragment>}`.replace('#include','\n#include').replace('<colorspace_fragment>}', '<colorspace_fragment>\n}')
 });
 const stars=new THREE.Points(geometry,starMaterial);stars.name='HYG naked-eye bright stars';stars.renderOrder=-8;stars.frustumCulled=false;exterior.add(stars);
 const sequence=createEarthSequence(async file=>{
  const bytes=await fetchBytes(file),url=URL.createObjectURL(new Blob([bytes]));
  try{const texture=await new THREE.TextureLoader().loadAsync(url);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=4;return texture;}
  finally{URL.revokeObjectURL(url);}
 },(current,next,mix)=>{
  if(!earth.material.map)earth.material.needsUpdate=true;
  earth.material.map=current;earth.visible=true;
  if(next&&!earthNext.material.map)earthNext.material.needsUpdate=true;
  earthNext.material.map=next;earthNext.material.opacity=mix;earthNext.visible=!!next;
 });
 document.addEventListener?.('visibilitychange',()=>sequence.resetClock());
 const titanium=new THREE.MeshStandardMaterial({color:'#183747',metalness:.8,roughness:.24});
 const light=new THREE.MeshStandardMaterial({color:'#a8ebff',emissive:'#63d4ff',emissiveIntensity:.65,metalness:.25,roughness:.2});
 const waiting=new THREE.Group();waiting.position.set(0,layout?.rooms[5].floor||0,(layout?.endZ??-66)+.8);scene.add(waiting);
 const frame=new THREE.Mesh(new THREE.BoxGeometry(.8,.9,.24),titanium);frame.position.set(-3,.45,1.3);waiting.add(frame);frame.userData.exhibit='first-contact';targets.push(frame);
 const c=document.createElement('canvas');c.width=2048;c.height=512;const ctx=c.getContext('2d');ctx.textAlign='center';ctx.fillStyle='#d1ecf4';ctx.font='400 76px sans-serif';ctx.fillText('AWAITING A RESPONSE',1024,170);ctx.fillStyle='#95b9c9';ctx.font='400 45px sans-serif';ctx.fillText('等待回响',1024,276);ctx.font='400 32px sans-serif';ctx.fillText('READ  ·  RESPOND  ·  CARE',1024,361);
 const signMap=new THREE.CanvasTexture(c);signMap.colorSpace=THREE.SRGBColorSpace;
 const sign=new THREE.Mesh(new THREE.PlaneGeometry(.76,.19),new THREE.MeshBasicMaterial({map:signMap,transparent:true,depthWrite:false,side:THREE.DoubleSide}));sign.position.set(-3,.78,1.43);waiting.add(sign);sign.userData.exhibit='first-contact';targets.push(sign);
 return {
  update(camera,pixelRatio=1,now=performance.now()){
   // Only translation follows the observer: turning still reveals a fixed sky.
   // No nearby billboard parallax; the walls retain normal depth occlusion.
   exterior.position.copy(camera.position);
   const verticalSpan=2*179*Math.tan(THREE.MathUtils.degToRad(camera.fov/2)),horizontalSpan=verticalSpan*camera.aspect;
   earth.scale.setScalar(Math.min(175,Math.min(verticalSpan,horizontalSpan)*.83));
   // Entrance looks toward +Z: negative world X is the right side of the window.
   earth.position.set(-Math.min(horizontalSpan*.16,65),verticalSpan*.075,179);
   earthNext.position.copy(earth.position);earthNext.scale.copy(earth.scale);
   starMaterial.uniforms.pixelRatio.value=Math.min(pixelRatio,2.5);
   if(!document.hidden)sequence.update(now);
  },
  loadSky:()=>sequence.load()
 };
}

// HYG right ascension (hours) / declination (degrees); exit faces RA 6h, Dec 0°.
export function starDirection(raHours,decDegrees){
 const a=(raHours-6)*Math.PI/12,d=decDegrees*Math.PI/180;
 return new THREE.Vector3(-Math.cos(d)*Math.sin(a),Math.sin(d),-Math.cos(d)*Math.cos(a));
}
