"""Regenerate the plain HTML reading archive and release inventory from local edition data."""
from pathlib import Path
import hashlib, html, json
P=Path(__file__).resolve().parents[1];D=P/'dist';esc=html.escape
guides=json.loads((D/'data/guide-audio.json').read_text())['tracks']
plan=(D/'tour-plan.js').read_text();stops=json.loads(plan.split('export const tourStops=',1)[1].split(';\nexport const tourDuration',1)[0])
rooms=json.loads((D/'data/rooms.json').read_text());sources=json.loads((D/'data/sources.json').read_text());items={e['id']:e for e in sources['items']};art={e['exhibit']:e for e in json.loads((D/'data/curatorial-illustrations.json').read_text())['items']}
curation={e['id']:e for e in json.loads((D/'data/curation.json').read_text())['items']}
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Memory Station · Exhibition Archive</title><style>body{margin:0;background:#09121d;color:#dce7ef;font:17px/1.85 system-ui,sans-serif}main{max-width:900px;margin:auto;padding:45px 24px}a{color:#9be6ed}h1,h2{font-weight:450}h1{font-size:36px}h2{margin-top:65px;border-top:1px solid #355063;padding-top:25px}h3{margin-top:35px}p,pre{overflow-wrap:anywhere}pre{white-space:pre-wrap;font:15px/1.9 system-ui;background:#112331;padding:20px}img{max-width:100%;max-height:500px;object-fit:contain}audio{display:block;max-width:100%;margin:15px 0}small{color:#9bb3c3}.note{padding:20px;background:#122633}summary{cursor:pointer;color:#9be6ed}nav{display:flex;flex-wrap:wrap;gap:18px}</style><main><a href="./index.html">← 进入三维展馆 / Enter 3D museum</a><h1>文明记忆站<br><small>Exhibition archive · '+esc(rooms['edition'])+'</small></h1><p class="note">2026 年后续策展。三条 Bitcoin 正本保持封存；本版空间、路线、导览与展签不增加解释权威。六厅是展览章节，不是原作预先规定的六个历史阶段。</p><p>This is a later exhibition. It does not amend the three Bitcoin originals. This reading archive preserves the room route, guide text, local media and source references without requiring WebGL.</p><nav>']
parts[0]=parts[0].replace('<title>', '<link rel="canonical" href="https://museum.trinityaccord.org/archive.html">'+r'<script>(() => { const path = location.pathname.replace(/^\/museum(?:\/|$)/, "/"); const suffix = path + location.search + location.hash; if (["www.trinityaccord.org", "trinityaccord.org"].includes(location.hostname)) location.replace("https://museum.trinityaccord.org" + suffix); else if (location.hostname === "museum.trinityaccord.org" && path !== location.pathname) history.replaceState(null, "", suffix); })();</script>'+'<title>', 1)
parts.extend('<a href="#'+r['id']+'">'+r['number']+' '+esc(r['title'])+'</a>' for r in rooms['rooms']);parts.append('</nav>')
for r in rooms['rooms']:
 parts.extend(['<section id="'+r['id']+'"><h2>'+r['number']+' '+esc(r['title'])+'<br><small>'+esc(r['en'])+'</small></h2><p>'+esc(r['guide'])+'</p><p>'+esc(r['narration'])+'</p>'])
 for stop_no,stop in enumerate(stops):
  if stop['room']!=rooms['rooms'].index(r):continue
  parts.append('<details class="guide-reading"><summary>提问式导览 / Question-led guide · '+str(stop_no+1)+'</summary>')
  for lang in ['zh','en']:
   track=next(t for t in guides if t['stop']==stop_no and t['language']==lang)
   model=track.get('provenance',{}).get('model',track['voice'])
   parts.append('<p lang="'+('zh-CN' if lang=='zh' else 'en')+'">'+esc(track['text'])+'</p><audio controls preload="none" src="'+esc(track['file'])+'"></audio><small>AI-generated narration · '+esc(model)+' · '+esc(track['voice'])+'</small>')
  parts.append('</details>')
 for id in r['exhibits']:
  if id in curation:
   c=curation[id]
   parts.append('<article><h3>'+esc(c.get('title',id))+'</h3><p>'+esc(c.get('text',''))+'</p><p>'+esc(c.get('textEn',''))+'</p>')
   if c.get('date'):parts.append('<p>Bitcoin inscription #'+esc(c['number'])+' · '+esc(c['date'][:10])+' UTC / Bitcoin 上链日期</p>')
   if c.get('originalText'):parts.append('<details><summary>完整原文 / Complete original</summary><pre>'+esc(c['originalText'])+'</pre></details>')
   parts.append('</article>')
  if id in art:
   a=art[id];parts.append('<figure><img loading="lazy" src="'+esc(a['file'])+'" alt="'+esc(a['title'])+'"><figcaption>2026 年后续策展配图 · AI 生成 · 非历史原图 / Later AI-generated curatorial illustration, not historical source art. <a href="data/curatorial-illustrations.json">Provenance / 来源</a></figcaption></figure>')
  if id.startswith('canon-'):
   canon={'canon-1':('协议 / The Protocol','97631551','e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343i0'),'canon-2':('瑕疵之约 / The Covenant of the Flaw','98369145','90116f35de075074f5e5d1fbdda69a646a124e2287d7d58e2520317098cd4258i0'),'canon-3':('编年史 · 封存元记录 / The Chronicle · Sealed Meta-record','98387475','4d1c8f5ea8e8bae2982b42de6cc79deda3d243a21010a2888546e62ed7192c8ci0')}[id]
   parts.append('<article id="'+id+'"><h3>'+canon[0]+'</h3><p>墙面文字展位 / Text on the wall · Bitcoin '+canon[1]+'</p><a href="https://ordinals.com/inscription/'+canon[2]+'">阅读 Bitcoin 原文 / Read the Bitcoin original</a></article>')
   if id=='canon-3':parts.append('<p>编年史由封存元记录指向其 Ethereum 合约；铭文本身未嵌入全部编年史媒体。/ The sealed meta-record points to the Ethereum Chronicle; it does not embed all Chronicle media.</p>')
  if id not in items:
   parts.append('<p class="note">无配套歌曲：此展位为文字、实物或策展说明。/ No accompanying song: this entry presents text, an object or exhibition context.</p>');continue
  e=items[id];parts.append('<article id="'+id+'"><h3>'+esc(e['title'])+'</h3><small>No. '+str(e['ordinal'])+' · '+esc(e['date'][:10])+' UTC · Ethereum mint / 铸造日期</small>')
  for m in sorted(e['media'],key=lambda m:0 if m['kind']=='image' else 1):
   parts.append(('<img loading="lazy" src="'+m['file']+'" alt="'+esc(e['title'])+'">') if m['kind']=='image' else '<audio controls preload="none" src="'+m['file']+'"></audio>')
  if e.get('relatedSoundExhibit'):
   sound=items[e['relatedSoundExhibit']];audio=next(m for m in sound['media'] if m['kind']=='audio')
   parts.append('<p class="note"><strong>'+esc(e['songTitle'])+'</strong><br>'+esc(e['audioRelation']['noteZh'])+'<br>'+esc(e['audioRelation']['noteEn'])+'<br><a href="'+esc(sound['sourceUrl'])+'">Recording source / 录音原始记录</a> · <a href="'+esc(sound['localRecord'])+'">Preserved record / 已保存原文</a> · <a href="data/audio-audit.json">Audio audit / 声音核对</a></p><audio controls preload="none" aria-label="'+esc(e['songTitle'])+'" src="'+esc(audio['file'])+'"></audio>')
  if e.get('localRecord'):parts.append('<p><a href="'+e['localRecord']+'">本版保存的完整来源文字 / Local source text</a></p>')
  if e['lyrics']:parts.append('<details><summary>歌词文字 / Lyric text</summary><p>保留原始描述中的歌词；播放字幕按录音另行对齐。 Original description text; playback captions are aligned separately to the recording.</p><pre>'+esc(e['lyrics'])+'</pre></details>')
  parts.append('<p><a href="'+esc(e['sourceUrl'])+'">Pinned source record / 固定版本原始记录</a> · <a href="'+esc(e['tokenUrl'])+'">Ethereum token</a></p></article>')
 if r['id']=='formation':parts.append('<p><a href="https://www.trinityaccord.org/inscriptions/">完整正本镜像与 Bitcoin 坐标 / Read the three originals</a></p>')
 if r['id']=='material':parts.append('<h3>水晶展陈模型 / Exhibition reconstruction</h3><img src="assets/crystal/crystal-preview.png" alt="Blender dimensional exhibition reconstruction"><p>依据作者视频与实物照片复原双语内雕和抛光倒角；悬浮与光晕属于后续数字展陈，不是实物属性。参考渲染图早于本次光效调整。 Levitation and halo are later exhibition design; the saved reference render predates this lighting revision.<a href="data/crystal-model.json">建模依据与范围</a></p>')
 if r['id']=='material':
  groups=json.loads((P/'scene/crystal-bilingual-layout.json').read_text())['groups']
  parts.append('<details><summary>清晰阅读内雕文字 / Read the inscription clearly</summary><p>展陈转录，近似复原 / Exhibition transcription, approximate layout</p>'+''.join('<pre>'+esc('\n'.join(g['lines']))+'</pre>' for g in groups)+'</details>')
 if r['id']=='material':parts.append('<h3>Core Object Alpha · 真实照片副本</h3><img src="assets/core-object-alpha.jpg" alt="Core Object Alpha"><p><a href="https://www.trinityaccord.org/physical-anchor/">物理锚定及证据 / Physical anchor</a></p>')
 if r['id']=='guardians':parts.append('<p><a href="https://www.trinityaccord.org/authority/">权威边界 / Authority</a></p>')
 if r['id']=='waiting':parts.append('<article><h3>从作者到守护者 / From Author to Guardian</h3><p>守护者原则 v1.1 属于后续守护层，不是第四条正本。创作者的后续解释不获得独占权威。区块链不能阻止后来发表新文字。Guardian Principles v1.1 is later guardianship material, not a fourth Original. Later commentary gains no exclusive authority; blockchain cannot prevent later speech.</p><a href="https://www.trinityaccord.org/authority/">Guardian Principles v1.1 / 原则镜像</a> · <a href="data/records/guardian-charter-103635270.txt">Separate later Authority Charter / 另一个后续文件</a> · <a href="data/guardian-sources.json">Sources / 来源区分</a></article>')
 if r['id']=='waiting':parts.append('<p><a href="https://www.trinityaccord.org/first-contact/">回应或守护 / First Contact</a> · <a href="https://www.trinityaccord.org/">原网站当前状态 / Current state</a></p>')
 parts.append('</section>')
parts.append('<h2>版本与来源 / Edition & sources</h2><p>窗景 / Window scenery: NASA / NOAA DSCOVR EPIC · HYG v4.1, David Nash / Astronexus (CC BY-SA 4.0). <a href="data/space-design.json">影像与星表来源 / Image and star catalog credits</a>.</p><p><a href="data/sources.json">素材来源与处理清单</a> · <a href="data/rooms.json">空间与导览配置</a> · <a href="data/guide-audio.json">当前配音、字幕与声学核对</a> · <a href="data/release-manifest.json">文件清单与哈希</a></p><p>来源仓库版本：'+esc(sources['sourceCommit'])+'</p><p class="note">数字展馆的沿革属于后续展览史。文件哈希只说明本版文件一致性；恢复旧版也仍受浏览器兼容性影响。外部来源链接需要网络连接。</p></main></html>')
(D/'archive.html').write_text('\n'.join(parts))
files=[]
for p in sorted(D.rglob('*')):
 if not p.is_file() or p.name=='release-manifest.json':continue
 b=p.read_bytes();files.append({'path':p.relative_to(D).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
manifest={'schema':'trinity-museum.release.v1','edition':rooms['edition'],'sourceCommit':sources['sourceCommit'],'created':rooms.get('updated',rooms['created']),'scope':'Complete static exhibition distribution except this self-referential manifest. Source tools and history are preserved by the Git commit.','files':files}
(D/'data/release-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Archive and manifest ready:',len(files),'files,',sum(f['bytes'] for f in files),'bytes')
