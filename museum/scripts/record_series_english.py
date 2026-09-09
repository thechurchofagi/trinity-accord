"""Produce the English voice; align_guide_captions.py supplies shared bilingual word captions."""
import argparse,hashlib,json,os,re,subprocess,time
from pathlib import Path
# All model files are local. Opt out of dependency telemetry before inference.
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
os.environ['GRADIO_ANALYTICS_ENABLED']='False'
os.environ['DO_NOT_TRACK']='1'
os.environ['HF_HUB_OFFLINE']='1'
import sys
import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel
assert "onnxruntime" not in sys.modules, "Apply the documented lazy ONNX dependency patch before 12Hz synthesis"
P=Path(__file__).resolve().parents[1];D=P/'dist'
ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('--cache',required=True);args=ap.parse_args()
cache=Path(args.cache);cache.mkdir(parents=True,exist_ok=True)
oldfile=P/'history/guide-audio-v136.json'
if not oldfile.exists():oldfile.write_bytes((D/'data/guide-audio.json').read_bytes())
old=json.loads(oldfile.read_text());stops=json.loads((P/'scene/tour-script.json').read_text())
H=lambda b:hashlib.sha256(b.encode() if isinstance(b,str) else b).hexdigest()
revision='0c0e3051f131929182e2c023b9537f8b1c68adfe'
style='A thoughtful museum guide, warm and calm, with clear natural conversational pacing. Read exactly the supplied text.'
reuse={t['text']:t for t in old['tracks'] if t['language']=='en'}
tracks=[];jobs={}
for i,s in enumerate(stops):
 if s['en'] in reuse:tracks.append(dict(reuse[s['en']],stop=i));continue
 sentences=re.findall(r'.+?(?:[.!?](?=\s|$)|$)',s['en']);parts=[];cur=''
 for sentence in sentences:
  if cur and len(cur)+len(sentence)>240:parts.append(cur.strip());cur=''
  cur+=sentence
 if cur.strip():parts.append(cur.strip())
 t=dict(stop=i,language='en',text=s['en'],parts=[])
 for text in parts:
  key=H(json.dumps([revision,'Aiden',style,text],ensure_ascii=False));j=dict(key=key,text=text);jobs[key]=j;t['parts'].append(j)
 tracks.append(t)
pending=[j for j in jobs.values() if not (cache/(j['key']+'.wav')).exists()]
print('ENGLISH_PLAN',len(tracks),'tracks',len(pending),'paragraphs',flush=True)
torch.set_num_threads(6);torch.manual_seed(42)
model=Qwen3TTSModel.from_pretrained(args.model,device_map='cpu',dtype=torch.bfloat16,attn_implementation='sdpa') if pending else None
assert "onnxruntime" not in sys.modules, "Unexpected ONNX dependency during 12Hz model loading"
for i,j in enumerate(pending):
 start=time.monotonic();print('BEGIN',i+1,j['text'][:55],flush=True)
 waves,sr=model.generate_custom_voice(text=j['text'],language='English',speaker='Aiden',instruct=style,max_new_tokens=1200)
 wav=waves[0];assert np.isfinite(wav).all() and sr<len(wav)<sr*90
 sf.write(cache/(j['key']+'.wav'),wav,sr,subtype='PCM_16')
 (cache/(j['key']+'.json')).write_text(json.dumps(dict(j,duration=len(wav)/sr),ensure_ascii=False)+'\n')
 print('DONE',i+1,'/',len(pending),'wall',round(time.monotonic()-start,1),'audio',round(len(wav)/sr,1),flush=True)
del model
out=D/'assets/guides-qwen-v137-en';out.mkdir(exist_ok=True)
for t in tracks:
 if 'parts' not in t:continue
 samples=[];cues=[];clock=0
 for j in t.pop('parts'):
  wav,sr=sf.read(cache/(j['key']+'.wav'),dtype='float32');dur=len(wav)/sr;samples.extend([wav,np.zeros(int(sr*.16),dtype=np.float32)])
  pieces=[];cur=''
  for unit in re.findall(r'\S+\s*',j['text']):
   if cur and len(cur+unit)>68:pieces.append(cur.strip());cur=''
   cur+=unit
  if cur.strip():pieces.append(cur.strip())
  weights=[len(re.sub(r'\s','',v)) for v in pieces];local=0
  for text,w in zip(pieces,weights):
   end=local+(dur-.04)*w/sum(weights);cues.append(dict(start=round(clock+local,4),end=round(clock+end,4),text=text));local=end
  clock+=dur+.16
 stem='stop-'+str(t['stop'])+'-en';wavpath=cache/(stem+'.wav');sf.write(wavpath,np.concatenate(samples),sr,subtype='PCM_16');mp3=out/(stem+'.mp3')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(wavpath),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','24000','-ac','1','-b:a','128k',str(mp3)],check=True)
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(mp3)]))
 t.update(file=mp3.relative_to(D).as_posix(),sha256=H(mp3.read_bytes()),textSha256=H(t['text']),duration=duration,cues=cues,voice='Aiden',rate='natural delivery, playback 1.0x',provenance=dict(provider='Qwen open-source, local CPU synthesis',model='Qwen3-TTS-12Hz-1.7B-CustomVoice',modelRevision=revision,voice='Aiden',voiceKind='built-in synthetic; no voice cloning',dependencyPatchSha256=H((P/'scripts/qwen-0.1.1-lazy-onnx.patch').read_bytes()),instructions=style,captionTiming='Measured paragraph boundaries, proportional short cues; not word-level alignment'))
old.update(edition='museum-v1.37.0',tracks=tracks,inspectionTracks=[t for t in old['inspectionTracks'] if t['language']=='en'],languageEditions={'audio':'en','subtitles':['en','zh-Hans']},voiceReview='English voice edition. Run recognition review and acoustic bilingual caption alignment before publication; no human listening certification is claimed.')
(D/'data/guide-audio.json').write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n')
print('ENGLISH_COMPLETE',sum(t['duration'] for t in tracks),flush=True)
