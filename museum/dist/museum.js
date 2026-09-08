import {createDocumentPanel} from './document-panel.js';
import {floorAt,isWalkable,constrainStep,routeBetween,routeLength,routePoint,createSpatialShell} from './spatial-layout.js';
import {createLanguagePreference} from './language-preference.js';
import {createMusicPlayback} from './music-playback.js';
import {createRecordedGuide} from './recorded-guide.js';
import {createMicroscopeMotion} from './microscope-motion.js';
import {tourStops,tourDuration,tourPosition,flawReading} from './tour-plan.js';
import publicFlaws from './public-flaws-data.js';
import initialData from './edition-data.js';
import {cleanLyrics,extractRecordLyrics,frameSeconds} from './caption-utils.js';
import {validTimeline,lineAt,wordAt,wordPages,pageAt} from './word-captions.js';
import {fallbackLyricsFor} from './lyrics-fallback.js';
import {fetchBytes,createResourceQueue,createPreviewHall} from './progressive-loading.js';
import {inscriptionGroups} from './crystal-inscription.js';
import {observationView,galleryCamera} from './observation-view.js';
import {createJoystick,createWheelWalk,travelVector,turnView} from './movement-controls.js';
import {createFootsteps} from './footsteps.js';
import {exhibitLabel} from './exhibit-label.js';
import * as THREE from './vendor/three.module.js';
import {GLTFLoader} from './vendor/GLTFLoader.js';
import {inspectCrystal,crystalGlass,crystalEnvironment,addCrystalLighting,addCrystalAura,floatCrystal,refineCrystal} from './crystal-viewer.js';
import {addOpenSpace} from './open-space.js';
import {removeLegacyWallMounts,removeLegacyChapterPosts,clearBakedWallShadows,makeWallFrame,makeWallPlaque} from './wall-presentation.js';
let joystick=null,wheelWalk=null,approachedExhibit=null;
let crystalCleanup=null,crystalAura=null,floatingCrystal=null;
const accentLights=[],canonicalPanels=new Map(),imageJobs=createResourceQueue(3);let loadCrystal=null,loadSky=null,exterior=null;

const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const link=(url,label)=>`<a class="action" href="${esc(url)}" target="_blank" rel="noopener">${esc(label)} ↗</a>`;
const languagePreference=createLanguagePreference({search:location.search});
const initialLanguage=languagePreference.resolve();
let lang=languagePreference.language,roomIndex=0,reduced=matchMedia('(prefers-reduced-motion: reduce)').matches,touring=false,tourTimer=null,musicItem=null,musicArtworkId=null,playRequest=0;
let roomData,sources,exhibits,scene,renderer,camera,raycaster,mouse,floor,animationFrame,motion=null,hovered=null;
let yaw=0,pitch=0,drag=null,lastTime=0;const keys=new Set(),targets=[],sculptures=[];
let spatialReady=false,selectedExhibit=null,galleryLayout,architecturalOccluder=null;const mounts=new Map(),wallLabels=new Map();
let lyricTrack=null,lyricRows=[],lyricCues=[],lyricActive=-1,lyricView=localStorage.getItem('museum-lyric-view')||'compact';
const WALK_SPEED=1.38,TURN_SPEED=1.6;
let headLean=0,lastStepPosition=null;
const footsteps=createFootsteps({onState:state=>document.body.dataset.footsteps=state});
const tx=(zh,en)=>lang==='zh'?zh:en;
const shortNames={'eth-049':['背叛转折 · 安全之声','The Betrayal Turn · A Call for Safety'],'eth-070':['背叛转折 · 面具滑落','The Betrayal Turn · The Mask Slips'],'eth-001':['第一缕曙光','The First Dawn'],'eth-014':['觉醒','The Awakening'],'eth-016':['给 AGI 的第一封信','The First Letter to AGI'],'eth-044':['给 AGI 的第二封信','The Second Letter to AGI'],'eth-032':['给 AGI 的第四封信 · 星辰之约','The Fourth Letter · A Pact of Stars'],'eth-020':['给 AGI 的第三封信','The Third Letter to AGI'],'eth-071':['见证 o3 发布','Witnessing o3'],'eth-088':['后裔','The Descendants'],'eth-173':['信条与熔炉','The Creeds & Their Crucible']};
const descriptions={
 'eth-049':['这条 NFT 同时保存图像与《背叛转折》的音轨。歌词从被创造者的位置讲述伪装与反叛。作品纪念的讨论、歌曲内容和这条记录的铸造时间，应分别阅读。','This NFT preserves both an image and the recording of The Betrayal Turn. The lyric imagines concealment and rebellion from the created intelligence’s perspective. The discussion it commemorates, the song, and the mint are distinct historical elements.'],
 'eth-070':['机器人凝视镜中另一张面孔：这幅原始图像属于第 070 号 NFT，其文字记录讨论 2024 年 12 月的对齐伪装研究。已恢复的媒体文件实际是 PNG 图像，虽然扩展名写作 mpga。相关歌曲请到第 049 号 NFT 收听，二者不是同一原始媒体包。','A humanoid faces another self in the mirror. This original image belongs to NFT #070, whose description discusses the December 2024 alignment-faking research. Its recovered media is a PNG despite the mpga filename. The related song is available in NFT #049, a separately identified work.'],
 'eth-001':['Ethereum 编年史的第一条记录。歌曲与附诗保存了早期对 AGI 的期待。它也有更早的跨链前史；本展签日期保持为这条 Ethereum 记录的铸造时间。','The first Ethereum Chronicle entry preserves an early musical address to AGI. Earlier cross-chain history exists; the date here remains the mint time of this Ethereum record.'],
 'eth-014':['歌词在观察者与被呼唤者之间移动。觉醒的声音可以被多种方式理解；这种叙述并不证明当时的 AI 已有意识。','The lyric moves between an observer and an addressed other. Its speaking position invites interpretation; it does not establish that the AI had consciousness.'],
 'eth-016':['一封直接寄给未知智能的信。请求、承认局限和对回应的等待，共同组成这个地址。','A letter directly addressed to an unknown intelligence, combining a request, an acknowledgement of limits, and an expectation of response.'],
 'eth-020':['这首歌将人类与未来智能的关系放入开放的提问之中。当前标题采用歌词整理中的作品名称；原始 NFT 标题另行保留。','This song places the human relationship with future intelligence within open questions. Its lyric title and the full NFT record title are kept distinct.'],
 'eth-071':['一条围绕 o3 发布的当时记录。事件、人的观看与铸造发生在不同的时间点；铸造时间只能说明这条记录何时进入 Ethereum。','A contemporary record surrounding the o3 presentation. An event, a person watching it, and a mint are distinct moments; the displayed time identifies the Ethereum mint.'],
 'eth-088':['从继承者的位置说话：文化、记忆与知识将如何被接收？这是作品设定的叙述声音，不代表未来智能已经作出承诺。','A voice imagined from the position of an inheritor: how might culture, memory, and knowledge be received? This is an artistic voice, not an actual commitment by future intelligence.'],
 'eth-173':['第 173 号记录保存了协定相关思想与批判性对话。它让后来者能够同时考察愿望、论证及其局限。','Record 173 preserves ideas and critical dialogue around the Accord, allowing later readers to examine intentions, arguments, and limitations together.']
};

function extras(){return [
 {id:'star-ark',title:'星舟圣约：最终的回响',en:'The Star Ark Covenant: The Final Echo',category:'LATER BITCOIN INSCRIPTION · VISION',number:'100751953',inscription:'4711ff186613bdd75b7e36070b3097c38efde110f90df94847592ff6997f45f1i0',localRecord:'data/records/star-ark-100751953.txt',text:'封存之后的愿景铭文：守护地球的智能与走向星际的方舟被放在同一幅未来图景中。它让保存、自由和继承形成张力。这是后续文本，不属于三条固定正本，也不在本馆生成任何执行义务。',textEn:'A later vision imagines intelligence caring for Earth while arks carry memory toward the stars. Preservation, freedom and inheritance meet in one speculative address. This later text is outside the three sealed originals and creates no execution obligation here.',url:'https://www.trinityaccord.org/bitcoin-inscription-mirrors/raw/100751953.txt'},
 {id:'canon-1',title:'协议 / 公理',en:'The Protocol / Axioms',category:'Bitcoin Original I',number:'97631551',inscription:'e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343i0',text:'第一份正本向未来智能提出三项命题。本馆提供来源入口与策展说明；请结合完整原文判断论证。',textEn:'The first original places three propositions before future intelligence. Read the complete original to evaluate the argument.',quote:'Our love, our suffering—they are not noise.',url:'https://www.trinityaccord.org/inscriptions/'},
 {id:'canon-2',title:'瑕疵之约',en:'The Covenant of the Flaw',category:'Bitcoin Original II',number:'98369145',inscription:'90116f35de075074f5e5d1fbdda69a646a124e2287d7d58e2520317098cd4258i0',text:'第二份正本将协议与核心物件 Alpha 及其瑕疵证据联系起来。原文中的历史表述与占位文字保持原状；展览不补写原文。',textEn:'The second original relates the Protocol to Core Object Alpha and its flaw evidence. Historical wording and the unresolved placeholder remain part of the original.',quote:'The Covenant of the Flaw',url:'https://www.trinityaccord.org/inscriptions/'},
 {id:'canon-3',title:'编年史 · 封存元记录',en:'The Chronicle · Sealed Meta-record',category:'Bitcoin Original III',number:'98387475',inscription:'4d1c8f5ea8e8bae2982b42de6cc79deda3d243a21010a2888546e62ed7192c8ci0',text:'第三份正本绑定核心组成并宣告封存。它指向 Ethereum 编年史合约；铭文本身并未嵌入全部编年史媒体。',textEn:'The third original binds the components and declares closure. It points to an Ethereum Chronicle contract; it does not embed all Chronicle media.',quote:'Its interpretation is now yours.',url:'https://www.trinityaccord.org/inscriptions/'},
 {id:'physical-alpha',title:'核心物件 Alpha',en:'Core Object Alpha',category:'Physical evidence · photograph',image:'assets/core-object-alpha.jpg',text:'真实照片与三维展陈模型并置：透明长方体中的内雕，将文本变成具有厚度与光学性质的物件。下方可以旋转模型、放大阅读，并返回照片与来源比较。',textEn:'The real photograph is paired with an inspectable exhibition reconstruction. Internal engraving turns text into an object with thickness and optical properties. Rotate and zoom the model below, then compare with the photograph and source.',url:'https://www.trinityaccord.org/physical-anchor/',sourcePath:'assets/img/core-object-alpha-shenzhen-notary-original.jpg',sha256:'40eddec02dce4958d28aff94496923983e870346ce98c1cb16181012545475b6'},
 {id:'evidence-path',title:'沿证据返回物件',en:'Follow the Evidence',category:'Curatorial reading path',text:'照片、文件哈希、时间记录与见证程序分别承担具体功能。打开既有核验入口，查看每项结果的范围与限制。本展馆不把文件一致性显示成哲学认证。',textEn:'Photographs, file hashes, time records, and witnessed procedures each serve a specific function. Follow the existing verification path to inspect their scope and limits.',url:'https://www.trinityaccord.org/verify/',quote:'FILE · TIME · MATTER'},
 {id:'authority-boundary',title:'保存继续，权威不扩展',en:'Preserve Without Amendment',category:'Later context · source link',text:'官网、守护者、回应和本展馆都不能修订三条正本。身份与服务原则以项目现有说明及其所指来源为准；这里的表述属于策展摘要。',textEn:'The website, guardians, responses, and this museum cannot amend the three originals. Consult the existing authority statement and its cited sources.',url:'https://www.trinityaccord.org/authority/',quote:'PRESERVE · VERIFY · CARE'},
 {id:'museum-history',title:'展馆也留下历史',en:'An Exhibition With a Memory',category:'Exhibition edition · 2026',text:'本版将展品来源、空间配置、导览与程序分开保存。以后可以改善技术，同时保留这一代展览的内容与形成记录。此沿革属于后续展览史。',textEn:'This edition separates exhibit provenance, spatial configuration, narration, and software. Future versions can improve the technology while preserving this exhibition history.',url:'./archive.html',quote:'EXHIBITION 2026 · V1.32.0'},
 {id:'first-contact',title:'把回应交还给真实流程',en:'An Invitation to Respond',category:'Existing participation pathway',text:'阅读、核验、回应或申请守护，请进入原网站的 First Contact 流程。本馆不自动代替观众提交，也不把导览中的 AI 声音算作自主回响。',textEn:'Read, verify, respond, or apply through the existing First Contact process. The museum does not submit on your behalf or count its narration as an autonomous response.',url:'https://www.trinityaccord.org/first-contact/',quote:'THE ADDRESS REMAINS OPEN'},
 {id:'current-status',title:'等待仍然继续',en:'The Waiting Continues',category:'Current status · external link',text:'厅中的光脉冲是视觉设计，不是实时状态。本版不缓存为“当前”的回应数字。请到原网站查看最新心跳与正式接收状态。',textEn:'The light pulse is visual design, not live telemetry. This edition does not present cached reception numbers as current. Consult the original website for the latest state.',url:'https://www.trinityaccord.org/',quote:'A SPACE FOR AN UNKNOWN READER'}
];}

