"""Replace a checkpoint with a documented pronunciation take; retain rejected audio."""
import argparse, hashlib, json, shutil
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

a=argparse.ArgumentParser()
for name in ['model','cache','key','synthesis-text','reason']:
    a.add_argument('--'+name,required=True)
args=a.parse_args();cache=Path(args.cache)
paths=list(cache.glob(args.key+'*.json'));assert len(paths)==1
p=paths[0];job=json.loads(p.read_text());wavpath=p.with_suffix('.wav')
torch.set_num_threads(2);torch.manual_seed(7)
model=Qwen3TTSModel.from_pretrained(args.model,device_map='cpu',dtype=torch.bfloat16,attn_implementation='sdpa')
style='A thoughtful museum guide, warm and calm, with clear natural conversational pacing. Read exactly the supplied text.'
waves,sr=model.generate_custom_voice(text=args.synthesis_text,language='English',speaker=job['voice'],instruct=style,max_new_tokens=700)
wav=waves[0];assert np.isfinite(wav).all() and sr<len(wav)<sr*55
rejected=cache/'rejected';rejected.mkdir(exist_ok=True)
digest=hashlib.sha256(wavpath.read_bytes()).hexdigest()
shutil.copy2(wavpath,rejected/(job['key']+'-'+digest[:12]+'.wav'))
shutil.copy2(p,rejected/(job['key']+'-'+digest[:12]+'.json'))
sf.write(wavpath,wav,sr,subtype='PCM_16')
job.update(duration=len(wav)/sr,synthesisText=args.synthesis_text,retakeReason=args.reason,retakeSeed=7,rejectedAudioSha256=digest)
p.write_text(json.dumps(job,ensure_ascii=False)+'\n')
print('PRONUNCIATION_RETAKE',job['key'],job['duration'],flush=True)
