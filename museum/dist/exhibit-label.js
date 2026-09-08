// Event and mint dates are independently sourced; never infer the former from the latter.
export function exhibitLabel(e,zh=false,music=false){
 if(e?.ordinal)return [
  `No. ${String(e.ordinal).padStart(3,'0')}${music?'  ♪':''}`,
  `${zh?'事件':'Event'} ${e.eventDate||'Date not specified'} · ${zh?(e.eventTitleZh||e.eventTitleEn||'历史背景'):(e.eventTitleEn||'Historical context')}`,
  `${zh?'铸造':'Mint'} ${e.date?.slice(0,10)||'—'} UTC`,
  `${e.mintTitle||e.title||''}`
 ].join('\n');
 if(e?.inscription)return `${zh?'铭文':'Inscr.'} ${e.number}\n${e.date?.slice(0,10)||'—'} UTC`;
 if(e?.id==='physical-alpha')return zh?'核心物件 Alpha':'Core Object Alpha';
 return (zh?e?.title:e?.en)|| (zh?'展览说明':'Exhibition note');
}
