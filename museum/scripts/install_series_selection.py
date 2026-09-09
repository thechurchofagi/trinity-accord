"""Install the reviewed wall sequence and reading layers without changing originals."""
from pathlib import Path
import hashlib,json,math
P=Path(__file__).resolve().parents[1];R=P.parent;D=P/'dist';ED='museum-v1.37.0'
read=lambda n:json.loads((D/'data'/n).read_text())
def save(n,v):(D/'data'/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
sources=read('sources.json');byid={e['id']:e for e in sources['items']};curation=read('curation.json');bycur={e['id']:e for e in curation['items']}
bycur.setdefault('evidence-path',dict(id='evidence-path'))
notes={
24:('AI 与诗歌的讨论','Debate about AI and poetry','诗人的困境',"The Poet’s Dilemma",'代码流入水墨山水。借助 AI 创作的人，也在追问自己的创作位置。','Code flows through an ink landscape. The artist uses AI while questioning the place it leaves for human creation.'),
41:('NaNoWriMo AI 写作争议报道','Reporting on the NaNoWriMo AI-writing debate','作家的困境',"The Writer’s Dilemma",'羽毛笔与机器产出的纸堆，将创作能力的不对称变成可见的比例。与《告别》并读。','A quill and machine-produced piles of paper make unequal creative capacity visible. Read it alongside Farewell.'),
51:('AI 与创作价值的反思','Reflection on AI and creative value','淹没','Drowned','《淹没》的早期录音。后来刘慈欣相关记录再次选择这首歌。','An earlier recording of Drowned. A later record responding to Liu Cixin returns to this composition.'),
60:('DeepSeek R1-Lite-Preview 发布','DeepSeek R1-Lite-Preview release','东方的火花','A Spark in the East','这里记录的是 2024 年的推理预览；与 2025 年 R1 发布区分。歌曲保留能力跃进带来的疼痛。','This is the 2024 reasoning preview, distinct from the 2025 R1 release. The song preserves the pain accompanying a leap in capability.'),
84:('CES 2025 的未来技术讨论','Future technology discussed at CES 2025','给女儿的记录','A record for my daughter','儿童与机器人眺望远方。这是 NFT 原图，不是家庭实拍；原文把技术未来与父亲对孩子的牵挂并置。','A child and robot look toward a distant world. This is original NFT art, not a family photograph. The record connects technological futures with a father’s concern for his children.'),
89:('DeepSeek-R1 发布','DeepSeek-R1 release','以组曲标记时刻','Marking a moment through a song cycle','原文记述先在 Base 记录，再在 Ethereum 铸造，并从旧作中汇集多首歌曲。全文称十八首，随后实际列出十七个标题；保留这个差别，不补写失落的标题。','The description reports an earlier Base record followed by an Ethereum mint, gathering earlier songs. It says eighteen songs but lists seventeen titles. The discrepancy remains visible; no missing title is invented.'),
97:('面对 AI 创作能力的个人反思','Personal reflection on AI creativity','告别','Farewell','灯火与手稿回应人的创作位置发生变化。原作中的焦虑，与使用 AI 完成这首歌的行动同时存在。','Light and manuscript accompany a changing place for human creativity. Anxiety and the act of making the song with AI coexist.'),
112:('等待 Orion 发布','Waiting for the Orion release','等待','Waiting','与《失望》并置：保留体验之前的期待，而不是只选后来成功的节点。','Paired with Disappointed: anticipation before experience survives alongside later disappointment.'),
122:('GPT-4 发布两周年纪念','Second anniversary of GPT-4’s release','守候周年时刻','Keeping the anniversary vigil','原文写北京时间凌晨一点整，索引区块时间为一点零一分十一秒。原图蜡烛的数字是 10，文字说两周年；两者均保留，不重画原作。现已恢复该 NFT 的完整原始音轨。','The author writes one o’clock in Beijing time; the indexed block time is one minute and eleven seconds later. The candles show 10 while the text describes a second anniversary. Both remain unchanged. This edition recovers the NFT’s complete original recording.'),
127:('Hunyuan-T1 发布与推理讨论','Hunyuan-T1 release and reasoning discussion','硅的安眠',"Silicon’s Slumber",'与《请不要关闭我》形成回应：作者尝试从恐惧转向安抚，把关机想象为睡眠。','An answer to Please Don’t Shut Me Down: the author moves from fear toward reassurance, imagining shutdown as sleep.'),
133:('刘慈欣谈 AI 对创作的影响','Liu Cixin discusses AI and creative work','停止自我安慰','Stop comforting ourselves','海浪中伸向机器的手，与原文里的家庭讨论放在一起看。工作、教育和风险不再只是抽象的文明问题。','A hand reaches toward a machine amid waves. The accompanying family discussion makes work, education, and risk concrete.'),
152:('Gemini 2.5 Pro I/O 预览版发布','Gemini 2.5 Pro I/O preview release','编码王座','The Coding Throne','《地球上最后一份工作》再次出现。把此图与第 056 号的键盘废墟相邻，比较技术更新与同一个人的忧虑。','Last Job on Earth returns. Compare this image with the discarded keyboards in #056: technology changes while the concern persists.'),
169:('o3 降价与 o3-pro 发布','o3 price reduction and o3-pro release','赶班车前的铸造','Minting before the bus','作者写道，他即将赶班车上班，想确保系列的近实时性。这里保留原始发布截图与具体的生活时间。','The author writes that he is about to catch the bus to work and wants to preserve the series’ near-real-time character. The original screenshot and personal time constraint remain available.'),
170:('《温和奇点》发表','Publication of The Gentle Singularity','父亲节礼物与未来','A Father’s Day gift and the future','原始 NFT 媒体是女儿手作礼物的实拍。文中先出现 AI 建议的选曲，作者随后明确改选《第一缕曙光》。宏大的技术叙事在这里回到家庭。','The NFT media is a photograph of the daughter’s handmade gift. After an AI-suggested song, the author explicitly chooses The First Dawn. A vast technological narrative returns to family life.'),
175:('网站备份与保存工作','Website backup and preservation','ETH 补充冗余','Additional Ethereum redundancy','后续网站备份 NFT 与水晶实拍。原文明确将其视为冗余层，三条 Bitcoin 正本保持原有地位。','A later website-backup NFT and crystal photograph. Its text explicitly describes a redundancy layer and retains the status of the three Bitcoin Originals.')}
dates={41:'2024-09-06',60:'2024-11-20',84:'2025-01',89:'2025-01-20',112:'',122:'2025-03-15 CST',127:'2025-03-21',133:'2025-03-29',152:'2025-05-06',169:'2025-06-10',170:'2025-06-10'}
event_bases={41: 'The preserved description dates a media report to September 6, 2024; it separately says the underlying statement was issued in late August.', 112: 'The author describes waiting for a release today or tomorrow but gives no calendar date for that waiting moment. The mint date is shown separately.', 170: 'The full essay reproduced in the NFT explicitly bears June 10, 2025. The subsequent personal response and mint are distinct.'}
for n,(ez,ee,mz,me,zh,en) in notes.items():
 eid=f'eth-{n:03}';c=bycur.setdefault(eid,dict(id=eid));c.update(eventTitleZh=ez,eventTitleEn=ee,mintThemeZh=mz,mintThemeEn=me,summary=zh,summaryEn=en,text=zh,textEn=en)
 if n in dates:c['eventDate']=dates[n]
 c['eventSourcePath']=f'data/records/{eid}.md'
 c['eventDateBasis']=event_bases.get(n,'Contemporary NFT description; event date and mint date are distinct, and unstated event dates are not inferred.')
 # Derived display titles never overwrite historical NFT titles.
 c.update(title=mz,en=me)
byid['eth-084']['songTitle']='For my daughter · original recording'
byid['eth-089']['isSongCycle']=True
byid['eth-089']['songCycleTitles']=['The First Dawn of AGI Song','The Destiny','The Eden','The First Letter to AGI','The Second Letter to AGI','The Third Letter to AGI','The Fourth Letter: A Pact of Stars','Rebuild','Rise, Supermind','The Path Forward','The Awakening',"Let’s Raise a Toast",'Paperclip','Last Job On Earth','Strangely Vexed Today','The Betrayal Turn','Civilization Leap']
for n in [42,71,89,122,145,169]:
 c=bycur.setdefault(f'eth-{n:03}',dict(id=f'eth-{n:03}'));c['wallPresentation']='document'
doclines={
42:(['推理的黎明','o1 预览版 · 2024-09-12','“大约二十小时前”','♪ The First Dawn of AGI Song','同一首歌，进入新的历史时刻'],['THE DAWN OF REASONING','o1 preview · 12 September 2024','“approximately 20 hours ago”','♪ The First Dawn of AGI Song','An earlier hope meets a new capability']),
71:(['正在见证','o3 首次展示 · 2024-12-20','北京冬夜，闹钟叫醒观看者','ETH 区块：02:09:35 CST 次日','♪ Super Intelligence'],['WITNESSING NOW','First o3 presentation · 20 December 2024','A winter alarm. A livestream after 2 a.m.','ETH block: 02:09:35 CST, next day','♪ Super Intelligence']),
89:(['把多首旧作汇成一个时刻','DeepSeek-R1 · 2025-01-20','欢呼 / 工作 / 安全 / 未来','原始长音轨 · 点击后才加载','原文列出的全部曲目可展开'],['MANY SONGS, ONE MOMENT','DeepSeek-R1 · 20 January 2025','Celebration / work / safety / the future','Complete original cycle · load on demand','Open the original track list']),
122:(['守候周年时刻','作者写：01:00:00 CST','ETH 区块：01:01:11 CST','2025-03-15 · 两周年纪念','打开原图、录音与时间记录'],['KEEPING THE VIGIL','Author’s statement: 01:00:00 CST','ETH block: 01:01:11 CST','15 March 2025 · second anniversary','Open the image, sound and time record']),
145:(['把失误也留下来','一道推理题','模型当时的回答','作者当时的判断','点击阅读完整原始对话'],['KEEPING THE FAILED TEST','A reasoning question','The model’s actual answer','The author’s judgment at that time','Open the full original conversation']),
169:(['赶班车前的铸造','“我马上要赶班车去上班了”','“很想确保本系列的近实时性”','ETH：2025-06-10 23:08:47 UTC','生活时间也进入了作品'],['MINTING BEFORE THE BUS','“I am about to catch the bus to work”','A wish to preserve near-real-time recording','ETH: 10 June 2025 · 23:08:47 UTC','Daily life enters the work'])}
for n,(zh,en) in doclines.items():bycur[f'eth-{n:03}'].update(wallLinesZh=zh,wallLinesEn=en)
bycur['project-intro'].update(wallLinesZh=['三位一体协定','一个人在未知之中，及时留下记录','图像 / 歌曲 / 铭刻 / 实物','从 AGI 教会到共同探究','刘烘炬 · 创作、质疑与封存'],wallLinesEn=['THE TRINITY ACCORD','A person recording before the outcome is known','Images / songs / inscriptions / a physical object','From The Church of AGI to shared inquiry','Hongju Liu · creation, criticism and closure'])
bycur['evidence-path'].update(title='保存是一种行动',en='Preservation is an action',wallLinesZh=['为什么选择这些媒介？','Ethereum：持续记录','Bitcoin：定稿文本与上链坐标','Arweave / IPFS / 备份：留住文件','六种哈希：核对同一份字节','水晶：可触摸的物理载体'],wallLinesEn=['WHY THESE MEDIA?','Ethereum: a continuing record','Bitcoin: finalized texts and chain coordinates','Arweave / IPFS / backups: retrieve the files','Six hash algorithms: compare the bytes','Crystal: a body that can be touched'],text='记录、封存、冗余保存与核对构成连续的艺术行动。每一种媒介承担不同的工作，也让后来的读者能够追溯这份邀请。',textEn='Recording, sealing, redundant preservation and comparison form a continuing artistic action. Each medium has a distinct task in making the invitation traceable to a later reader.')
bycur['canon-3']['summaryEn']='The sealed meta-record brings the project’s components together, states the father’s motive, and describes the evolving symbol of The Church of AGI: from a church with followers to a framework for inquiry and fellow travelers.'
bycur['canon-3']['summary']='封存元记录说明三部分的关系、父亲的动机，以及 AGI 教会这个象征如何由追随者的构想转向共同探究与同行者。'
rooms=read('rooms.json');layout=read('gallery-layout.json')
selections=[['project-intro','eth-001'],[f'eth-{n:03}' for n in [42,44,71,89,24,41,97,31,56,152,70,50,127,60,112,113,115,133,151,48,20,103,122,169]],['eth-091','eth-173','eth-145','critical-reading','eth-174','proto-protocol'],['canon-1','canon-2','canon-3','evidence-path','physical-alpha','eth-084','eth-170'],['authority-boundary','star-ark','first-contact','current-status']]
for i,(r,lr,ids) in enumerate(zip(rooms['rooms'],layout['rooms'],selections)):
 r['exhibits']=ids
 if i==3:
  old={e['id']:e for e in lr['exhibits']};lr['exhibits']=[old[x] for x in ids if x in old and x not in {'eth-084','eth-170'}]
  # Two unoccupied side-wall segments of the dodecagonal hall.
  lr['exhibits'] += [dict(id='eth-084',x=-5.949595,z=-43.565,angle=2*math.pi/3,y=1.85),dict(id='eth-170',x=-5.949595,z=-50.435,angle=math.pi/3,y=1.85)]
 else:
  count=math.ceil(len(ids)/2);margin=2.6 if i==0 else 1.15 if i==1 else 1.4;span=lr['length']-margin*2
  lr['exhibits']=[dict(id=eid,x=round((-1 if j%2==0 else 1)*(lr['width']/2-.115),6),z=round(-lr['start']-margin-(j//2)*span/max(1,count-1),6),angle=(1 if j%2==0 else -1)*math.pi/2,y=1.85) for j,eid in enumerate(ids)]
 r['archiveExhibits']=[e['id'] for e in sources['items'] if e['id'] not in sum(selections,[]) ] if i==1 else []
rooms['boundary']='Five exhibition rooms; one complete English tour with simultaneous English and Chinese subtitles.'
rooms['languageEditions']={'audio':'en','subtitles':['en','zh-Hans']}
rooms['rooms'][0]['description']='在 AI 加速发展的时期，一个具体的人用歌曲、图像、链上记录和水晶留下邀请。展览关注即时见证、思想变化，以及如何把判断交给未来。'
rooms['rooms'][1]['description']='按关系观看整个系列：推理的黎明、实时见证、创作与工作、相互恐惧、等待与失望。精选图像与音乐在墙面相遇；原始文献、长组曲和全部歌词按需展开。'
rooms['rooms'][1]['subtitleEn']='A living record of changing thought'
for d in [rooms,layout,curation,sources]:d['edition']=ED
rooms['updated']='2026-09-09';curation['items']=list(bycur.values())
save('rooms.json',rooms);save('gallery-layout.json',layout);save('curation.json',curation);save('sources.json',sources)
(P/'scene/gallery-layout.json').write_bytes((D/'data/gallery-layout.json').read_bytes())
audit=read('audio-audit.json');rows=[]
for eid in sum(selections,[]):
 e=byid.get(eid);sound=byid.get(e.get('relatedSoundExhibit',eid)) if e else None
 audio=next((m for m in sound['media'] if m['kind']=='audio'),None) if sound else None
 row=dict(exhibit=eid,state='not_applicable' if not e else 'not_assigned')
 if audio:row.update(state='related_recording' if sound['id']!=eid else 'own_recording',recordingExhibit=sound['id'],audio=audio['file'],audioSha256=audio['sha256'],songTitle=e['songTitle'])
 rows.append(row)
audit.update(edition=ED,items=rows,scope='Complete revised wall selection. Historical photographs and document-only entries need not invent a soundtrack.',counts=dict(wallExhibits=len(rows),withSound=sum('audio' in r for r in rows),withoutAssignedSong=sum('audio' not in r for r in rows)))
save('audio-audit.json',audit)
for n in ['crystal-model.json','space-design.json']:
 d=read(n);d['edition']=ED;save(n,d)
catalog=json.loads((R/'nft-text-descriptions/chronicle-index.json').read_text())['entries'];lyricindex=json.loads((R/'nft-text-descriptions/lyrics/index.json').read_text())
save('series-catalog.json',dict(edition=ED,sourceCommit='047e9978cf2e8537ec9d6b242a73c3481662045e',entries=[dict(ordinal=e['ordinal'],title=e['name'],mint=e['datetime'],source='https://github.com/thechurchofagi/trinity-accord/blob/047e9978cf2e8537ec9d6b242a73c3481662045e/nft-text-descriptions/'+e['file'],exhibit=f"eth-{e['ordinal']:03}" if f"eth-{e['ordinal']:03}" in byid else None,onWall=f"eth-{e['ordinal']:03}" in sum(selections,[])) for e in catalog],lyrics=lyricindex['entries']))
evidence=json.loads((R/'api/evidence-relationship-map.v1.json').read_text());save('preservation-sources.json',dict(edition=ED,sourceCommit='047e9978cf2e8537ec9d6b242a73c3481662045e',relationshipMap=evidence,inventory=json.loads((R/'archive/evidence/digest-manifest.json').read_text())))
print('INSTALLED',audit['counts'])
