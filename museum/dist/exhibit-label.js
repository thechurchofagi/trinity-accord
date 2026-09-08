// Four separate fields: record number, historical event, mint record, actual music.
export function exhibitLabel(e,zh=false,music=false){
 if(e?.ordinal){
  const track=music&&typeof music==='object'?music:null;
  const song=track?.songTitle||e.songTitle||track?.title||(zh?'配乐':'Music');
  return [
   `No. ${String(e.ordinal).padStart(3,'0')}`,
   `${zh?'事件':'Event'} ${e.eventDate||(zh?'日期未载':'Date unstated')} · ${zh?(e.eventTitleZh||'记录未注明独立事件'):(e.eventTitleEn||'No separate event specified')}`,
   `${zh?'铸造':'Mint'} ${e.date?.slice(0,10)||'—'} UTC · ${zh?(e.mintThemeZh||e.mintTitle||e.title||''):(e.mintThemeEn||e.mintTitle||e.title||'')}`,
   music?`♪ ${song}`:(zh?'— 无配乐':'— No music')
  ].join('\n');
 }
 if(e?.inscription)return `${zh?'铭文':'Inscr.'} ${e.number}\n${e.date?.slice(0,10)||'—'} UTC`;
 if(e?.id==='physical-alpha')return zh?'核心物件 Alpha':'Core Object Alpha';
 return (zh?e?.title:e?.en)|| (zh?'展览说明':'Exhibition note');
}
