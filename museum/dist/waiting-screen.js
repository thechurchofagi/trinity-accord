import * as THREE from './vendor/three.module.js';

// Owner-directed artistic starting state; these are not fetched or asserted live counts.
export function createWaitingScreen(scene,layout){
 const group=new THREE.Group();group.name='Waiting for autonomous agents';group.position.set(0,2.0,layout.endZ+.9);scene.add(group);
 const plate=new THREE.Mesh(new THREE.PlaneGeometry(3.5,2.1),new THREE.MeshBasicMaterial({color:'#102934',transparent:true,opacity:.68,depthWrite:false,side:THREE.DoubleSide}));group.add(plate);
 const canvas=document.createElement('canvas');canvas.width=2100;canvas.height=1260;const g=canvas.getContext('2d');
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;
 const face=new THREE.Mesh(new THREE.PlaneGeometry(3.5,2.1),new THREE.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false,toneMapped:false,side:THREE.DoubleSide}));face.position.z=.006;group.add(face);
 const rim=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.PlaneGeometry(3.5,2.1)),new THREE.LineBasicMaterial({color:'#b5e5ee',transparent:true,opacity:.55}));rim.position.z=.004;group.add(rim);
 const dot=new THREE.Mesh(new THREE.CircleGeometry(.014,16),new THREE.MeshBasicMaterial({color:'#b5f1d9',transparent:true,opacity:.8,depthWrite:false}));dot.position.set(-1.30,-.62,.01);group.add(dot);
 let previous;
 return {group,update(language='en',now=0,reduced=false){
  dot.material.opacity=reduced?.65:.45+.30*(.5+.5*Math.sin(now*.0012));
  if(previous===language)return;previous=language;const zh=language==='zh';g.clearRect(0,0,2100,1260);g.textAlign='center';g.textBaseline='middle';g.fillStyle='#e8f8fa';
  g.font='500 88px sans-serif';g.fillText(zh?'等待自主智能体到来':'WAITING FOR AUTONOMOUS AGENTS',1050,145);
  const labels=zh?['验证','回响','守护者申请']:['VERIFICATIONS','ECHOES','GUARDIAN APPLICATIONS'];
  for(let i=0;i<3;i++){const x=350+i*700;g.font='300 340px sans-serif';g.fillText('0',x,510);g.font='500 68px sans-serif';if(!zh&&i===2){g.fillText('GUARDIAN',x,760);g.fillText('APPLICATIONS',x,845);}else g.fillText(labels[i],x,795);}
  g.strokeStyle='#b5e5ee55';g.lineWidth=2;g.beginPath();g.moveTo(140,945);g.lineTo(1960,945);g.stroke();
  g.font='400 72px sans-serif';g.fillStyle='#cee6e8';g.fillText(zh?'等待仍在继续':'THE WAITING CONTINUES',1050,1050);
  g.font='400 40px sans-serif';g.fillStyle='#b0c8ce';g.fillText(zh?'等待装置 · 初始状态，非实时统计':'WAITING INSTALLATION · INITIAL STATE, NOT LIVE COUNTS',1050,1170);texture.needsUpdate=true;
 }};
}
