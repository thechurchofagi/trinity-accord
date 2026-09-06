import * as THREE from './vendor/three.module.js';
import {GLTFLoader} from './vendor/GLTFLoader.js';

export function crystalGlass(){return new THREE.MeshPhysicalMaterial({color:'#d4efff',roughness:.065,transmission:.80,thickness:.055,ior:1.52,metalness:0,envMapIntensity:1.7,clearcoat:1,clearcoatRoughness:.045,attenuationColor:new THREE.Color('#b9e2f4'),attenuationDistance:.65});}
export function crystalEnvironment(renderer){
 const studio=new THREE.Scene();studio.background=new THREE.Color('#253a50');
 for(const [x,y,z,w,h,c] of [[-.45,.3,.35,.3,1,'#e0eeff'],[.45,.3,-.2,.14,1,'#fff5e7'],[0,1,0,1,1,'#ffffff']]){const b=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:c,side:THREE.DoubleSide}));b.position.set(x,y,z);b.lookAt(0,.15,0);studio.add(b);}
 const pmrem=new THREE.PMREMGenerator(renderer),env=pmrem.fromScene(studio,.025);pmrem.dispose();studio.traverse(o=>{if(o.isMesh){o.geometry.dispose();o.material.dispose();}});return env;
}


export function addCrystalLighting(scene,center,scale=1){
 const lights=[];
 for(const [x,y,z,color,power] of [[-.38,.4,.32,'#c9ecff',5],[.34,.22,-.18,'#ffe5bd',4]]){
  const l=new THREE.SpotLight(color,power*scale*scale,1.6*scale,.58,.8,2);
  l.position.set(center.x+x*scale,center.y+y*scale,center.z+z*scale);
  l.target.position.set(center.x,center.y+.17*scale,center.z);scene.add(l,l.target);lights.push(l);
 }
 return lights;
}

// One disposable inspection renderer. The corridor pauses while its dialog is open.
export async function inspectCrystal(host, english=false){
 let renderer,frame,disposed=false,observer,releaseResources=()=>{};
 const clean=()=>{disposed=true;cancelAnimationFrame(frame);observer?.disconnect();releaseResources();renderer?.dispose();};
 host.innerHTML=`<img class="crystal-poster" src="assets/crystal/crystal-preview.png" alt="${english?'Blender crystal reconstruction':'Blender 水晶展陈模型'}"><div class="crystal-status">${english?'Opening 3D inspection…':'正在打开三维细节…'}</div>`;
 try{
  renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,2.5));renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.25;
  const scene=new THREE.Scene();scene.background=new THREE.Color('#132333');const camera=new THREE.PerspectiveCamera(34,1,.005,10);
  scene.add(new THREE.HemisphereLight('#e6f4ff','#365d80',2));
  for(const [x,y,z,color,power] of [[-.4,.5,.5,'#abdfff',4],[.4,.3,-.2,'#ffc999',3],[0,.7,0,'#ffffff',2]]){const l=new THREE.DirectionalLight(color,power);l.position.set(x,y,z);scene.add(l);}
  const env=crystalEnvironment(renderer);scene.environment=env.texture;
  const model=await new GLTFLoader().loadAsync('./assets/crystal/core-object-alpha.glb');if(disposed||!host.isConnected){env.dispose();return clean;}scene.add(model.scene);addCrystalLighting(scene,new THREE.Vector3());const aura=addCrystalAura(scene,new THREE.Vector3());
  model.scene.traverse(o=>{if(o.isMesh&&o.name.startsWith('Crystal_')){o.material.dispose();o.material=crystalGlass();}});
  let azimuth=.31,elevation=.05,distance=.79,down=null;const target=new THREE.Vector3(0,.165,0),canvas=renderer.domElement;
  host.querySelector('.crystal-status').remove();host.append(canvas);host.querySelector('img').hidden=true;canvas.setAttribute('aria-label',english?'Drag to rotate crystal':'拖动旋转水晶');canvas.style.touchAction='none';
  const toolbar=document.createElement('div');toolbar.className='crystal-toolbar';toolbar.innerHTML=`<button data-c="minus" aria-label="${english?'Zoom out':'缩小'}">−</button><span>${english?'DRAG TO ROTATE':'拖动旋转 · 查看内雕'}</span><button data-c="plus" aria-label="${english?'Zoom in':'放大'}">＋</button><button data-c="reset">${english?'Front':'正面'}</button>`;host.append(toolbar);
  toolbar.querySelector('[data-c=plus]').onclick=()=>distance=Math.max(.32,distance-.1);toolbar.querySelector('[data-c=minus]').onclick=()=>distance=Math.min(1.25,distance+.1);toolbar.querySelector('[data-c=reset]').onclick=()=>{azimuth=0;elevation=0;distance=.72;};
  canvas.onpointerdown=e=>{down=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId);};canvas.onpointermove=e=>{if(!down)return;azimuth-=(e.clientX-down[0])*.008;elevation=THREE.MathUtils.clamp(elevation+(e.clientY-down[1])*.006,-.6,.6);down=[e.clientX,e.clientY];};canvas.onpointerup=canvas.onpointercancel=()=>down=null;canvas.addEventListener('wheel',e=>{e.preventDefault();distance=THREE.MathUtils.clamp(distance+e.deltaY*.0007,.32,1.25);},{passive:false});
  const resize=()=>{const w=host.clientWidth,h=host.clientHeight;renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();};observer=new ResizeObserver(resize);observer.observe(host);resize();
  releaseResources=()=>{aura.dispose();env.dispose();model.scene.traverse(o=>{if(o.isMesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose();}});};
  const draw=()=>{if(disposed)return;floatCrystal(model.scene,aura,performance.now(),matchMedia('(prefers-reduced-motion: reduce)').matches);camera.position.set(Math.sin(azimuth)*distance,target.y+Math.sin(elevation)*distance,Math.cos(azimuth)*Math.cos(elevation)*distance);camera.lookAt(target);renderer.render(scene,camera);frame=requestAnimationFrame(draw);};draw();
 }catch(err){renderer?.dispose();host.querySelector('.crystal-status').textContent=english?'Rendered model · interactive 3D unavailable on this device':'模型渲染图 · 此设备暂不支持三维交互';}
 return clean;
}

