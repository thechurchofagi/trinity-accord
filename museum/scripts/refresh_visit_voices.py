"""Incrementally record changed museum narration, retaining exact unchanged takes.
Uses built-in neural voices and provider word timing. No voice cloning.
"""
import asyncio,hashlib,html,json,os,re,subprocess
from pathlib import Path
import edge_tts
P=Path(__file__).resolve().parents[1];D=P/'dist'
edge_tts.communicate._SSL_CTX.load_verify_locations(os.environ.get('SSL_CERT_FILE','/etc/ssl/certs/ca-certificates.crt'))
def captions(words,text,lang):
 pieces=[];cursor=0
 for word in words:
  word['text']=html.unescape(word['text']);pos=text.find(word['text'],cursor)
  if pos<0:pos=text.lower().find(word['text'].lower(),cursor)
  if pos>=0:
   end=pos+len(word['text']);tail=re.match(r'[，。！？、；：,.!?;:…’”\"\s]*',text[end:]).group(0)
   word['text']=text[pos:end]+tail;cursor=end+len(tail)
  pieces.append(word)
 cues=[];group=[]
 for word in pieces:
  candidate=''.join(w['text'] for w in group)+word['text']
  if group and (len(candidate.strip())>(28 if lang=='zh' else 68) or word['start']-group[-1]['end']>.7):
   cues.append({'start':group[0]['start'],'end':group[-1]['end'],'text':''.join(w['text'] for w in group).strip()});group=[]
  group.append(word)
  if re.search(r'[。！？.!?;；][’”\"]?\s*$',word['text']):
   cues.append({'start':group[0]['start'],'end':group[-1]['end'],'text':''.join(w['text'] for w in group).strip()});group=[]
 if group:cues.append({'start':group[0]['start'],'end':group[-1]['end'],'text':''.join(w['text'] for w in group).strip()})
 return cues

async def main():
 manifest=json.loads((D/'data/guide-audio.json').read_text());old=manifest['tracks']+manifest['inspectionTracks'];stops=json.loads((P/'scene/tour-script.json').read_text())
 output=D/'assets/guides-v133';output.mkdir(exist_ok=True);sem=asyncio.Semaphore(2)
 async def make(text,language,stop=None,flaw=None):
  found=next((t for t in old if t['text']==text and t['language']==language),None)
  if found:return dict(found,**({'stop':stop} if stop is not None else {'flaw':flaw}))
  h=hashlib.sha256(text.encode()).hexdigest();stem=('stop-'+str(stop) if stop is not None else 'flaw-'+str(flaw))+'-'+language;file=output/(stem+'.mp3');cache=output/(stem+'.json')
  if cache.exists():
   take=json.loads(cache.read_text())
   if take['textSha256']==h:return take
  voice='zh-CN-XiaoxiaoNeural' if language=='zh' else 'en-US-AndrewMultilingualNeural'
  async with sem:
   for attempt in range(3):
    try:
     audio=bytearray();words=[]
     async for event in edge_tts.Communicate(text,voice=voice,rate='+5%' if language=='zh' else '+0%',boundary='WordBoundary',receive_timeout=45).stream():
      if event['type']=='audio':audio.extend(event['data'])
      elif event['type']=='WordBoundary':words.append(dict(start=event['offset']/1e7,end=(event['offset']+event['duration'])/1e7,text=event['text']))
     assert audio and words;file.write_bytes(audio)
     duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(file)]))
     take=dict(language=language,voice=voice,rate='+5%' if language=='zh' else '+0%',text=text,textSha256=h,file=file.relative_to(D).as_posix(),sha256=hashlib.sha256(audio).hexdigest(),duration=duration,cues=captions(words,text,language),provenance=dict(provider='Microsoft Edge neural synthesis',voice=voice,voiceKind='built-in synthetic; no cloning',timing='provider WordBoundary'))
     take.update({'stop':stop} if stop is not None else {'flaw':flaw});cache.write_text(json.dumps(take,ensure_ascii=False,indent=2)+'\n');print(stem,round(duration,2),'seconds',flush=True);return take
    except Exception as e:
     print('retry',stem,type(e).__name__,flush=True)
     if attempt==2:raise
 tasks=[make(s[l],l,stop=i) for i,s in enumerate(stops) for l in ['zh','en']]
 tracks=await asyncio.gather(*tasks)
 flaws=[
 ('第一处瑕疵，请仔细看不规则结构的轮廓，以及它和周围内雕文字的位置关系。这里展示的是公开存档中的原始显微照片。文件哈希可以核对是不是同一份照片；真正比较水晶，还要把形态、相对位置、深度，以及不同观察角度下的变化放在一起。单个亮点不足以确认物件，多处特征之间的关系才更有辨识力。瑕疵之约借此把可以复制的文字，联系到一件经历过真实加工、值得继续照料的物。这也留下一个艺术上的问题：一件物的价值，是否一定依赖完美？',
 'For the first flaw, look closely at the irregular outline and its position beside the engraved lettering. This is an original microscope photograph from the public archive. A file hash can check whether it is the same photograph. Comparing the crystal itself also requires shape, relative position, depth, and changes seen from different angles. A single bright point is not enough to identify an object; relationships among several features are more distinctive. The Covenant links reproducible text to something that has passed through physical manufacture and can be cared for. It also leaves an artistic question: must value depend on perfection?'),
 ('第二处，请比较它与第一处的形态差异。它是另一条观察线索，需要和周围文字的位置一起核对。','For the second flaw, compare its shape with the first. It provides another clue, considered together with its position beside the lettering.'),
 ('第三处补充了另一组不规则特征。三张照片一起看，帮助形成相互参照；实际核验仍需观察实物。','The third photograph adds another irregular feature. Seen together, the three images provide cross-references; physical verification still requires examining the object.')]
 inspection=await asyncio.gather(*(make(t,l,flaw=i) for i,pair in enumerate(flaws) for t,l in zip(pair,['zh','en'])))
 manifest.update(tracks=tracks,inspectionTracks=inspection,source='Mixed retained and newly recorded built-in neural voices; per-track provenance',voiceReview='Existing unchanged takes retained; new tracks use provider word timings, checked against complete source text. No human-listening certification.')
 (D/'data/guide-audio.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 (D/'data/inspection-audio.json').write_text(json.dumps(inspection,ensure_ascii=False,indent=2)+'\n')
 print('VOICE_REFRESH_COMPLETE',flush=True)
asyncio.run(main())
