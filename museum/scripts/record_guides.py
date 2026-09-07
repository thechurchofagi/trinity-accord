"""Generate bundled bilingual guide recordings and timed short captions.
Install edge-tts; run with --script-json containing the exported tourStops.
Only public curatorial text is submitted. Device speech is not used at runtime.
"""
import asyncio,argparse,hashlib,html,json,os,re,subprocess,tempfile
from pathlib import Path
import edge_tts
P=Path(__file__).resolve().parents[1];D=P/'dist'
if os.environ.get('SSL_CERT_FILE'):
 edge_tts.communicate._SSL_CTX.load_verify_locations(os.environ['SSL_CERT_FILE'])
ap=argparse.ArgumentParser();ap.add_argument('--script-json',required=True);ap.add_argument('--cache-dir',default=str(Path(tempfile.gettempdir())/'trinity-museum-guide-cache'));args=ap.parse_args();cache_root=Path(args.cache_dir);cache_root.mkdir(parents=True,exist_ok=True)
stops=json.loads(Path(args.script_json).read_text());folder=D/'assets/guides';folder.mkdir(exist_ok=True)

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

async def record(index,lang,voice,rate):
 text=stops[index][lang];file=folder/f'{index:02}-{lang}.mp3';cache=cache_root/f'{index:02}-{lang}.json'
 text_hash=hashlib.sha256(text.encode()).hexdigest()
 if cache.exists() and file.exists():
  old=json.loads(cache.read_text())
  if old['textSha256']==text_hash and old['rate']==rate:return old
 for attempt in range(3):
  try:
   words=[];audio=bytearray()
   async def stream():
    async for event in edge_tts.Communicate(text,voice=voice,rate=rate,boundary='WordBoundary',receive_timeout=40).stream():
     if event['type']=='audio':audio.extend(event['data'])
     elif event['type']=='WordBoundary':words.append({'start':event['offset']/1e7,'end':(event['offset']+event['duration'])/1e7,'text':event['text']})
   await asyncio.wait_for(stream(),90)
   if not audio or not words:raise RuntimeError('Missing audio/timing')
   file.write_bytes(audio)
   duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(file)],text=True))
   result={'stop':index,'language':lang,'voice':voice,'rate':rate,'text':text,'textSha256':text_hash,'file':file.relative_to(D).as_posix(),'sha256':hashlib.sha256(audio).hexdigest(),'duration':duration,'cues':captions(words,text,lang)}
   cache.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(index,lang,round(duration,1),'seconds',flush=True);return result
  except Exception as e:
   if attempt==2:raise
   print('Retry',index,lang,type(e).__name__,flush=True)
   await asyncio.sleep(2)
async def main():
 tracks=[]
 # Bounded synthesis concurrency; each exact text/language output is cached.
 sem=asyncio.Semaphore(3)
 async def one(i,l,v,r):
  async with sem:return await record(i,l,v,r)
 tracks=await asyncio.gather(*(one(i,l,v,r) for i in range(len(stops)) for l,v,r in [('zh','zh-CN-XiaoxiaoNeural','+25%'),('en','en-US-AriaNeural','+15%')]))
 out={'schema':'trinity-museum.recorded-guides.v1','type':'AI-generated curatorial narration','source':'edge-tts','defaultPlaybackRate':1.1,'tracks':tracks}
 (D/'data/guide-audio.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
 print('Bilingual recordings and timing saved',len(tracks),flush=True)
asyncio.run(main())
