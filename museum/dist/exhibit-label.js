// Historical chain dates only. Never substitute an artwork's creation date.
export function exhibitLabel(e,zh=false){
 const date=e?.date?.slice(0,10);
 if(e?.ordinal)return `${zh?'编号':'Number'} ${String(e.ordinal).padStart(2,'0')}\n${zh?'铸造':'Minted'} ${date||'—'} UTC`;
 if(e?.inscription)return `${zh?'铭文':'Inscription'} ${e.number}\n${zh?'上链':'Inscribed'} ${date||'—'} UTC`;
 if(e?.id==='physical-alpha')return zh?'核心物件 Alpha · 实物照片':'Core Object Alpha · photograph';
 return zh?'展览说明':'Exhibition note';
}
