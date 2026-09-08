import assert from 'node:assert/strict';
import fs from 'node:fs';
import {wrapPanelText,createDocumentPanel} from '../dist/document-panel.js';
const exhibits=JSON.parse(fs.readFileSync(new URL('../dist/data/curation.json',import.meta.url))).items.filter(e=>e.id.startsWith('canon-')||e.id==='authority-boundary');
let drawn=[];
globalThis.document={createElement(){let font='';const ctx={get font(){return font},set font(f){font=f},fillRect(){},strokeRect(){},beginPath(){},moveTo(){},lineTo(){},stroke(){},measureText(t){const size=Number(font.match(/(\d+)px/)[1]);return {width:[...t].reduce((n,c)=>n+(/[\u4e00-\u9fff]/.test(c)?size:size*.56),0)}},fillText(t,x,y){assert.ok(x>=46&&x<2006&&y>=46&&y<1490);drawn.push(t)}};return {getContext:()=>ctx,width:0,height:0};}};
for(const e of exhibits)for(const lang of ['en','zh']){drawn=[];const texture=createDocumentPanel(e,lang);assert.equal(texture.image.width,2048);const complete=['canon-1','canon-2'].includes(e.id);assert.ok(drawn.at(-1).includes(lang==='zh'?(e.id==='authority-boundary'?'不是第四条正本':complete?'铭文全文':'阅读导引'):(e.id==='authority-boundary'?'NOT A FOURTH':complete?'COMPLETE INSCRIPTION':'READING GUIDE')));if(complete){assert.equal(drawn.slice(2,-1).join('').replace(/\s/g,''),e.originalText.replace(/\s/g,''),'Every original character must be displayed');}texture.dispose();}
assert.deepEqual(wrapPanelText('one two three',t=>t.length,7),['one two','three']);
console.log('PASS: all eight bilingual document panel layouts preserve source boundaries and readable headings.');
