// Event and mint dates are independently sourced; never infer the former from the latter.
export function exhibitLabel(e,zh=false,music=false){
 if(e?.ordinal)return [
  `No. ${String(e.ordinal).padStart(2,'0')}`,
  `Event ${e.eventDate||'Date not specified'} · ${e.eventTitleEn||'Historical context'}`,
  `Mint ${e.date?.slice(0,10)||'—'} UTC · ${(e.mintTitle||e.title||'').replace(/^(?:ASI|AGI)Milestones:\s*/,'')}`,
  music?`♪ ${e.songTitle||'Recording'}`:''
 ].join('\n');
 if(e?.inscription)return `${zh?'铭文':'Inscr.'} ${e.number}\n${e.date?.slice(0,10)||'—'} UTC`;
 if(e?.id==='physical-alpha')return zh?'核心物件 Alpha':'Core Object Alpha';
 return zh?'展览说明':'Exhibition note';
}
