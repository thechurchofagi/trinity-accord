"""Produce bundled curatorial audio locally with a pinned Qwen model.

No source artwork/audio is changed or sent to a speech service. Each paragraph
is checkpointed; restarting reuses only hash-matching takes. Caption timings are
measured paragraph boundaries with proportional short cues, not word alignment.
"""
import argparse,ast,hashlib,json,re,time,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel
P=Path(__file__).resolve().parents[1];D=P/'dist'
a=argparse.ArgumentParser();a.add_argument('--model',required=True);a.add_argument('--cache',required=True);a.add_argument('--batch',type=int,default=4);a.add_argument('--limit',type=int,default=0);args=a.parse_args()
cache=Path(args.cache);cache.mkdir(parents=True,exist_ok=True)
H=lambda v:hashlib.sha256(v.encode() if isinstance(v,str) else v).hexdigest()
revision='0c0e3051f131929182e2c023b9537f8b1c68adfe'
# Reuse the explicitly reviewed inspection script, without importing its old network producer.
tree=ast.parse((P/'scripts/refresh_visit_voices.py').read_text())
flaws=next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='flaws' for t in n.targets))
tracks=[dict(stop=i,language=l,text=s[l]) for i,s in enumerate(json.loads((P/'scene/tour-script.json').read_text())) for l in ['zh','en']]
tracks += [dict(flaw=i,language=l,text=text) for i,pair in enumerate(flaws) for l,text in zip(['zh','en'],pair)]
voices={'zh':'Serena','en':'Aiden'}
style={'zh':'温暖沉静的博物馆讲解，清晰自然，语速适中，不要拖长字音。准确朗读文字，不添加内容。','en':'A thoughtful museum guide, warm and calm, with clear natural conversational pacing. Read exactly the supplied text.'}
def paragraphs(text,language):
 sentences=re.findall(r'.+?(?:[。！？]|[.!?](?=\s|$)|$)',text)
 groups=[];cur='';limit=110 if language=='zh' else 240
 for sentence in sentences:
  if cur and len(cur)+len(sentence)>limit:groups.append(cur.strip());cur=''
  cur+=sentence
 if cur.strip():groups.append(cur.strip())
 assert re.sub(r'\s','',''.join(groups))==re.sub(r'\s','',text)
 return groups
jobs={}
for t in tracks:
 t['parts']=[]
 for text in paragraphs(t['text'],t['language']):
  key=H(json.dumps([revision,voices[t['language']],style[t['language']],text],ensure_ascii=False))
  job=dict(key=key,text=text,language=t['language'],voice=voices[t['language']]);t['parts'].append(job);jobs[key]=job
pending=[j for j in jobs.values() if not (cache/(j['key']+'.wav')).exists()]
pending.sort(key=lambda j:(j['language'],len(j['text'])))
if args.limit:pending=pending[:args.limit]
print('QWEN_PLAN',len(tracks),'tracks;',len(jobs),'paragraphs;',len(pending),'pending',flush=True)
torch.set_num_threads(6);torch.manual_seed(42)
model=Qwen3TTSModel.from_pretrained(args.model,device_map='cpu',dtype=torch.bfloat16,attn_implementation='sdpa')
for start in range(0,len(pending),args.batch):
 batch=pending[start:start+args.batch];began=time.monotonic();print('QWEN_BATCH_BEGIN',start+1,min(start+len(batch),len(pending)),flush=True)
 waves,sr=model.generate_custom_voice(text=[j['text'] for j in batch],language=['Chinese' if j['language']=='zh' else 'English' for j in batch],speaker=[j['voice'] for j in batch],instruct=[style[j['language']] for j in batch],max_new_tokens=1400)
 for j,wav in zip(batch,waves):
  assert np.isfinite(wav).all() and len(wav)>sr and len(wav)<sr*105, ('Invalid take',j['key'],len(wav)/sr)
  sf.write(cache/(j['key']+'.wav'),wav,sr,subtype='PCM_16')
  (cache/(j['key']+'.json')).write_text(json.dumps(dict(j,duration=len(wav)/sr),ensure_ascii=False)+'\n')
 print('QWEN_BATCH_COMPLETE',start+len(batch),'/',len(pending),'wallSeconds',round(time.monotonic()-began,1),'audioSeconds',round(sum(len(w)/sr for w in waves),1),flush=True)
if args.limit:raise SystemExit(0)
del model
out=D/'assets/guides-qwen-v133';out.mkdir(exist_ok=True)
for t in tracks:
 samples=[];cues=[];clock=0
 for j in t.pop('parts'):
  wav,sr=sf.read(cache/(j['key']+'.wav'),dtype='float32');dur=len(wav)/sr;samples.extend([wav,np.zeros(int(sr*.16),dtype=np.float32)])
  # Short subtitle cues stay within their own recorded paragraph.
  limit=28 if t['language']=='zh' else 68
  pieces=[];cur=''
  units=re.findall(r'\S+\s*',j['text']) if t['language']=='en' else list(j['text'])
  for unit in units:
   if cur and len(cur+unit)>limit:pieces.append(cur.strip());cur=''
   cur+=unit
  if cur.strip():pieces.append(cur.strip())
  weights=[len(re.sub(r'\s','',v)) for v in pieces];total=sum(weights);local=0
  for text,weight in zip(pieces,weights):
   end=local+(dur-.04)*weight/total;cues.append(dict(start=round(clock+local,4),end=round(clock+end,4),text=text));local=end
  clock+=dur+.16
 stem=('stop-'+str(t['stop']) if 'stop' in t else 'flaw-'+str(t['flaw']))+'-'+t['language'];wavpath=cache/(stem+'.wav');sf.write(wavpath,np.concatenate(samples),sr,subtype='PCM_16');mp3=out/(stem+'.mp3')
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(wavpath),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','24000','-ac','1','-b:a','128k',str(mp3)],check=True)
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(mp3)]))
 t.update(file=mp3.relative_to(D).as_posix(),sha256=H(mp3.read_bytes()),textSha256=H(t['text']),duration=duration,cues=cues,voice=voices[t['language']],rate='natural delivery, playback 1.0x',provenance=dict(provider='Qwen open-source, local CPU synthesis',model='Qwen3-TTS-12Hz-1.7B-CustomVoice',modelRevision=revision,libraryVersion='0.1.1',voice=voices[t['language']],voiceKind='built-in synthetic; no voice cloning',instructions=style[t['language']],captionTiming='Measured paragraph boundaries; proportional short cues within each paragraph, not word-level alignment'))
 print('TRACK_COMPLETE',stem,round(duration,1),flush=True)
g=json.loads((D/'data/guide-audio.json').read_text());g.update(source='Qwen3-TTS-12Hz-1.7B-CustomVoice',tracks=[t for t in tracks if 'stop'in t],inspectionTracks=[t for t in tracks if 'flaw'in t],voiceReview='Serena Chinese and Aiden English; local synthetic voices. Paragraph boundaries measured; short cue timing interpolated. See narration audit for independent recognition review.')
(D/'data/guide-audio.json').write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n');(D/'data/inspection-audio.json').write_text(json.dumps(g['inspectionTracks'],ensure_ascii=False,indent=2)+'\n')
print('QWEN_GUIDES_COMPLETE',len(tracks),flush=True)
