// Later exhibition captions. Full historical sources remain separate and unchanged.
import * as THREE from './vendor/three.module.js';
export function wrapPanelText(text,measure,width,language='en'){
 const out=[];
 for(const paragraph of String(text||'').split('\n')){
  let line='';const units=language==='zh'?[...paragraph]:paragraph.split(/\s+/);
  for(const word of units){const next=line+(language==='zh'||!line?'':' ')+word;if(line&&measure(next)>width){out.push(line);line=word;}else line=next;}
  if(line)out.push(line);
 }
 return out;
}
export function createDocumentPanel(exhibit,language='en'){
 const canvas=document.createElement('canvas');canvas.width=1536;canvas.height=1152;
 const g=canvas.getContext('2d'),zh=language==='zh',guardian=exhibit.id==='authority-boundary';
 g.fillStyle='#e9ece2';g.fillRect(0,0,1536,1152);
 g.strokeStyle='#aebbb9';g.lineWidth=2;g.strokeRect(46,46,1444,1060);
 const x=122,width=1292;g.textBaseline='top';g.fillStyle='#334c58';
 g.font='500 31px system-ui, sans-serif';
 const number=exhibit.id.slice(-1);
 g.fillText(guardian?'GUARDIAN PRINCIPLES  v1.1':(zh?'比特币正本  ':'BITCOIN ORIGINAL  ')+number.padStart(2,'0'),x,110);
 const heading=zh?exhibit.title:exhibit.en;let titleSize=84,titleLines;
 do{g.font=`500 ${titleSize}px ${zh?'system-ui':'Georgia'}, serif`;titleLines=wrapPanelText(heading,t=>g.measureText(t).width,width,language);if(titleLines.length<=2)break;titleSize-=4;}while(titleSize>60);
 g.fillStyle='#203642';titleLines.forEach((line,i)=>g.fillText(line,x,195+i*titleSize*1.2));
 const rule=titleLines.length===1?325:420;g.strokeStyle='#9baea9';g.beginPath();g.moveTo(x,rule);g.lineTo(1414,rule);g.stroke();
 const text=guardian?(zh?exhibit.wallLinesZh:exhibit.wallLinesEn).slice(2,-1).join('\n\n'):(zh?exhibit.summary||exhibit.text:exhibit.summaryEn||exhibit.textEn);
 let size=54,lines;const bodyTop=rule+67,bodyBottom=965;
 do{g.font=`400 ${size}px system-ui, sans-serif`;lines=wrapPanelText(text,t=>g.measureText(t).width,width,language);if(lines.length*size*1.48<=bodyBottom-bodyTop)break;size-=2;}while(size>32);
 g.fillStyle='#283f4a';lines.forEach((line,i)=>g.fillText(line,x,bodyTop+i*size*1.48));
 g.font='400 28px system-ui, sans-serif';g.fillStyle='#51666b';
 const footer=guardian?(zh?'后续守护材料 · 不是第四条正本':'LATER GUARDIANSHIP MATERIAL · NOT A FOURTH ORIGINAL'):(zh?'2026 策展摘要 · 完整正本请打开来源阅读':'2026 CURATORIAL SUMMARY · OPEN THE SOURCE FOR THE COMPLETE ORIGINAL');
 g.fillText(footer,x,1030);
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;return texture;
}