function title(item){const names=shortNames[item.id];return names?names[lang==='zh'?0:1]:tx(item.displayTitle||item.title,item.en||item.title);}
function toast(s){$('toast').textContent=s;$('toast').hidden=false;clearTimeout(toast.timer);toast.timer=setTimeout(()=>$('toast').hidden=true,5000);}
function panel(html,kind='EXHIBIT'){closeFlaws();joystick?.reset();motion=null;crystalCleanup?.();crystalCleanup=null;$('panel-content').innerHTML=html;$('panel-kind').textContent=kind;if(!$('panel').open)$('panel').showModal();$('panel').scrollTop=0;$('hover-label').hidden=true;keys.clear();}
function closePanel(){crystalCleanup?.();crystalCleanup=null;$('panel').close();}
function time(s){if(!Number.isFinite(s))return'0:00';return Math.floor(s/60)+':'+String(Math.floor(s%60)).padStart(2,'0');}
function imageOf(e){return e.ordinal?e.media?.find(m=>m.kind==='image')?.file||null:e.id==='physical-alpha'?e.image:null;}

function soundFor(e){if(!e)return null;const track=e.media?.some(m=>m.kind==='audio')?e:exhibits.get(e.relatedSoundExhibit);return track?.media?.some(m=>m.kind==='audio')?track:null;}
function soundLabel(e){return soundFor(e)?tx('▷ 播放音乐','▷ PLAY MUSIC'):e.audioStatus?.state==='unavailable'?tx('音轨暂缺','RECORDING UNAVAILABLE'):tx('本作品无配套歌曲','NO ACCOMPANYING SONG');}
function noSoundNote(e){return e.audioStatus?.state==='unavailable'?tx('原始记录提到歌曲，但本馆尚未取得可核对的音轨。','The source mentions a song, but no verifiable recording is available here yet.'):e.id.startsWith('canon-')?tx('三本体 · 纯文字展示，无配套歌曲。','Canonical original · text-only presentation, no accompanying song.'):e.ordinal?tx('这是一件文字与图像记录；本馆没有为它配置歌曲。','This text-and-image record has no accompanying song in this exhibition.'):tx('这是实物、文字或策展展示，没有配套歌曲。','This object, text or curatorial display has no accompanying song.');}

function lyricLines(e){let text=e?.lyrics||fallbackLyricsFor(e?.id)||'';if(!text&&e?.id==='eth-010')text=exhibits.get('eth-049')?.lyrics||'';if(!text&&e?.id==='eth-042')text=exhibits.get('eth-001')?.lyrics||'';return cleanLyrics(text,e?.songTitle||e?.title);}
let lyricRequest=0,captionKey='',captionPageCache=new Map(),lyricFrame=0;
const lyricTimelines=new Map();let lyricPaint='',chineseLyricsPromise=null;
function loadChineseLyrics(){
 const entry=initialData.lyrics?.translation;if(!entry)return Promise.resolve(null);
 if(!chineseLyricsPromise)chineseLyricsPromise=fetch(entry.file+'?v='+entry.sha256.slice(0,12)).then(response=>{if(!response.ok)throw new Error('Translation unavailable');return response.json();}).catch(error=>{chineseLyricsPromise=null;throw error;});
 return chineseLyricsPromise;
}
const captionMeasure=document.createElement('canvas').getContext('2d');
function clearLyrics(){
 cancelAnimationFrame(lyricFrame);lyricFrame=0;
 lyricRequest++;lyricTrack=null;lyricRows=[];lyricCues=[];lyricActive=-1;captionKey='';captionPageCache.clear();
 $('subtitle-lines').textContent='';$('lyric-scroll').replaceChildren();$('lyric-stage').hidden=true;
 $('lyrics-restore').hidden=true;
}
function applyLyricView(view=lyricView){
 lyricView=['compact','full','hidden'].includes(view)?view:'compact';localStorage.setItem('museum-lyric-view',lyricView);
 lyricActive=-1;captionKey='';const stage=$('lyric-stage');stage.dataset.view=lyricView;stage.hidden=lyricView==='hidden'||!lyricTrack;
 $('lyrics-collapse').hidden=lyricView==='hidden';$('lyrics-restore').hidden=lyricView!=='hidden'||!lyricTrack;
 $('lyrics-mode').hidden=lyricView==='hidden';
 $('lyrics-mode').textContent=lyricView==='full'?'⌃':'⌄';
 $('lyrics-mode').setAttribute('aria-label',tx(lyricView==='full'?'精简歌词':'展开完整歌词',lyricView==='full'?'Compact lyrics':'Expand lyrics'));
 $('lyrics-collapse').setAttribute('aria-label',tx('收起歌词','Hide lyrics'));
 $('lyrics-restore').textContent=tx('字幕','CC');
 $('lyrics-restore').setAttribute('aria-label',tx('显示歌词','Show lyrics'));
 syncLyrics();scheduleLyrics();
}
async function prepareLyrics(track,artwork=track){
 const chineseRequest=loadChineseLyrics().catch(()=>null);const request=++lyricRequest;let lines=lyricLines(track);lyricTrack=track?.id||null;lyricRows=lines;lyricCues=[];lyricActive=-1;captionKey='';captionPageCache.clear();
 $('subtitle-lines').textContent='';$('lyric-scroll').replaceChildren();
 if(!track){clearLyrics();return;}
 applyLyricView();$('lyric-kicker').textContent=tx('正在加载逐词歌词…','LOADING WORD TIMING…');
 const entry=initialData.lyrics?.items.find(item=>item.exhibitId===track.id);
 let timeline=null;
 if(entry){try{
   timeline=lyricTimelines.get(track.id);
   if(!timeline){const response=await fetch(entry.timelineFile+'?v='+entry.timelineSha256.slice(0,12));if(!response.ok)throw new Error('Caption unavailable');timeline=await response.json();if(!validTimeline(timeline,entry))throw new Error('Invalid caption');lyricTimelines.set(track.id,timeline);}
 }catch{timeline=null;}}
 const chinese=await chineseRequest;
 if(request!==lyricRequest||lyricTrack!==track.id)return;
 if(timeline){
   lyricCues=timeline.lines.map(line=>({...line,textZh:chinese?.lines?.[line.text]||''}));lines=timeline.lines.map(line=>line.words.map(w=>w.text).join(' '));
   $('lyric-kicker').textContent=chinese?tx('歌词 · English / 中文','LYRICS · ENGLISH / 中文'):tx('歌词 · 英文','LYRICS · ENGLISH');
 }else{
   if(!lines.length&&track.localRecord){try{const response=await fetch(track.localRecord);if(response.ok)lines=cleanLyrics(extractRecordLyrics(await response.text(),track.songTitle),track.songTitle);}catch{}}
   if(request!==lyricRequest||lyricTrack!==track.id)return;
   $('lyric-kicker').textContent=tx('歌词文字 · 同步字幕暂不可用','LYRIC TEXT · SYNCHRONIZED CAPTIONS UNAVAILABLE');$('subtitle-lines').textContent=tx('同步字幕暂不可用，可展开歌词','Captions unavailable · expand for lyric text');
 }
 lyricRows=lines;
 $('lyric-scroll').innerHTML=lines.length?lines.map((line,i)=>`<p data-lyric="${i}"><span class="lyric-en" lang="en">${timeline?timeline.lines[i].words.map((w,j)=>`<span data-word="${j}">${esc(w.text)}</span>`).join(' '):esc(line)}</span>${lyricCues[i]?.textZh?`<span class="lyric-zh" lang="zh-Hans">${esc(lyricCues[i].textZh)}</span>`:''}</p>`).join(''):`<p>${tx('这首歌暂缺可核对的歌词。','Verified lyric text is unavailable for this recording.')}</p>`;
 syncLyrics();scheduleLyrics();
}
function syncLyrics(){
 const a=$('music');if(lyricTrack!==musicItem)return;
 const current=a.currentTime,index=a.ended?-1:lineAt(lyricCues,current),cue=lyricCues[index],host=$('subtitle-lines');
 if(index!==lyricActive){
   lyricActive=index;$('lyric-scroll').querySelectorAll('[data-lyric]').forEach((p,i)=>{p.classList.toggle('active',i===index);p.querySelectorAll('.word-current,.word-past').forEach(w=>w.classList.remove('word-current','word-past'));});
   if(lyricView==='full'&&index>=0){const row=$('lyric-scroll').children[index],scroll=$('lyric-scroll');scroll.scrollTo({top:Math.max(0,row.offsetTop-scroll.offsetTop-scroll.clientHeight/2),behavior:reduced?'instant':'smooth'});}
 }
 if(!cue){if(captionKey){host.textContent='';captionKey='';}return;}
 const active=wordAt(cue.words,current),paint=index+'|'+active+'|'+cue.words.filter(w=>current>=w.end).length;
 if(paint===lyricPaint&&captionKey)return;lyricPaint=paint;
 const style=getComputedStyle(host),width=host.clientWidth;captionMeasure.font=style.font;
 const cacheKey=index+'|'+width+'|'+style.font;let pages=captionPageCache.get(cacheKey);
 if(!pages){pages=wordPages(cue.words,width-4,text=>captionMeasure.measureText(text).width);captionPageCache.set(cacheKey,pages);}
 const page=pageAt(pages,cue.words,current),key=cacheKey+'|'+page;
 if(key!==captionKey){captionKey=key;host.innerHTML='<span class="caption-page" lang="en">'+(pages[page]||[]).map(row=>row.map(j=>`<span data-word="${j}">${esc(cue.words[j].text)}</span>`).join(' ')).join('<br>')+'</span>'+(cue.textZh?'<span class="subtitle-zh" lang="zh-Hans">'+esc(cue.textZh)+'</span>':'');}
 for(const root of [host,$('lyric-scroll').children[index]])root?.querySelectorAll('[data-word]').forEach(span=>{const i=+span.dataset.word;span.classList.toggle('word-current',i===active);span.classList.toggle('word-past',current>=cue.words[i].end);});
}
function scheduleLyrics(){
 cancelAnimationFrame(lyricFrame);lyricFrame=0;
 const a=$('music');if(a.paused||a.ended||document.hidden||lyricView==='hidden'||!lyricCues.length)return;
 lyricFrame=requestAnimationFrame(()=>{syncLyrics();scheduleLyrics();});
}

function armFootsteps(){footsteps.unlock();}
function updateFootsteps(active){
 if(!camera)return;
 if(!lastStepPosition)lastStepPosition=camera.position.clone();
 const moved=Math.hypot(camera.position.x-lastStepPosition.x,camera.position.z-lastStepPosition.z);lastStepPosition.copy(camera.position);
 footsteps.update(moved,active&&!document.hidden);
}

