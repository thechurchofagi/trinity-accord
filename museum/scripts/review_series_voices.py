"""Independent, resumable recognition review of completed Qwen paragraph takes."""
import argparse,json,re
from pathlib import Path
from difflib import SequenceMatcher
from faster_whisper import WhisperModel
p=argparse.ArgumentParser();p.add_argument('--takes',required=True);p.add_argument('--models',required=True);a=p.parse_args();root=Path(a.takes);out=root/'review';out.mkdir(exist_ok=True)
model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=2,download_root=a.models,local_files_only=True)
norm=lambda t:re.sub(r'[^a-z0-9]','',t.lower())
for meta in sorted(root.glob('*.json')):
 d=json.loads(meta.read_text());wav=meta.with_suffix('.wav');target=out/meta.name
 if not wav.exists() or target.exists():continue
 seg,info=model.transcribe(str(wav),language='en',beam_size=5,condition_on_previous_text=False)
 heard=' '.join(s.text.strip() for s in seg);score=SequenceMatcher(None,norm(d['text']),norm(heard),autojunk=False).ratio()
 result={'key':d['key'],'text':d['text'],'recognized':heard,'similarity':round(score,4),'manualListeningReviewed':False,'reviewRequired':score<.92}
 target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(round(score,3),d['text'][:60],flush=True)
