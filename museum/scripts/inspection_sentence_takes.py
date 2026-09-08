"""Offline sentence-level speech retakes with bounded acoustic acceptance."""
import argparse,json,re,hashlib,subprocess
from pathlib import Path
import numpy as np,torch,soundfile as sf,librosa
from huggingface_hub import snapshot_download
from chatterbox.tts_turbo import ChatterboxTurboTTS
from faster_whisper import WhisperModel
p=argparse.ArgumentParser();p.add_argument('--flaw',type=int,required=True);p.add_argument('--output',required=True);a=p.parse_args()
D=Path(__file__).resolve().parents[1]/'dist';out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
t=next(x for x in json.loads((D/'data/guide-audio.json').read_text())['inspectionTracks'] if x['language']=='en' and x['flaw']==a.flaw)
torch.set_num_threads(3)
revision='1e4698ca7cbb41ff030c4185f0927a3b42d76924';local=snapshot_download('ResembleAI/chatterbox-turbo',revision=revision,allow_patterns=['ve.safetensors','t3_turbo_v1.safetensors','s3gen_meanflow.safetensors','conds.pt','*.json','*.txt'])
model=ChatterboxTurboTTS.from_local(local,'cpu');sr=model.sr;recognizer=WhisperModel('small.en',device='cpu',compute_type='int8',cpu_threads=3,num_workers=1)
norm=lambda s:re.findall(r'[a-z]+',s.lower().replace('’',"'").replace("flaw's",'flaws'))
parts=[];cues=[];reports=[];offset=0
for i,sentence in enumerate(re.split(r'(?<=[.!?])\s+',t['text'])):
 for attempt in range(4):
  seed=15000+a.flaw*100+i*4+attempt;torch.manual_seed(seed);y=model.generate(sentence,temperature=.5,top_p=.9,repetition_penalty=1.2).squeeze().numpy()
  segs,_=recognizer.transcribe(librosa.resample(y,orig_sr=sr,target_sr=16000),language='en',beam_size=5,word_timestamps=True,condition_on_previous_text=False,vad_filter=True)
  words=[w for seg in segs for w in seg.words];transcript=' '.join(w.word.strip() for w in words);expected=norm(sentence);actual=norm(transcript)
  print('SENTENCE_CHECK',a.flaw,i,attempt,transcript,flush=True)
  # Whitespace, punctuation and possessive segmentation are the only relaxations.
  if expected==actual:break
 else:raise RuntimeError(f'Sentence {i} not accepted after four takes; no manifest adopted')
 y=y[:min(len(y),round((words[-1].end+.14)*sr))];duration=len(y)/sr
 import difflib
 spans=list(re.finditer(r'\S+',sentence));indices={}
 # Preserve short complete source captions with acoustic first/last word times.
 cursor=0;first=0
 while first<len(spans):
  last=first+1
  while last<len(spans) and spans[last].end()-spans[first].start()<=64:last+=1
  lo=len(norm(sentence[:spans[first].start()]));hi=len(norm(sentence[:spans[last-1].end()]));token_times=[]
  for w in words:token_times.extend([(w.start,w.end)]*len(norm(w.word)))
  cues.append(dict(start=round(offset+token_times[lo][0],3),end=round(offset+token_times[hi-1][1],3),text=sentence[spans[first].start():spans[last-1].end()]));first=last
 reports.append(dict(sentence=sentence,transcript=transcript,seed=seed,attempt=attempt+1,accepted=True));parts.extend([y,np.zeros(round(sr*.18),dtype=np.float32)]);offset+=duration+.18
wav=out/f'inspection-{a.flaw}-en.wav';mp3=wav.with_suffix('.mp3');sf.write(wav,np.concatenate(parts),sr)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(wav),'-af','loudnorm=I=-18:TP=-2:LRA=7','-ar','24000','-ac','1','-b:a','128k',str(mp3)],check=True);wav.unlink()
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(mp3)]))
H=lambda b:hashlib.sha256(b).hexdigest();t.update(file='assets/guides-expressive/'+mp3.name,sha256=H(mp3.read_bytes()),bytes=mp3.stat().st_size,duration=duration,cues=cues,voice='Chatterbox Turbo built-in synthetic voice',textSha256=H(t['text'].encode()),provenance=dict(model='Chatterbox Turbo 350M',modelRevision=revision,voiceKind='built-in synthetic conditionals; no identity cloning',license='MIT',watermark='Upstream PerTh',delivery='24kHz MP3, original source words; separate accepted sentence takes'),captionAudit=dict(method='Whisper small.en exact normalized sentence checks and audio word times',sentences=reports,accepted=True,humanListeningReview=False))
mp3.with_suffix('.json').write_text(json.dumps(t,ensure_ascii=False,indent=2)+'\n');print('ALL_SENTENCES_ACCEPTED',a.flaw,duration,flush=True)