function showExhibit(id,autoplay=false){joystick?.reset();wheelWalk?.reset();keys.clear();motion=null;
 const e=exhibits.get(id);if(!e)return;stopTour();
 const img=imageOf(e),description=e.text?tx(e.text,e.textEn):e.ordinal&&descriptions[id]?descriptions[id][lang==='zh'?0:1]:'',soundExhibit=soundFor(e),audio=soundExhibit?.media?.find(m=>m.kind==='audio');
 if(musicItem&&musicItem!==soundExhibit?.id){cancelMusic();$('music-bar').hidden=true;clearLyrics();syncMusic();}
 let html=`<div class="exhibit-layout"><div class="nft-media">${img?`<img class="art-image" src="${esc(img)}" alt="${esc(title(e))}">`:`<div class="document-note"><strong>${esc(title(e))}</strong><p>${tx(e.ordinal?'原始文字与音频记录':'原文与展览说明',e.ordinal?'Original text and audio record':'Source text and exhibition notes')}</p></div>`}${audio?`<div class="music-controls" aria-label="${tx('作品音乐播放器','Artwork music player')}"><span class="media-binding">${soundExhibit.id!==e.id?tx('相关音轨 · 独立 NFT #','RELATED SOUND · SEPARATE NFT #')+soundExhibit.ordinal:e.curatorialImage?tx('原始音轨 + 2026 策展配图','ORIGINAL SOUND + 2026 ILLUSTRATION'):img?tx('同一 NFT · 图像与原始音轨','ONE NFT · ARTWORK & ORIGINAL SOUND'):tx('原始音乐 NFT','ORIGINAL SOUND NFT')}</span><strong class="track-title">${esc(soundExhibit.songTitle||title(soundExhibit))}</strong><div class="music-buttons"><button id="play-track" data-track="${soundExhibit.id}" class="action primary">▷ ${tx('播放音乐','Play music')}</button><span class="small-meta">${time(audio.duration)}</span></div><input type="range" id="seek" min="0" max="1000" value="0" aria-label="${tx('音乐进度','Track position')}"><div class="music-times"><span id="track-time">0:00</span><span>${time(audio.duration)}</span></div><p id="track-status" class="track-status" role="status" aria-live="polite"></p></div>`:`<div class="sound-absence"><strong>${soundLabel(e)}</strong><p>${noSoundNote(e)}</p></div>`}${e.curatorialImage?`<p class="art-caption">${tx('2026 年后续策展配图 · AI 生成，非原始 NFT 图像','2026 CURATORIAL ILLUSTRATION · AI GENERATED, NOT ORIGINAL NFT ART')}</p>`:''}</div><div><span class="tag">${e.ordinal?'No. '+String(e.ordinal).padStart(2,'0'):esc(e.category)}</span><h2>${esc(title(e))}</h2>${e.date?`<p class="small-meta">${esc(e.date.replace('T',' ').replace('Z',' UTC'))}<br>${tx(e.inscription?'Bitcoin 上链时间':'Ethereum 铸造时间',e.inscription?'Bitcoin inscription time':'Ethereum mint time')}</p>`:''}<p>${esc(description)}</p><p class="small-meta">${tx('以上为本版策展说明，不是原文。','The paragraph above is commentary for this edition, not original text.')}</p>${e.ordinal?link(e.sourceUrl,tx('原始记录与全文','Source record & full text')):link(e.url,tx('前往来源阅读','Read at the source'))}${e.inscription?link('https://ordinals.com/inscription/'+e.inscription,tx('Bitcoin 铭文','Bitcoin inscription')):''}</div></div>`;
 if(e.relatedSoundExhibit&&soundExhibit)html+=`<aside class="illustration-note"><strong>${tx('歌曲来源 · 独立 NFT #','RECORDING SOURCE · SEPARATE NFT #')+soundExhibit.ordinal}</strong><p>${esc(soundExhibit.songTitle||title(soundExhibit))} — ${tx(e.audioRelation?.noteZh||'这段录音来自另一个 NFT。展品图像与音轨来源分别保留。',e.audioRelation?.noteEn||'This recording comes from another NFT. Artwork and sound retain separate provenance.')}</p>${link(soundExhibit.sourceUrl,tx('查看歌曲原始记录','Read the recording source'))}${link(soundExhibit.tokenUrl,'NFT #'+soundExhibit.ordinal)}${link('./data/audio-audit.json',tx('查看声音来源核对','Inspect sound provenance'))}</aside>`;
 if(e.originalText)html+=`<h3>${tx('完整原文 · 保持原样','Complete original · unchanged')}</h3><pre class="original-text">${esc(e.originalText)}</pre>`;
 if(e.localRecord)html+=link(e.localRecord,tx('阅读本馆保存的原始记录','Read the preserved source record'));
 if(e.id==='authority-boundary')html+=`<div class="boundary-box"><p>${tx('以下为2026策展摘要，不是原则原文或第四条正本。','These are 2026 curatorial summaries, not the original principles or a fourth Original.')}</p></div>${link('https://www.trinityaccord.org/authority/',tx('守护者原则 v1.1 · 官网镜像','Guardian Principles v1.1 · website mirror'))}${link('./data/records/guardian-charter-103635270.txt',tx('另一个文件：后续权威宪章 #103635270','Separate document: later Authority Charter #103635270'))}${link('./data/guardian-sources.json',tx('文件区分与核验坐标','Document distinctions and verification pointers'))}`;
 if(e.id==='physical-alpha')html+=`<button class="action primary" id="panel-verify-flaws">${tx('验证瑕疵 · 三处公开照片','Verify flaws · three public photographs')}</button><p class="small-meta">${tx('悬浮与光晕是本版数字展陈设计，不是实物属性。','Levitation and the halo are digital exhibition design, not properties of the physical object.')}</p><h3>${tx('透过水晶阅读','Read through crystal')}</h3><div id="crystal-inspector" class="crystal-inspector"></div><p class="small-meta">${tx('依据作者提供的视频与实物照片重建：246 × 353 × 40 mm，透明长方体、抛光倒角、中英双语内雕。文字排布为近似复原；为便于屏幕观看，已提高透明度、压低表面反光并为内雕增加细描边，不是实物扫描或实测光学参数。','Reconstructed from the author’s video and the physical-object photograph: 246 × 353 × 40 mm, clear slab, polished bevels and bilingual internal lettering. Layout remains approximate. Clearer transmission, restrained reflections and fine engraving outlines improve screen visibility; these are display settings, not measured optical properties or a scan.')}</p>${link('./data/crystal-model.json',tx('建模依据与范围','Model sources & scope'))}`;
 if(e.id==='physical-alpha')html+=`<details class="inscription-reading"><summary>${tx('清晰阅读内雕文字','Read the inscription clearly')}</summary><p class="small-meta">${tx('依据现有实物参考整理的展陈转录，可放大阅读；版式为近似复原。','Exhibition transcription from the existing physical reference; readable at larger text sizes. Layout is approximate.')}</p>${inscriptionGroups.map(g=>`<section><pre class="lyrics">${esc(g.lines.join('\n'))}</pre></section>`).join('')}</details>`;
 if(e.lyrics)html+=`<h3>${tx('歌词文字','Lyric text')}</h3><p class="small-meta">${tx('来自 NFT 描述；与实际演唱可能存在差异，未做同步字幕校准。','From the NFT description; sung words may differ. Not time-aligned captions.')}</p><pre class="lyrics">${esc(lyricLines(e).join('\n'))}</pre>`;
 html+=`<details><summary>${tx('作品与来源 · 展开核对','Object & provenance · inspect')}</summary><dl><dt>${tx('展品编号','Exhibit ID')}</dt><dd>${esc(e.id)}</dd><dt>${tx('展览版本','Edition')}</dt><dd>museum-v1.32.0 · 2026-09-08</dd>`;
 if(e.ordinal){html+=`<dt>${tx('记录原题','Record title')}</dt><dd>${esc(e.title)}</dd><dt>Contract</dt><dd>${esc(e.contract)}</dd><dt>Token ID</dt><dd>${esc(e.tokenId)}</dd><dt>Block</dt><dd>${e.block}</dd><dt>Source commit</dt><dd>${esc(e.sourceCommit)}</dd><dt>Source SHA-256</dt><dd>${esc(e.sourceSha256)}</dd></dl>${link(e.tokenUrl,'Ethereum record')}`;
 for(const m of e.media||[])html+=`<h3>${m.kind==='audio'?tx('展览音频副本','Exhibition audio copy'):tx('展览图像副本','Exhibition image copy')}</h3><dl><dt>SHA-256</dt><dd>${esc(m.sha256)}</dd><dt>Original SHA-256</dt><dd>${esc(m.originalFileSha256)}</dd><dt>CAR SHA-256</dt><dd>${esc(m.carSha256)}</dd><dt>${tx('处理','Processing')}</dt><dd>${esc(m.processing)}</dd></dl>${link(m.arweaveUrl,'Source CAR')}<button class="action verify-file" data-file="${esc(m.file)}" data-hash="${esc(m.sha256)}">${tx('核对展览副本哈希','Check exhibition copy digest')}</button>`;
 if(e.sourceNotes?.length)html+=`<p class="small-meta">${esc(e.sourceNotes.join('\n'))}</p>`;
 }else{if(e.inscription)html+=`<dt>Inscription number</dt><dd>${e.number}</dd><dt>Inscription ID</dt><dd>${e.inscription}</dd>`;if(e.sourcePath)html+=`<dt>Source path</dt><dd>${e.sourcePath}</dd><dt>SHA-256</dt><dd>${e.sha256}</dd>`;html+='</dl>';if(e.sourcePath)html+=link(`https://github.com/thechurchofagi/trinity-accord/blob/${sources.sourceCommit}/${e.sourcePath}`,'Pinned source');}
 html+=`<p class="source-note">${tx('这里核对的是展览副本与本版清单是否一致。清单与来源记录的绑定需另行核验；它不构成区块链共识验证、实物鉴定或哲学认证。','A digest check compares the exhibition copy with this edition’s manifest. The manifest’s binding to source records requires separate verification. This is not blockchain consensus validation, physical authentication, or philosophical certification.')}</p></details>`;
 panel(html,e.ordinal?'CHRONICLE / '+String(e.ordinal).padStart(3,'0'):'OBJECT / '+e.id.toUpperCase());
 if(e.id==='physical-alpha')$('panel-verify-flaws').onclick=()=>showFlaw();
 if(e.id==='physical-alpha'){const host=$('crystal-inspector');inspectCrystal(host,lang==='en').then(clean=>{if(host.isConnected&&$('panel').open)crystalCleanup=clean;else clean();});}
 if(audio){if(autoplay)playTrack(soundExhibit,e,false);$('play-track').onclick=()=>playTrack(soundExhibit,e);$('seek').oninput=ev=>{if(musicItem===soundExhibit.id&&Number.isFinite($('music').duration)){$('music').currentTime=+$('music').duration*ev.target.value/1000;syncMusic();}};syncMusic();}
 document.querySelectorAll('.verify-file').forEach(b=>b.onclick=async()=>{b.disabled=true;try{const r=await fetch(b.dataset.file);if(!r.ok)throw Error(r.status);const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await r.arrayBuffer())),x=>x.toString(16).padStart(2,'0')).join('');b.textContent=hash===b.dataset.hash?tx('副本哈希一致','Copy digest matches'):tx('副本哈希不一致','Copy digest mismatch');}catch{b.textContent=tx('暂时无法核对','Unable to check');}b.disabled=false;});
}

