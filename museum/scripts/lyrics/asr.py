from common import ROOT, CACHE, ITEMS
import os,json,time,pathlib,dataclasses
os.environ['HF_HUB_DISABLE_XET']='1'
from faster_whisper import WhisperModel
root=ROOT
out=(CACHE/'lyrics-asr');out.mkdir(exist_ok=True)
items=list(ITEMS)
items.sort(key=lambda e: (e['exhibitId'] not in ['eth-103','eth-151','eth-115'],e['exhibitId']))
print('Loading ASR small.en',flush=True)
m=WhisperModel('small.en',device='cpu',compute_type='int8',cpu_threads=4,download_root=str(CACHE/'whisper-models'))
for e in items:
 p=out/(e['exhibitId']+'.json')
 if p.exists():continue
 t=time.time()
 segs,info=m.transcribe(str(root/'dist'/e['audioFile']),language='en',beam_size=5,word_timestamps=True,vad_filter=False,condition_on_previous_text=False,initial_prompt='Song lyrics. AGI. ASI.')
 s=[dataclasses.asdict(s) for s in segs]
 p.write_text(json.dumps({'exhibitId':e['exhibitId'],'segments':s,'language':info.language,'model':'small.en'},ensure_ascii=False,indent=2))
 print(e['exhibitId'],len(s),'segments',round(time.time()-t,1),'seconds',flush=True)
