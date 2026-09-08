// Chain dates and source titles stay distinct from the recording title.
export function exhibitLabel(e,zh=false,music=false){
 const date=e?.date?.slice(0,10)||'—';
 if(e?.ordinal){
  const event=(zh?e.eventTitleZh:e.eventTitleEn)||e.title?.replace(/^(?:ASI|AGI)Milestones:\s*/,'')||'';
  return [`No. ${String(e.ordinal).padStart(2,'0')}${music?' ♪':''}  ·  ${date}`,
   `${zh?'事件':'Event'}: ${event}`,
   ...(music?[`${zh?'歌曲':'Song'}: ${e.songTitle||event}`]:[])].join('\n');
 }
 if(e?.inscription)return `${zh?'铭文':'Inscr.'} ${e.number}\n${date}`;
 if(e?.id==='physical-alpha')return zh?'核心物件 Alpha · 实物照片':'Core Object Alpha · photograph';
 return zh?'展览说明':'Exhibition note';
}