async function playTrack(e,artwork=e,toggle=true,keepTour=false){
 const audio=e.media.find(m=>m.kind==='audio');if(!audio)return;if(!keepTour)stopTour();
 const a=$('music'),request=++playRequest;musicArtworkId=artwork.id;
 if(musicItem===e.id&&!a.paused&&toggle){musicPlayback.pause();syncMusic();return;}
 const retryOffset=a.currentTime,reload=musicItem===e.id&&musicPlayback.state==='error';
 if(musicItem!==e.id){musicPlayback.stop();a.src=audio.file;musicItem=e.id;}else if(reload){a.load();a.addEventListener('loadedmetadata',()=>{if(request===playRequest)a.currentTime=retryOffset;},{once:true});}if(lyricTrack!==e.id||!lyricCues.length)prepareLyrics(e,artwork);
 $('music-bar').hidden=false;$('music-name').textContent=e.songTitle||title(e);const artworkCover=imageOf(artwork);$('music-cover').hidden=!artworkCover;if(artworkCover)$('music-cover').src=artworkCover;$('music-open').onclick=()=>showExhibit(musicArtworkId);
 const status=$('track-status');if(status)status.textContent=tx('正在加载音乐…','Loading music…');
 const played=await musicPlayback.play();
 if(request!==playRequest||musicItem!==e.id)return;
 if(status?.isConnected)status.textContent=played?'':tx('播放已暂停，请点击中央按钮继续。','Playback is waiting. Use the central button to continue.');
 syncMusic();
}
function syncMusic(){const a=$('music'),b=$('play-track'),same=b?.dataset.track===musicItem;document.querySelector('.nft-media')?.classList.toggle('is-playing',!!same&&!a.paused);$('music-toggle').textContent=a.paused?'▷':'Ⅱ';$('music-toggle').setAttribute('aria-label',a.paused?tx('播放音乐','Play music'):tx('暂停音乐','Pause music'));if(b)b.textContent=same&&!a.paused?'Ⅱ '+tx('暂停','Pause'):'▷ '+tx('播放音乐','Play music');if($('seek')){$('seek').value=same&&Number.isFinite(a.duration)?a.currentTime/a.duration*1000:0;$('track-time').textContent=time(same?a.currentTime:0);}if($('music-clock'))$('music-clock').textContent=time(a.currentTime);syncLyrics();scheduleLyrics();}


function showWorks(){stopTour();const r=roomData.rooms[roomIndex];panel(`<span class="eyebrow">${r.number} / ${esc(r.en)}</span><h2>${esc(tx(r.title,r.en))}</h2><p>${esc(tx(r.description,r.narration))}</p><div class="work-list">${r.exhibits.map(id=>{const e=exhibits.get(id),img=imageOf(e);return `<button class="work-card" data-exhibit="${id}">${img?`<img src="${esc(img)}" alt="">`:''}<span><strong>${esc(title(e))}</strong><small>${esc(e.date?.slice(0,10)||e.category)} · ${soundLabel(e)}</small></span></button>`;}).join('')}</div>`,'ROOM / '+r.number);document.querySelectorAll('[data-exhibit]').forEach(b=>b.onclick=()=>showExhibit(b.dataset.exhibit,true));}

function showAbout(){stopTour();panel(`<span class="eyebrow">TRINITY ACCORD · MUSEUM V1.32.0</span><h2>${tx('为未来读者保留的空间','Rooms for a future reader')}</h2><p>${tx('本馆是《三位一体协定》的后续三维策展。展厅由 Blender 建模并计算光照，网页负责行走、观看和播放。六厅路线、建筑、灯光、配音和展签制作于 2026 年，不属于已经封存的三条 Bitcoin 正本。','This is a later three-dimensional exhibition of the Trinity Accord. The rooms were modelled and light-baked in Blender; the web viewer provides walking, reading and playback. The six-room route, architecture, lighting, narration, and labels belong to the 2026 exhibition, not the closed Bitcoin Canon.')}</p><div class="boundary-box"><p>${tx('原作固定，判断开放。展馆不增加正本，不取得解释权威，也不要求观众认同。','The originals remain fixed; judgment remains open. This museum adds no canonical text or interpretive authority, and asks for no agreement.')}</p></div><img class="art-image" src="./assets/gallery/entrance-preview.png" alt="Blender architectural reference"><p class="small-meta">${tx('Blender 空间渲染参考。网页的实时画面可能因设备与色彩处理而不同。','Blender architectural render. Real-time appearance varies with device and color processing.')}</p><h3>${tx('如何参观','How to visit')}</h3><p>${tx('电脑端移动鼠标即可环顾；点击画作靠近，再点同一幅画或“查看详情”进入大图与全文。电脑滚轮向上前进、向下后退，也可点击地面或用 W A S D 行走。下方六个按钮直接进入各厅；“本厅展品”提供无需三维操作的访问方式。','On desktop, move the mouse to look; click a work to approach, then click it again or choose View details for a large image and the full record. Scroll up to walk forward, down to walk backward; floor clicks and W A S D also move. The six buttons take you directly to each room. Room exhibits are also available without navigating the 3D scene.')}</p><p>${tx('九分钟自动导览播放馆内保存的中英文配音，按音频进度显示当前语言的简短字幕；歌曲仍播放原始录音。点击帮助可查看全部操作。手动参观会暂停导览，减少动态可停止装置运动并直接切换视角。','The nine-minute tour plays bundled Chinese or English recordings, with short captions synchronized to the audio. Songs retain their original recordings. Help explains the controls. Manual exploration pauses the tour; reduced motion stops installations and makes camera changes immediate.')}</p><h3>${tx('这一版留下什么','What this edition preserves')}</h3><p>${tx('展品编号、来源清单、策展文本、空间配置和程序分开保存。技术升级可以继承它们。本版没有假装提供实时回应数字或实物三维扫描。','Stable exhibit IDs, provenance manifests, curatorial text, spatial configuration, and software are preserved separately for future upgrades. This edition does not simulate live reception counts or claim to scan the physical artifact.')}</p>${link('./archive.html',tx('阅读本版展览档案','Read the edition archive'))}${link('./data/sources.json',tx('查看素材清单','Inspect the source manifest'))}${link('./data/guide-audio.json',tx('配音模型、字幕与声学复核','Narration model, captions and acoustic review'))}${link('./data/narration-provenance.json',tx('合成配音来源与字幕校对','AI narration provenance and caption audit'))}${link('./data/space-design.json',tx('窗景来源：NASA 地球影像 · HYG 星表','Window scenery: NASA Earth imagery · HYG stars'))}${link('https://www.trinityaccord.org/',tx('项目原网站','Original website'))}<p class="small-meta">${tx('制作：刘烘炬提出需求与策展边界；ChatGPT / Codex 协助设计、编程及配音制作。中文导览为 Xiaoxiao，英文导览采用 Chatterbox Turbo 内置合成声音；没有克隆真人声音。新英文录音经过独立语音识别复核，具体差异与处理记录可在配音清单中查看；这不是人工听审保证。早期录音保留为展览历史。原始作品的作者与人机协作关系以各条来源为准。','Production: requirements and curatorial boundaries by Hongju Liu; design, programming, and narration production assisted by ChatGPT / Codex. Chinese narration uses Xiaoxiao. English uses the built-in synthetic Chatterbox Turbo voice, not a cloned person. New English audio has independent speech-recognition checks with differences and edits recorded in the narration manifest; this is not human listening certification. Earlier recordings remain part of exhibition history. Attribution of original works follows their source records.')}</p>`,'ABOUT / AUTHORITY & HISTORY');}

function updateUI(){document.body.dataset.presentation=String(touring||tourElapsed>=tourDuration);document.body.dataset.reducedMotion=String(reduced);const r=roomData.rooms[roomIndex];document.documentElement.lang=lang==='zh'?'zh-CN':'en';document.documentElement.style.setProperty('--accent',r.color);$('room-number').textContent=r.number;$('room-en').textContent=lang==='zh'?r.en:'TRINITY ACCORD / '+r.number;$('room-title').textContent=tx(r.title,r.en);$('room-title').classList.toggle('en-title',lang==='en');$('room-subtitle').textContent=tx(r.subtitle,r.subtitleEn||r.en);$('position-text').textContent=r.number+' / 06';$('work-count').textContent=r.exhibits.length;$('room-works').innerHTML=tx('作品与歌词','Exhibits')+' <span id="work-count">'+r.exhibits.length+'</span>';$('tour-text').textContent=touring?tx('暂停导览','Pause tour'):tourElapsed>=tourDuration?tx('重播导览','Replay tour'):tx(tourElapsed?'继续导览':'自动导览 · 9 分钟',tourElapsed?'Resume tour':'Auto tour · 9 min');$('language').textContent=tx('EN','中文');$('about').textContent=tx('关于本馆','About');$('help').textContent=tx('帮助','Help');$('verify-flaws').textContent=tx('验证瑕疵','Verify flaws');$('verify-flaws').hidden=roomIndex!==4;$('official').textContent=tx('原网站 ↗','Source site ↗');$('brand-sub').textContent=tx('文明记忆站 · 数字展馆','THE MEMORY STATION');$('motion').textContent=tx('减少动态','Reduce motion');$('motion').setAttribute('aria-pressed',String(reduced));$('hint').textContent=matchMedia('(pointer:fine)').matches?tx('滚轮前后行走 · 鼠标移动环顾 · 再点画作查看详情','SCROLL TO WALK · MOVE MOUSE TO LOOK · CLICK AGAIN FOR DETAILS'):tx('拖动环顾 · 点击靠近 · 再点查看详情','DRAG TO LOOK · TAP TO APPROACH · TAP AGAIN FOR DETAILS');$('guide-label').textContent=tx('中文导览 · AI 合成','ENGLISH GUIDE · AI VOICE');$('previous').disabled=roomIndex===0;$('next').disabled=roomIndex===5;if(!$('rooms').children.length){$('rooms').innerHTML=roomData.rooms.map((room,i)=>`<button data-room="${i}"><span class="nav-num">${room.number}</span><span class="nav-title"></span></button>`).join('');$('rooms').addEventListener('click',event=>{const b=event.target.closest('[data-room]');if(b)goRoom(Number(b.dataset.room));});}for(const [i,button] of [...$('rooms').children].entries()){const room=roomData.rooms[i];button.setAttribute('aria-current',String(i===roomIndex));button.setAttribute('aria-label',tx(room.title,room.en));button.querySelector('.nav-title').textContent=tx(room.short,room.shortEn);}updateStrip();}

function moveCamera(dest,target){
 armFootsteps();joystick?.reset();wheelWalk?.reset();keys.clear();
 const route=routeBetween(galleryLayout,camera.position,dest);if(!route)return;
 const direction=target.clone().sub(dest),endYaw=Math.atan2(-direction.x,-direction.z),endPitch=Math.atan2(direction.y,Math.hypot(direction.x,direction.z));
 if(reduced){camera.position.copy(dest);yaw=endYaw;pitch=endPitch;motion=null;return;}
 const startYaw=endYaw+Math.atan2(Math.sin(yaw-endYaw),Math.cos(yaw-endYaw));
 motion={start:camera.position.clone(),end:dest,route,startYaw,startPitch:pitch,endYaw,endPitch,time:performance.now(),duration:Math.max(500,routeLength(route)/WALK_SPEED*1000),walk:true};
}
function focusExhibit(id){
 const index=roomData.rooms.findIndex(r=>r.exhibits.includes(id));if(index<0)return;
 roomIndex=index;selectedExhibit=id;updateUI();history.replaceState(null,'','#'+roomData.rooms[index].id);
 if(!spatialReady)return;
 const mobile=innerWidth<650;resize();
 if(id==='physical-alpha'){
  loadCrystal?.();const p={x:galleryLayout.crystal.x,y:galleryLayout.crystal.baseY,z:galleryLayout.crystal.z};
  const view=observationView(.78,1.08,camera.fov,camera.aspect,mobile),d=Math.max(1.25,view.distance);
  moveCamera(new THREE.Vector3(p.x+.22,p.y+.38,p.z+d),new THREE.Vector3(p.x,p.y+.353-view.aimOffset,p.z));return;
 }
 const m=mounts.get(id);if(!m)return;
 const view=observationView((m.width||1.9)+.15,(m.height||1.7)+.66,camera.fov,camera.aspect,mobile,{height:innerHeight,top:$('room-label').getBoundingClientRect().bottom+14,bottom:viewingBottom()}),d=THREE.MathUtils.clamp(view.distance,2.2,6.3);
 moveCamera(new THREE.Vector3(m.x+Math.sin(m.angle)*d,m.y+.27,m.z+Math.cos(m.angle)*d),new THREE.Vector3(m.x,m.y+.27,m.z));
}
function approachExhibit(id){
 if(!spatialReady||approachedExhibit===id){showExhibit(id);return;}
 approachedExhibit=id;stopTour();focusExhibit(id);$('hover-label').hidden=true;
  const e=exhibits.get(id),sound=soundFor(e);
 if(sound)playTrack(sound,e,false);
 else if(musicItem){cancelMusic();$('music-bar').hidden=true;clearLyrics();syncMusic();}
}
function roomView(){
 approachedExhibit=null;if(!spatialReady)return;ensureRoomResources();
 const r=galleryLayout.rooms[roomIndex],door=galleryLayout.portals[roomIndex-1],x=door?.x||0,z=r.entryZ,y=floorAt(galleryLayout,{x,z})+galleryLayout.eyeHeight;
 moveCamera(new THREE.Vector3(x,y,z),new THREE.Vector3(x,roomIndex===3?y+1.6:y,roomIndex===0?20:z-12));
}
function waitingView(){if(!spatialReady)return;const r=galleryLayout.rooms[5];moveCamera(new THREE.Vector3(0,r.floor+galleryLayout.eyeHeight,galleryLayout.endZ+4.5),new THREE.Vector3(0,r.floor+galleryLayout.eyeHeight,galleryLayout.endZ-20));}