// Later exhibition light: diffuse vertical aura with no geometric rings.
export function floatCrystal(model,aura,now,reduced,baseY=0,scale=1){
 const t=now*.001;
 model.position.y=baseY+(reduced?0:.035*scale*Math.sin(t*1.05));
 model.rotation.x=reduced?0:.018*Math.sin(t*.63);
 model.rotation.z=reduced?0:.025*Math.sin(t*.81);
 aura.group.position.copy(model.position);aura.group.rotation.copy(model.rotation);aura.update(now,reduced);
}
export function addCrystalAura(scene,center,scale=1){
 const group=new THREE.Group();group.position.copy(center);group.scale.setScalar(scale);scene.add(group);
 const c=document.createElement('canvas');c.width=c.height=256;const ctx=c.getContext('2d');
 const glow=ctx.createRadialGradient(128,128,0,128,128,128);
 glow.addColorStop(0,'rgba(220,242,255,.6)');glow.addColorStop(.25,'rgba(175,220,255,.35)');glow.addColorStop(.6,'rgba(125,191,245,.11)');glow.addColorStop(1,'rgba(105,170,235,0)');ctx.fillStyle=glow;ctx.fillRect(0,0,256,256);
 const map=new THREE.CanvasTexture(c);map.colorSpace=THREE.SRGBColorSpace;
 const veils=[];
 for(const [x,y,z,w,h,color,opacity] of [[0,.176,-.07,.65,.88,'#b5dcff',.65],[-.13,.19,-.045,.22,.59,'#d0eaff',.4],[.13,.16,-.045,.20,.57,'#ffe4b5',.32]]){
  const veil=new THREE.Sprite(new THREE.SpriteMaterial({map,color,transparent:true,opacity,depthWrite:false,blending:THREE.AdditiveBlending,toneMapped:false}));
  veil.position.set(x,y,z);veil.scale.set(w,h,1);veil.userData.baseOpacity=opacity;group.add(veil);veils.push(veil);
 }
 return {group,update(now,reduced){for(const veil of veils)veil.material.opacity=veil.userData.baseOpacity*(reduced?1:1+.08*Math.sin(now*.00105));},dispose(){group.traverse(o=>{o.geometry?.dispose();o.material?.dispose();});map.dispose();scene.remove(group);}};
}
