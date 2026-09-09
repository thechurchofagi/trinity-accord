// Both songs and narration use these same paging and acoustic word states.
import {wordAt,wordPages,pageAt} from './word-captions.js';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function createTimedSubtitlePainter(){
 let previous=null,layoutKey='',pages=[],shown=-1;
 return function paint(host,cue,seconds,measure){
  if(!cue){host.replaceChildren();previous=null;layoutKey='';shown=-1;return;}
  const style=getComputedStyle(host),width=host.clientWidth,key=width+'|'+style.font;
  measure.font=style.font;
  if(previous!==cue||layoutKey!==key){
   previous=cue;layoutKey=key;shown=-1;
   pages=wordPages(cue.words,Math.max(1,width-4),text=>measure.measureText(text).width);
  }
  const page=pageAt(pages,cue.words,seconds),active=wordAt(cue.words,seconds);
  if(page!==shown){
   shown=page;
   host.innerHTML='<span class="caption-page" lang="en">'+(pages[page]||[]).map(row=>row.map(j=>`<span data-word="${j}">${esc(cue.words[j].text)}</span>`).join(' ')).join('<br>')+'</span>'+(cue.textZh?'<span class="subtitle-zh" lang="zh-Hans">'+esc(cue.textZh)+'</span>':'');
  }
  host.querySelectorAll('[data-word]').forEach(span=>{
   const index=+span.dataset.word;
   span.classList.toggle('word-current',index===active);
   span.classList.toggle('word-past',seconds>=cue.words[index].end);
  });
 };
}