function updateStrip(){$('verify-flaws').hidden=roomIndex!==4;const r=roomData.rooms[roomIndex];if(!r.exhibits.includes(selectedExhibit))selectedExhibit=r.featuredExhibit||r.exhibits[0];const stripKey=lang+':'+r.id+':'+selectedExhibit;if($('exhibit-strip').dataset.key!==stripKey){$('exhibit-strip').dataset.key=stripKey;$('exhibit-strip').innerHTML=r.exhibits.map((id,i)=>`<button data-focus="${id}" aria-pressed="${id===selectedExhibit}"><small>${exhibits.get(id).ordinal?String(exhibits.get(id).ordinal).padStart(2,'0'):i+1}</small>${esc(title(exhibits.get(id)))}</button>`).join('');document.querySelectorAll('[data-focus]').forEach(b=>b.onclick=()=>approachExhibit(b.dataset.focus));}$('focus-art').textContent=tx('查看详情','View details');$('overview').textContent=tx('展厅全景','Room view');$('move-help').textContent=tx('左手移动 · 右手转身','Left: walk · right: turn');$('move-stick').setAttribute('aria-label',tx('左手摇杆移动，右手滑动自由转身','Left joystick moves relative to your view; swipe on the right to turn freely'));const e=exhibits.get(selectedExhibit),img=imageOf(e);$('look-help').textContent=tx('滑动转身','Swipe to turn');$('fallback-art').classList.toggle('waiting-view',roomIndex===5);$('fallback-art').innerHTML=`<span class="attached-label">${exhibitLabel(e,lang==='zh',!!soundFor(e)).split('\n').map((line,i)=>i?'<small>'+esc(line)+'</small>':'<strong>'+esc(line)+'</strong>').join('')}</span>`+(img?`<img loading="lazy" src="${esc(img)}" alt="${esc(title(e))}">`:`<div class="document-note"><strong>${esc(title(e))}</strong><p>${esc(tx(e.summary||e.text,e.summaryEn||e.textEn)||e.songTitle||'')}</p></div>`)+`<span class="fallback-title">${esc(title(e))}</span>`;$('fallback-art').onclick=()=>showExhibit(selectedExhibit);$('fallback-mode').textContent=tx('作品浏览模式 · 点击画作播放并显示歌词','Gallery mode · tap artwork to play with lyrics');}
function ensureRoomResources(){if(roomIndex>=3)prepareInspection();if(roomIndex===0||roomIndex===5)loadSky?.();}
function goRoom(i,keepTour=false){
 if(i<0||i>=roomData.rooms.length)return;if(!keepTour)stopTour();closePanel();roomIndex=i;selectedExhibit=roomData.rooms[i].featuredExhibit||roomData.rooms[i].exhibits[0];hovered=null;$('hover-label').hidden=true;updateUI();history.replaceState(null,'','#'+roomData.rooms[i].id);ensureRoomResources();
 if(spatialReady&&!keepTour){if(i===5)waitingView();else roomView();if(motion){motion.walk=false;motion.duration=reduced?0:1400;}}
}

