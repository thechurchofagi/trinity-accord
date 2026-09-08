"""Offline narration production. Built-in synthetic voices only, no identity cloning.
OpenAI is used only when an existing key is available. Otherwise run the pinned
MIT-licensed Chatterbox Turbo model on the build runner, never in the browser.
"""
import argparse,difflib,gc,hashlib,json,os,re,subprocess,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--stop',type=int,required=True);p.add_argument('--output',required=True);a=p.parse_args()
D=Path(__file__).resolve().parents[1]/'dist';out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
track=next(t for t in json.loads((D/'data/guide-audio.json').read_text())['tracks'] if t['stop']==a.stop and t['language']=='en');text=track['text'];stem=f'{a.stop:02d}-en';wav=out/(stem+'.wav');mp3=out/(stem+'.mp3')
H=lambda b:hashlib.sha256(b).hexdigest()
key=os.environ.get('OPENAI_API_KEY','').strip()
if key:
 engine='gpt-4o-mini-tts-2025-12-15';voice='cedar'
 body=dict(model=engine,voice=voice,input=text,response_format='wav',speed=1,instructions='A warm, thoughtful museum guide speaking to one attentive visitor. Natural conversational English, clear but never robotic. Ask the opening question with genuine curiosity. Use subtle emphasis and breath, not theatrical gravity or salesmanship. About 145 words per minute. Read exactly the supplied words; no additions or sound effects.')
 request=urllib.request.Request('https://api.openai.com/v1/audio/speech',json.dumps(body).encode(),{'Authorization':'Bearer '+key,'Content-Type':'application/json'})
 with urllib.request.urlopen(request,timeout=180) as r:wav.write_bytes(r.read())
 provenance=dict(provider='OpenAI',model=engine,voice=voice,voiceKind='built-in synthetic',instructions=body['instructions'])
else:
 import numpy as np,soundfile as sf,torch
 from huggingface_hub import snapshot_download
 from chatterbox.tts_turbo import ChatterboxTurboTTS
 torch.set_num_threads(3);torch.manual_seed(4200+a.stop)
 revision='1e4698ca7cbb41ff030c4185f0927a3b42d76924'
 model_dir=snapshot_download('ResembleAI/chatterbox-turbo',revision=revision,allow_patterns=['ve.safetensors','t3_turbo_v1.safetensors','s3gen_meanflow.safetensors','conds.pt','*.json','*.txt'])
 model=ChatterboxTurboTTS.from_local(model_dir,'cpu');rate=model.sr
 # Short paragraphs, rather than individual words, preserve connected prosody.
 sentences=re.split(r'(?<=[.!?])\s+',text);chunks=[];current=''
 for sentence in sentences:
  if current and len(current)+len(sentence)>260:chunks.append(current);current=''
  current=(current+' '+sentence).strip()
 if current:chunks.append(current)
 samples=[]
 for i,chunk in enumerate(chunks):
  print(f'NARRATION {a.stop}: paragraph {i+1}/{len(chunks)}',flush=True)
  audio=model.generate(chunk,temperature=.65,top_p=.9,repetition_penalty=1.2).squeeze().numpy()
  assert len(audio)>rate and np.isfinite(audio).all(),'Invalid generated audio'
  samples.extend([audio,np.zeros(round(rate*.22),dtype=np.float32)])
 sf.write(wav,np.concatenate(samples),rate,subtype='PCM_16')
 provenance=dict(provider='Resemble AI open-source model, offline CPU inference',model='Chatterbox Turbo 350M',voice='bundled default conditionals',voiceKind='built-in synthetic; no user or third-party reference recording',modelRevision=revision,libraryRevision='5de7a54aa4e5e2baadb0182dde554908b48b85c2',license='MIT',watermark='PerTh applied by upstream generator',temperature=.65,topP=.9)
 del model,samples;gc.collect()
# Loudness-normalise narration only; original songs and evidence are untouched.
subprocess.run(['ffmpeg','-y','-v','error','-i',str(wav),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','24000','-ac','1','-b:a','128k',str(mp3)],check=True)
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(mp3)]))
from faster_whisper import WhisperModel
recognizer=WhisperModel('base.en',device='cpu',compute_type='int8',cpu_threads=3,num_workers=1)
segments,info=recognizer.transcribe(str(mp3),beam_size=5,language='en',word_timestamps=True,condition_on_previous_text=False,initial_prompt='Trinity Accord. Core Object Alpha. Guardian Principles. Anthropic. Redwood Research. GPT four. Bitcoin. Ethereum.')
words=[w for seg in segments for w in seg.words];transcript=' '.join(w.word.strip() for w in words)
normal=lambda w:re.sub(r'[^a-z0-9]','',w.lower())
original=list(re.finditer(r'\S+',text));expected=[normal(m.group()) for m in original];actual=[normal(w.word) for w in words]
matcher=difflib.SequenceMatcher(None,expected,actual,autojunk=False);matched={}
for block in matcher.get_matching_blocks():
 for i in range(block.size):matched[block.a+i]=words[block.b+i]
ratio=len(matched)/len(expected);print(f'NARRATION {a.stop}: {duration:.2f}s; recognised exact-word coverage {ratio:.3f}',flush=True)
# Proper names/numeral spelling may differ. Record every unmatched token rather
# than falsely describing ASR interpolation as exact forced alignment.
assert ratio>=.78,('Narration recognition requires review',a.stop,ratio,transcript)
intervals=[]
for i,m in enumerate(original):
 if i in matched:start,end=matched[i].start,matched[i].end
 else:
  prev=max((k for k in matched if k<i),default=-1);nxt=min((k for k in matched if k>i),default=len(original));lo=matched[prev].end if prev>=0 else 0;hi=matched[nxt].start if nxt<len(original) else duration-.12
  step=max(.001,hi-lo)/(nxt-prev);start=lo+(i-prev-1)*step;end=lo+(i-prev)*step
 start=max(intervals[-1][1] if intervals else 0,start);end=max(start+.001,end);intervals.append((start,min(duration-.01,end)))
cues=[];i=0
while i<len(original):
 j=i+1
 while j<len(original) and original[j].end()-original[i].start()<=64 and not re.search(r'[.!?]$',original[j-1].group()):j+=1
 cues.append(dict(start=round(intervals[i][0],3),end=round(intervals[j-1][1],3),text=text[original[i].start():original[j-1].end()]))
 i=j
track.update(file='assets/guides-expressive/'+mp3.name,sha256=H(mp3.read_bytes()),bytes=mp3.stat().st_size,duration=duration,textSha256=H(text.encode()),cues=cues,voice=provenance['voice'],rate='natural delivery, playback 1.0x',provenance=provenance)
track['captionAudit']=dict(method='Whisper base.en word timestamps mapped to source text; unmatched spellings interpolated between recognised neighbours',recognisedExactWordCoverage=ratio,unmatchedSourceWords=[m.group() for i,m in enumerate(original) if i not in matched],transcript=transcript,humanListeningReview=False)
(out/(stem+'.json')).write_text(json.dumps(track,ensure_ascii=False,indent=2)+'\n');wav.unlink()
print('NARRATION_COMPLETE',a.stop,provenance['model'],mp3.stat().st_size,flush=True)
