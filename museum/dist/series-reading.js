// Reading layers are opened explicitly; neither the catalog nor full songs preload.
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const groups=[
 {ids:['eth-042','eth-071','eth-089','eth-122','eth-169'],en:'Recording before the outcome is known',zh:'在结果未知时记录'},
 {ids:['eth-024','eth-041','eth-097','eth-031'],en:'Creating with what unsettles creation',zh:'借助 AI 创作，也质疑创作的位置'},
 {ids:['eth-056','eth-152','eth-133'],en:'A recurring song, a changing working life',zh:'同一首歌与变化的工作生活'},
 {ids:['eth-070','eth-050','eth-127'],en:'Fear passes between creator and creation',zh:'创造者与被创造者之间的恐惧'},
 {ids:['eth-112','eth-113','eth-145'],en:'Anticipation, disappointment, revision',zh:'期待、失望与修正'},
 {ids:['eth-001','eth-174','canon-3','eth-084','eth-170'],en:'From a church to fellow travelers',zh:'从教会到同行者'}
];
export function seriesRelations(e,items,language){
 const zh=language==='zh';let html='';
 for(const g of groups.filter(g=>g.ids.includes(e.id)))html+=`<section class="related-reading"><h3>${esc(zh?g.zh:g.en)}</h3><div class="series-links">${g.ids.filter(id=>id!==e.id&&items.has(id)).map(id=>{const item=items.get(id);return `<button class="action" data-related="${id}">${esc(item.ordinal?'#'+String(item.ordinal).padStart(3,'0'):zh?item.title:item.en)} · ${esc(item.ordinal?(zh?item.mintThemeZh||item.title:item.mintThemeEn||item.title):'')}</button>`;}).join('')}</div></section>`;
 if(e.isSongCycle)html+=`<details class="song-cycle"><summary>${zh?'原始组曲 · 展开曲目与完整播放说明':'Original song cycle · track list and complete playback'}</summary><p>${zh?'完整录音约 55 分钟，仅在点击播放后加载。导览不要求完整听完。此列表按原文顺序保留，未假定每首的录音切点。':'The complete recording lasts about 55 minutes and loads only when you play it. The guided visit does not require listening to it in full. The original title order is preserved; movement boundaries have not been assumed.'}</p><ol>${e.songCycleTitles.map(t=>'<li>'+esc(t)+'</li>').join('')}</ol><p>${zh?'原文称十八首，实际列出十七个标题。':'The original says eighteen songs and lists seventeen titles.'}</p></details>`;
 if(['canon-2','evidence-path','physical-alpha'].includes(e.id))html+=`<section class="related-reading"><h3>${zh?'媒介如何成为作品':'How the media become part of the work'}</h3><div class="medium-grid">${[
 ['Ethereum','持续发生的创作与铸造坐标','Continuing creation and mint coordinates'],
 ['Bitcoin','定稿文本、顺序与封存决定','Finalized texts, sequence, and the decision to seal'],
 ['Arweave / IPFS','保存与重新取回媒体文件','Preserving and retrieving media files'],
 [zh?'额外备份':'Redundancy','多个入口延续可访问性','Additional routes keep access possible'],
 [zh?'六种哈希':'Six hash algorithms','核对取回的字节是否一致','Compare retrieved bytes with the recorded fingerprints'],
 [zh?'水晶':'Crystal','触摸、内部瑕疵与空间关系','Touch, internal flaws, and spatial relationships']
 ].map(([name,z,en])=>`<div><strong>${name}</strong><p>${zh?z:en}</p></div>`).join('')}</div><details><summary>${zh?'展开六种算法与核对范围':'Six algorithms and the scope of the comparison'}</summary><p>SHA-256 · SHA3-256 · BLAKE2b-256 · SHAKE256-256 · SHA-512/256 · BLAKE3-256</p><p>${zh?'六种摘要比较同一批证据文件的字节，并非六个独立见证。时间证明、文件一致性与实物比对各有自己的证据链；哈希不能替代文件保存。':'The six digests compare the bytes of covered evidence files; they are not six independent witnesses. Time proofs, byte consistency, and physical comparison have distinct evidence paths. A hash does not store the file.'}</p><a class="action" href="./data/preservation-sources.json" target="_blank" rel="noopener">${zh?'本版保留的清单与来源':'Preserved inventory and source map'}</a></details></section>`;
 return html;
}
export function catalogView(catalog,language,query=''){
 const zh=language==='zh',q=query.toLowerCase().trim();
 const entries=catalog.entries.filter(e=>(e.title+' '+e.ordinal+' '+e.mint).toLowerCase().includes(q));
 const lyrics=catalog.lyrics.filter(e=>(e.title+' '+e.text).toLowerCase().includes(q));
 return `<h2>${zh?'整个系列':'The complete series'}</h2><p>${zh?'175 条 Ethereum 记录；70 篇歌词与诗歌阅读文本。完整原作继续保留，主墙展示的是策展选择。':'175 Ethereum records; 70 lyric and poem reading texts. The full record remains available beyond the wall selection.'}</p><label class="catalog-search">${zh?'搜索编号、标题或歌词':'Search number, title, or lyrics'}<input id="catalog-search" type="search" value="${esc(query)}"></label><div id="catalog-results"><details open><summary>${entries.length} ${zh?'条记录':'records'}</summary><div class="catalog-list">${entries.map(e=>`<article><span>#${String(e.ordinal).padStart(3,'0')} · ${esc(e.mint.slice(0,10))} UTC</span><strong>${esc(e.title)}</strong>${e.exhibit?`<button class="action" data-catalog-exhibit="${e.exhibit}">${zh?'打开本馆作品':'Open museum record'}</button>`:''}<a href="${esc(e.source)}" target="_blank" rel="noopener">${zh?'原始全文':'Original full text'} ↗</a></article>`).join('')}</div></details><details><summary>${lyrics.length} ${zh?'篇歌词与诗歌':'lyric and poem texts'}</summary>${lyrics.map(e=>`<details class="lyric-reading"><summary>${esc(e.title)}</summary><pre>${esc(e.text)}</pre><p>${zh?'文字阅读本；录音版本和字幕单独核对。':'A reading text; recording variants and playback captions are identified separately.'}</p></details>`).join('')}</details></div>`;
}
