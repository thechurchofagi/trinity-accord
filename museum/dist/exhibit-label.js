// Historical chain dates only. Never substitute an artwork's creation date.
export function exhibitLabel(e,zh=false){
 const date=e?.date?.slice(0,10);
 if(e?.ordinal)return `NFT #${String(e.ordinal).padStart(3,'0')} · ${zh?'Ethereum 铸造':'Ethereum mint'} ${date||'—'} UTC`;
 if(e?.inscription)return `${zh?'铭文':'Inscription'} #${e.number} · ${zh?'Bitcoin 上链':'Bitcoin inscribed'} ${date||'—'} UTC`;
 return zh?'2026 策展说明':'2026 curatorial display';
}