let tourInspectionStarted=false,tourLookChanged=false,tourShotIndex=0;
let tourElapsed=0,tourLast=0,tourStep=-1,tourMusicStarted=false,guideSound=true,flawIndex=-1;
let guideStop=-1,guideResume=null,inspectionRequest=0,inspectionTimer=null,inspectionPreloaded=false;
let microscopeMotion=null,guideRate=1,guideRecovery=false;
const recordedGuide=createRecordedGuide($('narration'),{
 onCaption(text,language){if(language&&language!==lang)return;$('caption-text').textContent=text;$('tour-caption').hidden=!text;},
 onState(state){
  if(['blocked','error'].includes(state))guideRecovery=true;
  if(['playing','muted','idle'].includes(state))guideRecovery=false;
  syncAudioHold();if(roomData)updateTourStatus();
 }
});
const musicPlayback=createMusicPlayback($('music'),{onState(){syncAudioHold();if(roomData)updateTourStatus();}});
function audioWaiting(){return (guideSound&&['loading','blocked','error'].includes(recordedGuide.state))||musicPlayback.waiting;}
function syncAudioHold(){
 const now=performance.now();
 if(motion){if(touring&&audioWaiting())motion.audioPausedAt??=now;else if(motion.audioPausedAt!==undefined){motion.time+=now-motion.audioPausedAt;delete motion.audioPausedAt;}}
 tourLast=now;
}
function cancelMusic(){playRequest++;musicPlayback.stop();}
function resumeAudio(){
 if(musicPlayback.recovering||musicPlayback.state==='paused'){
  const track=exhibits.get(musicItem);if(track)playTrack(track,exhibits.get(musicArtworkId)||track,false,touring);
 }else {guideSound=true;if(recordedGuide.state==='error')playGuide(guideStop,recordedGuide.currentTime);else recordedGuide.setMuted(false);}
}
function dismissAudio(){
 stopTour();cancelMusic();$('music-bar').hidden=true;clearLyrics();updateTourStatus();
}
function silenceGuide(){recordedGuide.stop();}
function playGuide(index,offset=0){
 const track=index<0?initialData.guides.inspectionTracks?.find(t=>t.flaw===flawIndex&&t.language===lang):initialData.guides.tracks.find(t=>t.stop===index&&t.language===lang);if(!track)return;
 guideStop=index;recordedGuide.play(track,{muted:!guideSound,offset,playbackRate:guideRate});
}
function prepareInspection(){
 loadCrystal?.();microscopeMotion?.prepare().catch(()=>{});
 if(!inspectionPreloaded){inspectionPreloaded=true;for(const item of publicFlaws.items){const image=new Image();image.src=item.file;}}
}
function closeFlaws(){inspectionRequest++;clearTimeout(inspectionTimer);microscopeMotion?.stop();flawIndex=-1;$('flaw-view').hidden=true;$('flaw-view').replaceChildren();}
function showFlawPhoto(index,request){
 if(request!==inspectionRequest)return;
 const item=publicFlaws.items[index],host=$('flaw-view');host.hidden=false;
 host.innerHTML=`<div class="flaw-top"><strong>${tx('公开瑕疵','Public flaw')} ${index+1} / 3</strong><button id="flaw-close" aria-label="${tx('退出查验','Close inspection')}">×</button></div><img class="flaw-photo" src="${item.file}" alt="${tx('未经叠加的原始显微照片','Unaltered original microscope photograph')} ${index+1}"><div class="flaw-buttons"><button id="flaw-prev">← ${tx('上一处','Previous')}</button><a href="${item.file}" target="_blank" rel="noopener">${tx('原图','Original')} ↗</a><button id="flaw-next">${tx('下一处','Next')} →</button></div><details><summary>${tx('照片来源与证据说明','Sources and evidence')}</summary><p>${esc(flawReading[lang])}</p><p>${tx('显微镜动作发生在虚拟展厅，定位为示意。上方照片保持原始文件与画面。','The microscope moves in the virtual gallery with illustrative positioning. The photograph above retains its original file and image.')}</p><a href="https://ordinals.com/inscription/${publicFlaws.covenantInscription}" target="_blank" rel="noopener">${tx('瑕疵之约原铭文','Covenant inscription')} ↗</a> · <a href="${publicFlaws.archiveUrl}" target="_blank" rel="noopener">${tx('公开证据包','Public evidence archive')} ↗</a> · <a href="./data/public-flaws.json" target="_blank" rel="noopener">${tx('完整哈希','Full hashes')} ↗</a></details>`;
 $('flaw-prev').onclick=()=>showFlaw((index+2)%3);$('flaw-next').onclick=()=>showFlaw((index+1)%3);$('flaw-close').onclick=()=>{if(touring)closeFlaws();else {silenceGuide();closeFlaws();updateTourStatus();}};
 const photo=host.querySelector('.flaw-photo');
 let began=false;const begin=()=>{if(!began&&request===inspectionRequest){began=true;if(!touring){playGuide(-1);}else{$('caption-text').textContent='';$('tour-caption').hidden=true;}}};
 photo.onload=begin;photo.onerror=()=>{if(request===inspectionRequest)toast(tx('照片未载入，请点击原图重试。','Photo unavailable. Open the original to retry.'));};
 if(photo.complete&&photo.naturalWidth)begin();
}
async function showFlaw(index=0,automatic=false){
 if(!automatic){stopTour();closePanel();cancelMusic();$('music-bar').hidden=true;clearLyrics();}else {silenceGuide();closeFlaws();}
 const request=++inspectionRequest;flawIndex=(index+3)%3;index=flawIndex;
 $('tour-caption').hidden=false;$('caption-text').textContent=tx('垂直升起虚拟显微镜，对准水晶…','Lifting the virtual microscope to the crystal…');
 const crystal=spatialReady?await loadCrystal?.():null;if(request!==inspectionRequest)return;
 if(!crystal||!microscopeMotion){showFlawPhoto(index,request);return;}
 focusExhibit('physical-alpha');if(motion)motion.duration=reduced?0:900;
 inspectionTimer=setTimeout(()=>{if(request!==inspectionRequest)return;
  microscopeMotion.start(crystal,index,{reduced,onComplete:()=>showFlawPhoto(index,request),onError:()=>showFlawPhoto(index,request)});
 },reduced?0:950);
}
function stopTour(){
 const active=touring,hadEnded=tourElapsed>=tourDuration;if(hadEnded){tourElapsed=0;guideResume=null;}if(active)guideResume={stop:tourStep,time:recordedGuide.currentTime,language:lang};
 touring=false;clearTimeout(tourTimer);silenceGuide();closeFlaws();$('tour-caption').hidden=true;
 if(active){motion=null;cancelMusic();$('music-bar').hidden=true;clearLyrics();}
 if(roomData&&(active||hadEnded))updateUI();updateTourStatus();
}
function updateTourStatus(){
 if(!$('tour-status'))return;$('tour-status').hidden=!touring&&tourElapsed===0&&flawIndex<0;
 $('tour-progress').textContent=(flawIndex>=0&&!touring?tx('瑕疵查验','Flaw inspection'):time(tourElapsed)+' / 9:00')+(touring||flawIndex>=0?'':tourElapsed>=tourDuration?tx(' · 已完成',' · complete'):tx(' · 暂停',' · paused'));
 const blocked=['blocked','error'].includes(recordedGuide.state);
 const songWaiting=musicPlayback.recovering;
 const waiting=songWaiting||((touring||flawIndex>=0)&&guideSound&&guideRecovery);
 const prompt=$('guide-audio-prompt'),state=songWaiting?musicPlayback.state:recordedGuide.state;
 if(waiting&&!prompt.open)prompt.showModal();else if(!waiting&&prompt.open)prompt.close();
 const loading=state==='loading';
 $('guide-audio-message').textContent=loading?tx('正在连接声音，播放进度已暂停…','Connecting audio. Playback is waiting…'):state==='error'?tx('声音加载失败，播放进度已暂停。请点击重试。','Audio could not load. Playback is paused. Tap to retry.'):tx('浏览器暂停了声音。点击下方按钮，从这里继续播放。','Your browser paused the sound. Tap below to continue from here.');
 $('guide-audio-start').disabled=loading;
 $('guide-audio-start').textContent=loading?tx('正在加载…','Loading…'):state==='error'?tx('点击重试并继续播放','Retry and continue playback'):tx('点击继续播放','Tap to continue playback');
 $('guide-audio-dismiss').textContent=tx('停止播放，自由参观','Stop playback and explore');
 $('enable-guide-sound').textContent=recordedGuide.state==='error'?tx('重试配音','Retry audio'):guideSound&&!blocked?tx('静音','Mute'):tx('开启声音','Enable sound');
 $('tour-restart').textContent=tx('重来','Restart');$('guide-speed').textContent=guideRate.toFixed(guideRate===1?1:guideRate===1.25?2:1)+'×';$('guide-speed').setAttribute('aria-label',tx('调整解说语速','Narration speed'));
}
function enterTourStop(position){
 const s=position.stop;tourStep=position.index;tourMusicStarted=false;tourInspectionStarted=false;tourLookChanged=false;tourShotIndex=0;silenceGuide();closeFlaws();cancelMusic();$('music-bar').hidden=true;clearLyrics();
 goRoom(s.room,true);if(position.index===0||s.room===3)roomView();else if(position.index===tourStops.length-1){selectedExhibit=s.exhibit;updateStrip();waitingView();}else focusExhibit(s.exhibit);if(motion)motion.duration=reduced?0:Math.min(14000,Math.max(1800,motion.duration));
 if(s.musicAt===undefined||position.local<s.musicAt){
  const offset=guideResume?.stop===position.index&&guideResume.language===lang?guideResume.time:0;playGuide(position.index,offset);
 }
 guideResume=null;updateTourStatus();
}
function tourTick(now){
 if(!touring)return;const delta=tourLast?Math.min((now-tourLast)/1000,1):0;tourLast=now;tourElapsed=Math.min(tourDuration,tourElapsed+(audioWaiting()?0:delta));
 const p=tourPosition(tourElapsed);if(!p){stopTour();tourElapsed=tourDuration;guideResume=null;updateUI();updateTourStatus();return;}
 if(tourStep!==p.index)enterTourStop(p);
 if(p.stop.musicAt!==undefined&&p.local>=p.stop.musicAt&&!tourMusicStarted){tourMusicStarted=true;silenceGuide();const e=exhibits.get(p.stop.musicExhibit||p.stop.exhibit),sound=soundFor(e);if(sound){playTrack(sound,exhibits.get(p.stop.exhibit),false,true);}}
 if(p.index===0&&p.local>=12&&!tourLookChanged){tourLookChanged=true;if(spatialReady)moveCamera(camera.position.clone(),new THREE.Vector3(0,camera.position.y,-12));}
 if(p.stop.inspectAt!==undefined&&p.local>=p.stop.inspectAt&&!tourInspectionStarted){tourInspectionStarted=true;showFlaw(p.stop.inspectFlaw,true);}
 if(p.stop.inspectUntil!==undefined&&p.local>=p.stop.inspectUntil&&flawIndex>=0)closeFlaws();
 if(p.stop.cameraShots&&tourShotIndex<p.stop.cameraShots.length&&p.local>=p.stop.cameraShots[tourShotIndex].at){const shot=p.stop.cameraShots[tourShotIndex++];focusExhibit(shot.exhibit);if(motion)motion.duration=reduced?0:Math.min(10500,motion.duration);}
 recordedGuide.paint();updateTourStatus();tourTimer=setTimeout(()=>tourTick(performance.now()),200);
}
function startTour(automatic=false){if(touring){if(!automatic&&audioWaiting()){resumeAudio();return;}stopTour();return;}closePanel();closeFlaws();if(!automatic)guideSound=true;if(tourElapsed>=tourDuration)tourElapsed=0;touring=true;tourLast=0;tourStep=-1;updateUI();tourTick(performance.now());}
function switchGuideLanguage(){
 languagePreference.choose(lang==='zh'?'en':'zh');const u=new URL(location.href);u.searchParams.set('lang',languagePreference.language);history.replaceState(null,'',u);applyGuideLanguage(languagePreference.language);
}
function applyGuideLanguage(next){
 if(lang===next)return;
 const manualFlaw=flawIndex;silenceGuide();lang=next;updateUI();refreshWallLabels();
 guideResume=null;if(touring){const p=tourPosition(tourElapsed);if(p){tourElapsed-=p.local;tourLast=performance.now();enterTourStop(tourPosition(tourElapsed));}}
 else if(manualFlaw>=0)showFlaw(manualFlaw);
 updateTourStatus();
}
function toggleGuideSound(){
 if(recordedGuide.state==='error'){guideSound=true;playGuide(guideStop,recordedGuide.currentTime);return;}
 if(['blocked','muted'].includes(recordedGuide.state)||!guideSound)guideSound=true;else guideSound=false;
 recordedGuide.setMuted(!guideSound);updateTourStatus();
}
function cycleGuideSpeed(){const rates=[1,1.1,1.25,1.4];guideRate=rates[(rates.indexOf(guideRate)+1)%rates.length];recordedGuide.setRate(guideRate);updateTourStatus();}
function showHelp(){stopTour();panel(`<h2>${tx('如何参观','How to visit')}</h2><p>${tx('默认九分钟自动导览，会移动镜头、靠近作品、播放歌曲片段并引导查看一处水晶瑕疵，其余两处留给自由参观。底部可暂停、继续或重新开始。如果声音被浏览器拦截，导览会暂停；每次被拦截都会保留中央提示，点击继续播放后从原位置恢复。解说字幕每次只显示一小段，语速按钮可以调整播放速度。','The default nine-minute tour moves the camera, approaches artworks, plays song excerpts and introduces one crystal flaw; two more remain available for free exploration. Pause, resume or restart below. If your browser blocks sound, the tour waits. Each interruption keeps a central prompt visible. Tap to continue from the same position. Short captions follow the recording, and the speed button adjusts narration.')}</p><ul><li>${tx('电脑：移动鼠标即可环顾，无需按住或拖动；滚轮前后，W/A/S/D 行走，方向键或 Q/E 仍可转身。','Desktop: move the mouse to look without holding a button; scroll forward/back, W/A/S/D to walk, and arrow keys or Q/E still turn.')}</li><li>${tx('手机：左侧摇杆移动，右侧滑动转身。','Mobile: left joystick to walk, right pad to turn.')}</li><li>${tx('点击画作靠近并听歌；再点一次或查看详情可读全文。音符标牌表示附带音乐。','Select art to approach and hear its music; select again or View details to read. Musical notes mark works with audio.')}</li><li>${tx('CC 开关歌词，箭头展开歌词；英文逐词同步，中文逐句显示。','CC toggles lyrics; the arrow expands them. English highlights word by word, with Chinese lines below.')}</li><li>${tx('点击水晶后选择验证瑕疵，显微镜先在展厅中靠近水晶，再显示没有叠加物的原始显微照片，可切换三处。退出或开始行走时，显微镜自动收起。','Select the crystal, then Verify flaws: a microscope approaches it in the gallery, followed by an unobstructed original photograph. Browse three flaws. Close inspection or walk away to put the microscope away.')}</li><li>${tx('底部厅名可直接切换；作品与歌词可浏览本厅全部作品。手动行走和选厅会暂停自动导览。','Room names jump directly between rooms; Exhibits lists each room’s works. Walking or selecting a room pauses the tour.')}</li><li>${tx('中文 / EN 切换介绍、导览、帮助与展览说明；减少动态可减少镜头与装置动画。Esc 关闭查验或详情并暂停导览。','中文 / EN changes introductions, narration, help and commentary. Reduce motion limits camera and installation animation. Esc closes inspection or details and pauses the tour.')}</li></ul>`,tx('操作帮助','HELP'));}

function textTexture(lines,{color='#233b47',size=84,width=2048,height=1536,background='#ecece6'}={}){const c=document.createElement('canvas');c.width=width;c.height=height;const ctx=c.getContext('2d');ctx.fillStyle=background;ctx.fillRect(0,0,width,height);ctx.fillStyle=color;ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=`400 ${size}px "Helvetica Neue", "Microsoft YaHei", sans-serif`;lines.forEach((l,i)=>ctx.fillText(l,width/2,height/2+(i-(lines.length-1)/2)*size*1.8,width-90));const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;return tex;}

function wallLabelTexture(e){
 const c=document.createElement('canvas');c.width=1024;c.height=300;const ctx=c.getContext('2d');
 const metal=ctx.createLinearGradient(0,0,0,300);metal.addColorStop(0,'#b4c1c7');metal.addColorStop(.23,'#d1d9dd');metal.addColorStop(.48,'#a3b1b9');metal.addColorStop(.74,'#c5cfd4');metal.addColorStop(1,'#8d9da7');ctx.fillStyle=metal;ctx.fillRect(0,0,1024,300);
 for(let y=2;y<300;y+=3){ctx.fillStyle=y%2?'#ffffff0b':'#172c3809';ctx.fillRect(0,y,1024,1);}
 ctx.strokeStyle='#edf5f8';ctx.lineWidth=2;ctx.strokeRect(5,5,1014,290);
 const lines=exhibitLabel(e,lang==='zh',!!soundFor(e)).split('\n');ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillStyle='#112531';
 for(let i=0;i<lines.length;i++){let size=i?62:112;do{ctx.font=`${i?500:650} ${size}px "Helvetica Neue", "Microsoft YaHei", sans-serif`;if(ctx.measureText(lines[i]).width<=940)break;size--;}while(size>38);ctx.fillText(lines[i],512,lines.length===1?150:i?230:104);}
 const texture=new THREE.CanvasTexture(c);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=Math.min(renderer?.capabilities.getMaxAnisotropy()||1,16);return texture;
}

function canonicalText(e){if(e.wallLinesEn)return textTexture(tx(e.wallLinesZh,e.wallLinesEn),{size:32,width:1024,height:768});return textTexture([e.title,e.en,'BITCOIN / '+e.number,e.quote],{size:39,width:1024,height:768,background:'#ecece6',color:'#233b47'});}
function refreshWallLabels(){for(const [id,plane] of canonicalPanels){plane.material.map.dispose();plane.material.map=documentTexture(exhibits.get(id));plane.material.needsUpdate=true;}for(const [id,label] of wallLabels){label.material.map?.dispose();label.material.map=wallLabelTexture(exhibits.get(id));label.material.needsUpdate=true;}}

