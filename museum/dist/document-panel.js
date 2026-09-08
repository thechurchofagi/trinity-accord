// Historical text is typeset verbatim; the frame and typography are exhibition design.
import * as THREE from './vendor/three.module.js';
export function wrapPanelText(text,measure,width,language='en'){
 const out=[];
 for(const paragraph of String(text||'').split('\n')){
  if(!paragraph){out.push('');continue;}
  let line='';const units=paragraph.match(/[\u2e80-\u9fff]|[^\s\u2e80-\u9fff]+|[ \t]+/gu)||[];
  for(const word of units){const next=line+word;if(line&&measure(next)>width){out.push(line.trimEnd());line=word.trimStart();}else line=next;
   if(measure(line)>width){let fragment='';for(const char of line){if(fragment&&measure(fragment+char)>width){out.push(fragment);fragment=char;}else fragment+=char;}line=fragment;}
  }
  out.push(line.trimEnd());
 }
 return out;
}
export function createDocumentPanel(exhibit,language='en'){
 const canvas=document.createElement('canvas');canvas.width=2048;canvas.height=1536;
 const g=canvas.getContext('2d'),zh=language==='zh',guardian=exhibit.id==='authority-boundary';
 const formation=exhibit.id==='proto-protocol';
 const complete=['canon-1','canon-2','proto-protocol'].includes(exhibit.id)&&!!exhibit.originalText;
 // Cool mineral centre, fine titanium inlay, and a warm edge; no paper imitation.
 g.fillStyle='#d8e3e4';g.fillRect(0,0,2048,1536);
 g.fillStyle='#9fafb5';g.fillRect(0,0,20,1536);g.fillRect(2028,0,20,1536);
 g.strokeStyle='#91a7ae';g.lineWidth=2;g.strokeRect(42,42,1964,1452);
 g.fillStyle='#ae9571';g.fillRect(96,90,10,132);g.textBaseline='top';g.fillStyle='#334f5c';
 g.font='500 30px system-ui, sans-serif';
 g.fillText(guardian?'GUARDIAN PRINCIPLES  v1.1':formation?'FORMATION RECORD  /  97534036':(zh?'比特币正本  ':'BITCOIN ORIGINAL  ')+exhibit.id.slice(-1).padStart(2,'0')+'   /   '+exhibit.number,132,92);
 const heading=zh?exhibit.title:exhibit.en;g.font=`500 62px ${zh?'system-ui':'Georgia'}, serif`;
 g.fillStyle='#233d4a';g.fillText(heading,132,155);
 g.strokeStyle='#8fa8af';g.beginPath();g.moveTo(96,267);g.lineTo(1952,267);g.stroke();
 const text=complete?exhibit.originalText:guardian?(zh?exhibit.wallLinesZh:exhibit.wallLinesEn).slice(2,-1).join('\n\n'):
  (zh?exhibit.text:exhibit.textEn)+'\n\n'+(zh?'正本内容：三部分的绑定、编年史的历史与方法、对不完美作品的说明，以及最终签名。点击展板阅读完整原文。':'Inside the original: the binding of the three parts; the Chronicle’s history and method; the imperfect artifact; and the final signature. Select this display to read the complete text.');
 const columns=complete?2:1,gap=70,width=(1856-gap*(columns-1))/columns,top=322,bottom=1365;
 let size=complete?38:62,lines,lineHeight,perColumn;
 do{g.font=`400 ${size}px system-ui, sans-serif`;lines=wrapPanelText(text,t=>g.measureText(t).width,width,language);lineHeight=size*1.32;perColumn=Math.floor((bottom-top)/lineHeight);if(lines.length<=perColumn*columns)break;size-=1;}while(size>22);
 g.fillStyle='#233d48';lines.forEach((line,i)=>{const col=Math.floor(i/perColumn),row=i%perColumn;g.fillText(line,96+col*(width+gap),top+row*lineHeight);});
 if(columns===2){g.strokeStyle='#b3c5c9';g.beginPath();g.moveTo(1024,322);g.lineTo(1024,1365);g.stroke();}
 g.font='400 27px system-ui, sans-serif';g.fillStyle='#48636d';
 const footer=formation?(zh?'2025-06-16 · 协议形成史 · 点击阅读全文':'2025-06-16 · PROTOCOL FORMATION · SELECT FOR FULL TEXT'):guardian?(zh?'后续守护材料 · 不是第四条正本':'LATER GUARDIANSHIP MATERIAL · NOT A FOURTH ORIGINAL'):complete?(zh?'铭文全文 · 保留原语言及历史占位文字':'COMPLETE INSCRIPTION · ORIGINAL LANGUAGE AND HISTORICAL PLACEHOLDERS RETAINED'):(zh?'2026 阅读导引 · 点击展板阅读完整正本':'2026 READING GUIDE · SELECT THE DISPLAY FOR THE COMPLETE ORIGINAL');
 g.fillText(footer,96,1430);
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;return texture;
}
