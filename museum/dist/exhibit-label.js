// Historical chain dates only. Never substitute an artwork's creation date.
export function exhibitLabel(e,zh=false,music=false){
 const date=e?.date?.slice(0,10);
 if(e?.ordinal)return `No. ${String(e.ordinal).padStart(2,'0')}${music?' ♪':''}\n${date||'—'}`;
 if(e?.inscription)return `${zh?'铭文':'Inscr.'} ${e.number}\n${date||'—'}`;
 if(e?.id==='physical-alpha')return zh?'核心物件 Alpha · 实物照片':'Core Object Alpha · photograph';
 return zh?'展览说明':'Exhibition note';
}
