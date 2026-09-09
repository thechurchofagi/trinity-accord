"""Checkpoint acoustic word observations for newly recovered recordings.

These are recognition drafts for review, not historical lyric replacements.
"""
import argparse,dataclasses,hashlib,json,time
from pathlib import Path
from faster_whisper import WhisperModel
P=Path(__file__).resolve().parents[1];D=P/'dist'
a=argparse.ArgumentParser();a.add_argument('--cache',required=True);args=a.parse_args();cache=Path(args.cache);cache.mkdir(parents=True,exist_ok=True)
sources=json.loads((D/'data/sources.json').read_text())['items']
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=2,download_root=str(cache/'models'))
for number in [97,122,84,24,51,60,112,127]:
 e=next(e for e in sources if e['id']==f'eth-{number:03}');m=next(m for m in e['media'] if m['kind']=='audio');out=cache/(e['id']+'.json')
 if out.exists() and json.loads(out.read_text()).get('audioSha256')==m['sha256']:continue
 start=time.monotonic();print('BEGIN',e['id'],flush=True)
 segments,info=model.transcribe(str(D/m['file']),word_timestamps=True,beam_size=5,vad_filter=False,condition_on_previous_text=False,initial_prompt='Song lyrics. AGI. ASI.')
 data=dict(exhibitId=e['id'],audioSha256=m['sha256'],duration=m['duration'],language=info.language,segments=[dataclasses.asdict(s) for s in segments],method='Faster Whisper small multilingual CPU int8; acoustic word timestamps; review draft')
 out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('DONE',e['id'],data['language'],len(data['segments']),round(time.monotonic()-start,1),flush=True)