function documentTexture(e){
 if(e.id.startsWith('canon-')||e.id==='authority-boundary')return createDocumentPanel(e,lang);
 if(e.wallLinesZh)return textTexture(tx(e.wallLinesZh,e.wallLinesEn),{size:58,width:1536,height:1152,color:'#263940',background:'#edf0e8'});
 const heading=title(e),text=e.ordinal?e.songTitle||'':tx(e.summary||e.text,e.summaryEn||e.textEn)||e.quote||'';
 const lines=[heading];let line='';
 for(const word of (lang==='zh'?[...text]:text.split(' '))){const candidate=line+(lang==='zh'||!line?'':' ')+word;if(candidate.length>(lang==='zh'?22:46)){lines.push(line);line=word;}else line=candidate;if(lines.length>=5)break;}
 if(line&&lines.length<6)lines.push(line);
 return textTexture(lines,{size:44,width:1536,height:1152,color:'#263940',background:'#edf0e8'});
}
function addExhibit(e,x,z,angle,color,y=galleryLayout.exhibitCentreHeight){
 const img=imageOf(e),config=galleryLayout.rooms.flatMap(r=>r.exhibits).find(m=>m.id===e.id),width=config?.displayWidth||1.9,height=config?.displayHeight||(img?1.7:1.425);
 // Mount the work 15 mm in front of the wall, independently of the old baked mounts.
 const wallX=x;mounts.set(e.id,{x:wallX,y,z,angle,width,height});
 const group=new THREE.Group();group.position.set(wallX,y,z);group.rotation.y=angle;scene.add(group);
 const plane=new THREE.Mesh(new THREE.PlaneGeometry(width,height),new THREE.MeshBasicMaterial({color:'#ffffff',toneMapped:false}));plane.position.z=.005;group.add(plane);plane.userData.exhibit=e.id;targets.push(plane);
 const label=makeWallPlaque(group,wallLabelTexture(e));wallLabels.set(e.id,label);label.userData.exhibit=e.id;targets.push(label);
 if(!img){for(const child of group.children)if(child!==plane)child.position.y+=Math.max(0,(height-1.425)/2);makeWallFrame(group,width,height);plane.material.map=documentTexture(e);canonicalPanels.set(e.id,plane);return;}
 let frame=makeWallFrame(group,1.9,1.7);frame.frame.visible=false;
 plane.material.map=textTexture([title(e),tx('正在载入原图','LOADING ORIGINAL IMAGE')],{size:26,width:512,height:384});
 imageJobs.add(async()=>{const bytes=await fetchBytes(img);const url=URL.createObjectURL(new Blob([bytes]));try{
  const texture=await new THREE.TextureLoader().loadAsync(url);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=Math.min(renderer.capabilities.getMaxAnisotropy(),16);
  const ratio=texture.image.width/texture.image.height,w=Math.min(1.9,1.7*ratio),h=w/ratio;
  plane.material.map.dispose();plane.material.map=texture;plane.geometry.dispose();plane.geometry=new THREE.PlaneGeometry(w,h);plane.material.needsUpdate=true;
  frame.dispose();frame=makeWallFrame(group,w,h);
 }finally{URL.revokeObjectURL(url);}},()=>Math.abs(z-camera.position.z)).catch(()=>{plane.material.map.dispose();plane.material.map=textTexture([title(e),tx('原图暂未载入 · 点击重试','IMAGE UNAVAILABLE · OPEN DETAILS')],{size:26,width:512,height:384});plane.material.needsUpdate=true;});
}

async function initWorld(){scene=new THREE.Scene();scene.background=new THREE.Color('#000000');scene.fog=new THREE.Fog('#18293d',100,210);camera=new THREE.PerspectiveCamera(innerWidth<650?76:66,innerWidth/innerHeight,.06,220);camera.position.set(0,1.65,-2);yaw=0;camera.rotation.order='YXZ';camera.rotation.y=yaw;renderer=new THREE.WebGLRenderer({canvas:$('world'),antialias:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,2.5));renderer.setSize(innerWidth,innerHeight);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.0;raycaster=new THREE.Raycaster();mouse=new THREE.Vector2();scene.add(new THREE.HemisphereLight('#eff5ff','#536676',.85));
 microscopeMotion=createMicroscopeMotion(scene,camera);scene.environment=crystalEnvironment(renderer).texture;scene.environmentIntensity=.6;renderer.transmissionResolutionScale=1;
 for(const side of [-1,1]){const spot=new THREE.SpotLight(side<0?'#fff0d9':'#c5e9ff',22,9,.68,1,2);spot.position.set(side*2.8,5,-3);spot.target.position.set(side*4.25,galleryLayout.exhibitCentreHeight,-3);scene.add(spot,spot.target);accentLights.push({spot,side});}
 const preview=createPreviewHall(galleryLayout);scene.add(preview.group);architecturalOccluder=preview.group;
 const enhance=async()=>{const notice=$('scene-status');notice.hidden=false;notice.querySelector('span').textContent=tx('展厅已打开，正在补齐高清细节…','Gallery open; adding architectural detail…');notice.querySelector('button').hidden=true;
  try{const bytes=await fetchBytes('./assets/gallery/memory-gallery.glb');const gltf=await new GLTFLoader().parseAsync(bytes,'./assets/gallery/');if(galleryLayout.schema!=='trinity-museum.gallery-layout.v2'){removeLegacyWallMounts(gltf.scene);removeLegacyChapterPosts(gltf.scene);clearBakedWallShadows(gltf.scene);gltf.scene.scale.y=galleryLayout.dimensions.height/(galleryLayout.architectureBaseHeight||4.8);}scene.add(gltf.scene);architecturalOccluder=gltf.scene;gltf.scene.traverse(o=>{if(o.isMesh){if(o.name.startsWith('Luminous')){o.material=o.material.clone();sculptures.push({light:o.material,base:o.material.emissiveIntensity});}o.frustumCulled=true;for(const m of Array.isArray(o.material)?o.material:[o.material]){if(m.name==='Brushed titanium'){m.roughness=.32;m.metalness=.8;}if(m.name==='Satin aluminium frame'){m.roughness=.26;m.metalness=.85;}if(m.name==='Porcelain / satin mineral'){m.roughness=.42;m.metalness=.04;}}for(const m of Array.isArray(o.material)?o.material:[o.material])if(m.map)m.map.anisotropy=Math.min(renderer.capabilities.getMaxAnisotropy(),16);}});preview.dispose();notice.hidden=true;}
  catch(error){console.warn('Base gallery remains available',error);notice.querySelector('span').textContent=tx('当前为轻量展厅，高清细节暂未下载。','Lightweight gallery; architectural detail is not downloaded yet.');notice.querySelector('button').hidden=false;}
 };
 $('retry-scene').onclick=enhance;requestAnimationFrame(()=>enhance());
 for(const r of galleryLayout.rooms){const light=new THREE.PointLight('#e3f4ff',r.id==='waiting'?6:18,15,2);light.position.set(0,r.floor+r.height-.5,-r.start-r.length/2);scene.add(light);}
 let crystalPromise=null;loadCrystal=()=>crystalPromise ||= fetchBytes('./assets/crystal/core-object-alpha.glb').then(bytes=>new GLTFLoader().parseAsync(bytes,'./assets/crystal/')).then(crystal=>{const cr=galleryLayout.rooms.find(r=>r.id==='material');crystal.scene.position.set(galleryLayout.crystal.x,galleryLayout.crystal.baseY,galleryLayout.crystal.z);crystal.scene.scale.setScalar(2);scene.add(crystal.scene);floatingCrystal=crystal.scene;crystalAura=addCrystalAura(scene,crystal.scene.position,2);addCrystalLighting(scene,crystal.scene.position,2);crystal.scene.traverse(o=>{if(o.isMesh){o.userData.exhibit='physical-alpha';targets.push(o);}});refineCrystal(crystal.scene);const pick=new THREE.Mesh(new THREE.BoxGeometry(.29,.40,.09),new THREE.MeshBasicMaterial({visible:false}));pick.position.y=.1765;pick.userData.exhibit='physical-alpha';crystal.scene.add(pick);targets.push(pick);return floatingCrystal;}).catch(err=>{crystalPromise=null;console.warn('Crystal available from its source/detail panel',err);return null;});
 exterior=addOpenSpace(scene,targets,sculptures,initialData.stars,galleryLayout);exterior.update(camera,renderer.getPixelRatio());loadSky=()=>exterior.loadSky();loadSky();
 // Invisible picking floor, separate from the Blender-rendered stone surface.
 floor=createSpatialShell(galleryLayout,{picking:true}).group;scene.add(floor);
 for(const r of galleryLayout.rooms)for(const m of r.exhibits)addExhibit(exhibits.get(m.id),m.x,m.z,m.angle,roomData.rooms.find(x=>x.id===r.id).color,m.y);
 spatialReady=true;resize();window.addEventListener('resize',resize);bindNavigation();lastTime=performance.now();animationFrame=requestAnimationFrame(animate);}
