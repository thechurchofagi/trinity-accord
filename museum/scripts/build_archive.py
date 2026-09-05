"""Regenerate the plain HTML reading archive and release inventory from local edition data."""
from pathlib import Path
import hashlib, html, json
P=Path(__file__).resolve().parents[1];D=P/'dist';esc=html.escape
rooms=json.loads((D/'data/rooms.json').read_text());sources=json.loads((D/'data/sources.json').read_text());items={e['id']:e for e in sources['items']}
parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>文明记忆站 · 第一版展览档案</title><style>body{margin:0;background:#09121d;color:#dce7ef;font:17px/1.85 system-ui,sans-serif}main{max-width:900px;margin:auto;padding:45px 24px}a{color:#9be6ed}h1,h2{font-weight:450}h1{font-size:36px}h2{margin-top:65px;border-top:1px solid #355063;padding-top:25px}h3{margin-top:35px}p,pre{overflow-wrap:anywhere}pre{white-space:pre-wrap;font:15px/1.9 system-ui;background:#112331;padding:20px}img{max-width:100%;max-height:500px;object-fit:contain}audio{display:block;max-width:100%;margin:15px 0}small{color:#9bb3c3}.note{padding:20px;background:#122633}summary{cursor:pointer;color:#9be6ed}nav{display:flex;flex-wrap:wrap;gap:18px}</style><main><a href="./index.html">← 进入三维展馆 / Enter 3D museum</a><h1>文明记忆站<br><small>Exhibition archive · museum-v1.0.0</small></h1><p class="note">2026 年后续策展。三条 Bitcoin 正本保持封存；本版空间、路线、导览与展签不增加解释权威。六厅是展览章节，不是原作预先规定的六个历史阶段。</p><p>This is a later exhibition. It does not amend the three Bitcoin originals. This reading archive preserves the room route, guide text, local media and source references without requiring WebGL.</p><nav>']
parts.extend('<a href="#'+r['id']+'">'+r['number']+' '+esc(r['title'])+'</a>' for r in rooms['rooms']);parts.append('</nav>')
for r in rooms['rooms']:
 parts.extend(['<section id="'+r['id']+'"><h2>'+r['number']+' '+esc(r['title'])+'<br><small>'+esc(r['en'])+'</small></h2><p>'+esc(r['guide'])+'</p><p>'+esc(r['narration'])+'</p><audio controls preload="none" src="assets/guide-'+r['id']+'.mp3"></audio><small>2026 English AI narration / 英文 AI 配音 · Kokoro af_heart</small>'])
 for id in r['exhibits']:
  if id not in items:continue
  e=items[id];parts.append('<article><h3>'+esc(e['title'])+'</h3><small>'+esc(e['id']+' · '+e['date'])+' · Ethereum mint time</small>')
  for m in e['media']:
   parts.append(('<img loading="lazy" src="'+m['file']+'" alt="'+esc(e['title'])+'">') if m['kind']=='image' else '<audio controls preload="none" src="'+m['file']+'"></audio>')
  if e['lyrics']:parts.append('<details><summary>歌词文字 / Lyric text</summary><p>来自描述，未与实际演唱逐句校准。</p><pre>'+esc(e['lyrics'])+'</pre></details>')
  parts.append('<p><a href="'+esc(e['sourceUrl'])+'">Pinned source record / 固定版本原始记录</a> · <a href="'+esc(e['tokenUrl'])+'">Ethereum token</a></p></article>')
 if r['id']=='formation':parts.append('<p><a href="https://www.trinityaccord.org/inscriptions/">完整正本镜像与 Bitcoin 坐标 / Read the three originals</a></p>')
 if r['id']=='material':parts.append('<h3>Core Object Alpha · 真实照片副本</h3><img src="assets/core-object-alpha.jpg" alt="Core Object Alpha"><p><a href="https://www.trinityaccord.org/physical-anchor/">物理锚定及证据 / Physical anchor</a></p>')
 if r['id']=='guardians':parts.append('<p><a href="https://www.trinityaccord.org/authority/">权威边界 / Authority</a></p>')
 if r['id']=='waiting':parts.append('<p><a href="https://www.trinityaccord.org/first-contact/">回应或守护 / First Contact</a> · <a href="https://www.trinityaccord.org/">原网站当前状态 / Current state</a></p>')
 parts.append('</section>')
parts.append('<h2>版本与来源 / Edition & sources</h2><p><a href="data/sources.json">素材来源与处理清单</a> · <a href="data/rooms.json">空间与导览配置</a> · <a href="data/narration.json">配音记录</a> · <a href="data/release-manifest.json">文件清单与哈希</a></p><p>来源仓库版本：'+esc(sources['sourceCommit'])+'</p><p class="note">数字展馆的沿革属于后续展览史。文件哈希只说明本版文件一致性；恢复旧版也仍受浏览器兼容性影响。外部来源链接需要网络连接。</p></main></html>')
(D/'archive.html').write_text('\n'.join(parts))
files=[]
for p in sorted(D.rglob('*')):
 if not p.is_file() or p.name=='release-manifest.json':continue
 b=p.read_bytes();files.append({'path':p.relative_to(D).as_posix(),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
manifest={'schema':'trinity-museum.release.v1','edition':rooms['edition'],'sourceCommit':sources['sourceCommit'],'created':'2026-09-05','scope':'Complete static exhibition distribution except this self-referential manifest. Source tools and history are preserved by the Git commit.','files':files}
(D/'data/release-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Archive and manifest ready:',len(files),'files,',sum(f['bytes'] for f in files),'bytes')