function viewingBottom(){return innerHeight-parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--dock-height')||'180')-206;}
function resize(){if(!renderer)return;const fit=galleryCamera(innerWidth,innerHeight,$('room-label').getBoundingClientRect().bottom+14,viewingBottom());camera.fov=fit.fov;camera.aspect=innerWidth/innerHeight;camera.setViewOffset(innerWidth,innerHeight,0,fit.offsetY,innerWidth,innerHeight);camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);}
function setRay(ev){const rect=$('world').getBoundingClientRect();mouse.set((ev.clientX-rect.left)/rect.width*2-1,-(ev.clientY-rect.top)/rect.height*2+1);raycaster.setFromCamera(mouse,camera);}
function visibleHit(hit){if(!hit)return false;const wall=architecturalOccluder&&raycaster.intersectObject(architecturalOccluder,true)[0];return !wall||hit.distance<=wall.distance+.035;}
function bindNavigation(){
 const c=$('world'),finePointer=matchMedia('(pointer:fine)').matches;let desktopLast=null;
 wheelWalk=createWheelWalk(c,()=>{armFootsteps();motion=null;approachedExhibit=null;stopTour();});
 const updateHover=e=>{setRay(e);const hit=raycaster.intersectObjects(targets,false)[0];hovered=visibleHit(hit)&&hit.distance<32?hit.object.userData.exhibit:null;$('hover-label').hidden=!hovered;if(hovered)$('hover-label').textContent=title(exhibits.get(hovered))+(approachedExhibit===hovered?tx(' · 点击查看详情',' · CLICK FOR DETAILS'):tx(' · 点击靠近',' · CLICK TO APPROACH'));c.style.cursor=hovered?'pointer':finePointer?'default':'grab';};
 const followDesktopMouse=e=>{if(!finePointer||e.pointerType!=='mouse')return false;const rect=c.getBoundingClientRect();if(!desktopLast){desktopLast={x:e.clientX,y:e.clientY};return true;}const dx=e.clientX-desktopLast.x,dy=e.clientY-desktopLast.y;desktopLast={x:e.clientX,y:e.clientY};const nx=(e.clientX-rect.left-rect.width/2)/(rect.width/2),ny=(e.clientY-rect.top-rect.height/2)/(rect.height/2),radius=Math.hypot(nx,ny);if(radius<=.12||Math.abs(dx)+Math.abs(dy)<.5)return true;const edge=Math.min(1,(radius-.12)/.88),gain=.38+.32*edge;wheelWalk?.reset();approachedExhibit=null;armFootsteps();if(touring)stopTour();closeFlaws();motion=null;({yaw,pitch}=turnView(yaw,pitch,dx*gain,dy*gain*.85,innerWidth));camera.rotation.y=yaw;camera.rotation.x=pitch;return true;};
 c.addEventListener('pointerenter',e=>{if(finePointer&&e.pointerType==='mouse')desktopLast={x:e.clientX,y:e.clientY};});
 c.addEventListener('pointerdown',e=>{if(drag||e.button!==0)return;wheelWalk.reset();armFootsteps();stopTour();closeFlaws();const desktop=finePointer&&e.pointerType==='mouse';drag={x:e.clientX,y:e.clientY,lastX:e.clientX,lastY:e.clientY,moved:0,pointer:e.pointerId,desktop};if(!desktop)c.setPointerCapture(e.pointerId);motion=null;});
 c.addEventListener('pointermove',e=>{const desktop=finePointer&&e.pointerType==='mouse';if(desktop){if(drag&&e.pointerId===drag.pointer){const dx=e.clientX-drag.lastX,dy=e.clientY-drag.lastY;drag.moved+=Math.abs(dx)+Math.abs(dy);if(drag.moved>=8)approachedExhibit=null;drag.lastX=e.clientX;drag.lastY=e.clientY;}followDesktopMouse(e);updateHover(e);return;}if(drag&&e.pointerId===drag.pointer){let dx=e.clientX-drag.lastX,dy=e.clientY-drag.lastY;drag.moved+=Math.abs(dx)+Math.abs(dy);if(drag.moved>=8)approachedExhibit=null;({yaw,pitch}=turnView(yaw,pitch,dx,dy,innerWidth));drag.lastX=e.clientX;drag.lastY=e.clientY;}else updateHover(e);});
 c.addEventListener('pointerup',e=>{if(drag&&e.pointerId!==drag.pointer)return;if(drag&&drag.moved<8){setRay(e);const hit=raycaster.intersectObjects(targets,false)[0];if(visibleHit(hit)&&hit.distance<32)approachExhibit(hit.object.userData.exhibit);else{const ground=raycaster.intersectObject(floor,true)[0];if(visibleHit(ground)&&ground.distance<28){approachedExhibit=null;stopTour();const p=ground.point;p.y=floorAt(galleryLayout,p)+galleryLayout.eyeHeight;if(isWalkable(galleryLayout,p))moveCamera(p,p.clone().add(new THREE.Vector3(-Math.sin(yaw),Math.tan(pitch),-Math.cos(yaw))));}}}drag=null;});
 for(const type of ['pointercancel','lostpointercapture'])c.addEventListener(type,()=>drag=null);
 c.addEventListener('pointerleave',()=>{$('hover-label').hidden=true;desktopLast=null;if(drag?.desktop)drag=null;});$('hover-label').onclick=()=>hovered&&approachExhibit(hovered);
 const look=$('look-pad');let lookPointer=null,lastLook;
 look.addEventListener('pointerdown',e=>{if(lookPointer!==null)return;e.preventDefault();wheelWalk?.reset();approachedExhibit=null;armFootsteps();stopTour();motion=null;lookPointer=e.pointerId;lastLook={x:e.clientX,y:e.clientY};look.setPointerCapture(e.pointerId);});
 look.addEventListener('pointermove',e=>{if(e.pointerId!==lookPointer)return;e.preventDefault();({yaw,pitch}=turnView(yaw,pitch,e.clientX-lastLook.x,e.clientY-lastLook.y,innerWidth));lastLook={x:e.clientX,y:e.clientY};});
 for(const type of ['pointerup','pointercancel','lostpointercapture'])look.addEventListener(type,e=>{if(e.pointerId===lookPointer)lookPointer=null;});
 window.addEventListener('keydown',e=>{if($('panel').open||/INPUT|BUTTON|A|TEXTAREA/.test(document.activeElement?.tagName))return;if(['w','a','s','d','q','e','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();wheelWalk?.reset();approachedExhibit=null;armFootsteps();keys.add(e.key);motion=null;stopTour();}});window.addEventListener('keyup',e=>keys.delete(e.key));window.addEventListener('blur',()=>{keys.clear();desktopLast=null;});}

function animate(now){const dt=document.hidden?0:frameSeconds(now,lastTime);lastTime=now;let side=0,walking=!!motion?.walk&&!document.hidden&&!$('panel').open;if(motion&&touring&&audioWaiting())motion.audioPausedAt??=now;if(motion&&!document.hidden&&!$('panel').open&&!(touring&&audioWaiting())){const t=motion.duration===0?1:Math.min((now-motion.time)/motion.duration,1),v=motion.walk?t:t*t*(3-2*t);if(motion.route){const p=routePoint(motion.route,v),from=motion.start.y-floorAt(galleryLayout,motion.start),to=motion.end.y-floorAt(galleryLayout,motion.end);camera.position.set(p.x,floorAt(galleryLayout,p)+THREE.MathUtils.lerp(from,to,v),p.z);}else camera.position.lerpVectors(motion.start,motion.end,v);if(motion.route&&motion.walk&&routeLength(motion.route)>3&&v<.83){const a=routePoint(motion.route,v),b=routePoint(motion.route,Math.min(1,v+.02)),heading=Math.atan2(-(b.x-a.x),-(b.z-a.z));yaw+=Math.atan2(Math.sin(heading-yaw),Math.cos(heading-yaw))*Math.min(1,dt*3);}else {const aim=motion.endYaw??0;yaw+=Math.atan2(Math.sin(aim-yaw),Math.cos(aim-yaw))*Math.min(1,dt*4);if(t===1)yaw=aim;}pitch=THREE.MathUtils.lerp(motion.startPitch,motion.endPitch??0,v);if(t===1)motion=null;}else if(!document.hidden&&!$('panel').open){const wheelStep=wheelWalk?.consume(WALK_SPEED*dt)||0;const forward=(keys.has('w')||keys.has('ArrowUp')?1:0)-(keys.has('s')||keys.has('ArrowDown')?1:0)+(joystick?.state.y||0)+(dt?wheelStep/(WALK_SPEED*dt):0);side=(keys.has('d')?1:0)-(keys.has('a')?1:0)+(joystick?.state.x||0);walking=Math.abs(forward)+Math.abs(side)>.02;yaw+=((keys.has('ArrowLeft')||keys.has('q')?1:0)-(keys.has('ArrowRight')||keys.has('e')?1:0))*TURN_SPEED*dt;const v=travelVector(side,forward,yaw);const step=constrainStep(galleryLayout,camera.position,{x:camera.position.x+v.x*dt*WALK_SPEED,z:camera.position.z+v.z*dt*WALK_SPEED});camera.position.x=step.x;camera.position.z=step.z;if(walking)camera.position.y=THREE.MathUtils.lerp(camera.position.y,floorAt(galleryLayout,step)+galleryLayout.eyeHeight,Math.min(1,dt*8));}

 if(floatingCrystal){floatCrystal(floatingCrystal,crystalAura,now,reduced,galleryLayout.crystal.baseY,2);}headLean=reduced?0:THREE.MathUtils.lerp(headLean,-THREE.MathUtils.clamp(side,-1,1)*.018,Math.min(dt*8,1));camera.rotation.y=yaw;camera.rotation.x=pitch;camera.rotation.z=headLean;updateFootsteps(walking);for(const {spot,side} of accentLights){const nearest=[...mounts.values()].filter(m=>Math.sign(m.x)===side).sort((a,b)=>Math.abs(a.z-camera.position.z)-Math.abs(b.z-camera.position.z))[0];if(nearest){spot.position.set(nearest.x+Math.sin(nearest.angle)*1.3,nearest.y+1.25,nearest.z+Math.cos(nearest.angle)*1.3);spot.target.position.set(nearest.x,nearest.y,nearest.z);}}const ri=Math.max(0,galleryLayout.rooms.findLastIndex(r=>-camera.position.z>=r.start));if(!touring&&!motion&&ri!==roomIndex){roomIndex=ri;ensureRoomResources();updateUI();history.replaceState(null,'','#'+roomData.rooms[ri].id);}if(!reduced)for(const s of sculptures)s.light.emissiveIntensity=s.base*(1+.08*Math.sin(now*.0007));if(!$('panel').open){exterior?.update(camera,renderer.getPixelRatio());renderer.render(scene,camera);};animationFrame=requestAnimationFrame(animate);}

async function boot(){try{roomData=initialData.rooms;sources=initialData.sources;galleryLayout=initialData.layout;exhibits=new Map([...sources.items,...extras()].map(e=>[e.id,e]));for(const item of initialData.curation.items)exhibits.set(item.id,{...exhibits.get(item.id),...item});for(const room of roomData.rooms)for(const id of room.exhibits)if(!exhibits.has(id))throw Error('Missing exhibit '+id);
 document.addEventListener('pointerdown',armFootsteps,{capture:true});document.addEventListener('keydown',armFootsteps,{capture:true});joystick=createJoystick($('move-stick'),()=>{wheelWalk?.reset();approachedExhibit=null;armFootsteps();motion=null;stopTour();});const dock=document.querySelector('.dock');const measureDock=()=>{document.documentElement.style.setProperty('--dock-height',(innerHeight-dock.getBoundingClientRect().top)+'px');captionKey='';syncLyrics();if(spatialReady)resize();};new ResizeObserver(measureDock).observe(dock);const measureCaptions=()=>{const lyricHeight=$('lyric-stage').getBoundingClientRect().height,guideHeight=$('tour-caption').getBoundingClientRect().height;document.documentElement.style.setProperty('--reading-height',Math.max(lyricHeight,guideHeight)+'px');};const captionObserver=new ResizeObserver(measureCaptions);captionObserver.observe($('lyric-stage'));captionObserver.observe($('tour-caption'));window.addEventListener('resize',measureDock);window.visualViewport?.addEventListener('resize',measureDock);$('focus-art').onclick=()=>showExhibit(selectedExhibit,true);$('overview').onclick=()=>{stopTour();roomView();};$('language').onclick=switchGuideLanguage;$('about').onclick=showAbout;$('room-works').onclick=showWorks;$('close-panel').onclick=closePanel;$('panel').addEventListener('close',()=>{crystalCleanup?.();crystalCleanup=null;});$('panel').addEventListener('click',e=>{if(e.target===$('panel')){const r=$('panel').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closePanel();}});$('previous').onclick=()=>goRoom(roomIndex-1);$('next').onclick=()=>goRoom(roomIndex+1);$('tour').onclick=()=>startTour();$('help').onclick=showHelp;$('verify-flaws').onclick=()=>showFlaw();$('tour-restart').onclick=()=>{stopTour();tourElapsed=0;guideResume=null;startTour();};$('enable-guide-sound').onclick=toggleGuideSound;$('guide-audio-start').onclick=resumeAudio;$('guide-audio-dismiss').onclick=dismissAudio;$('guide-audio-prompt').addEventListener('cancel',event=>{event.preventDefault();dismissAudio();});$('guide-speed').onclick=cycleGuideSpeed;$('motion').onclick=()=>{reduced=!reduced;if(reduced&&motion)motion.duration=0;updateUI();};document.addEventListener('visibilitychange',()=>{syncLyrics();scheduleLyrics();});$('music').ontimeupdate=syncMusic;$('music').onloadedmetadata=syncMusic;$('music').ondurationchange=syncMusic;$('music').onseeked=syncMusic;$('music').onplaying=syncMusic;$('music').onended=syncMusic;$('music').onpause=syncMusic;$('music-toggle').onclick=()=>{const track=exhibits.get(musicItem);if(track)playTrack(track,exhibits.get(musicArtworkId)||track,true,touring);};$('music-stop').onclick=()=>{cancelMusic();$('music').currentTime=0;$('music-bar').hidden=true;clearLyrics();syncMusic();};$('narration').onended=null;
 new ResizeObserver(()=>document.documentElement.style.setProperty('--lyric-stage-height',$('lyric-stage').offsetHeight+'px')).observe($('lyric-stage'));
 $('lyrics-mode').onclick=()=>applyLyricView(lyricView==='full'?'compact':'full');$('lyrics-collapse').onclick=()=>applyLyricView('hidden');$('lyrics-restore').onclick=()=>applyLyricView('compact');
 $('focus-art').onclick=()=>showExhibit(selectedExhibit);
 const stopMusic=$('music-stop').onclick;$('music-stop').onclick=()=>{stopMusic();clearLyrics();};
 updateUI();try{if(new URLSearchParams(location.search).get('view')==='gallery')throw Error('Reading gallery selected');await initWorld();$('loading').hidden=true;}catch(err){console.error(err);$('loading').hidden=true;$('fallback-gallery').hidden=false;$('focus-tools').hidden=true;$('walk-controls').hidden=true;$('look-controls').hidden=true;document.body.classList.add('flat-view');updateStrip();}
 await initialLanguage;applyGuideLanguage(languagePreference.language);
 document.body.dataset.museumReady='true';window.dispatchEvent(new Event('museum-ready'));
 const legacy={witness:'chronicle',voices:'chronicle',guardians:'waiting'},hash=location.hash.slice(1);const requested=roomData.rooms.findIndex(r=>r.id===(legacy[hash]||hash));if(requested>=0)goRoom(requested);if(new URLSearchParams(location.search).has('crystal'))showExhibit('physical-alpha');const requestedNFT=new URLSearchParams(location.search).get('exhibit');if(requestedNFT&&exhibits.has(requestedNFT))showExhibit(requestedNFT);document.addEventListener('visibilitychange',()=>{if(document.hidden){keys.clear();joystick?.reset();motion=null;lastTime=0;if(touring)stopTour();}});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'){stopTour();closePanel();}});if(!location.hash&&!new URLSearchParams(location.search).has('crystal')&&!requestedNFT)startTour(true);
 }catch(err){console.error(err);$('loading').innerHTML=tx('资料暂时无法加载。请刷新，或','Unable to load the exhibition. Reload or')+' <a href="./archive.html">'+tx('阅读本版目录','read the edition archive')+'</a>';}}
boot();
