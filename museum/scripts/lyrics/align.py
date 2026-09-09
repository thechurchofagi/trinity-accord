from common import ROOT, CACHE, ITEMS
import pathlib,json,re,time,hashlib,numpy as np
from rapidfuzz.distance import Levenshtein
root=ROOT;cache=CACHE
pipeline_hash=hashlib.sha256((pathlib.Path(__file__).read_bytes()+pathlib.Path(__file__).with_name('ctc_alignment.py').read_bytes())).hexdigest()
labels=json.loads((cache/'lyrics-ctc/labels.json').read_text());vocab={c:i for i,c in enumerate(labels)}
from ctc_alignment import align, letters
items=list(ITEMS)
for e in items:
 p=cache/'lyrics-ctc'/(e['exhibitId']+'.npz');src=cache/'lyrics-sung'/(e['exhibitId']+'.json')
 if not p.exists() or not src.exists():raise RuntimeError('Missing acoustic/transcript cache: '+e['exhibitId'])
 f=root/'dist/data/lyrics'/(e['exhibitId']+'.json')
 if f.exists() and f.stat().st_mtime>max(p.stat().st_mtime,src.stat().st_mtime) and json.loads(f.read_text()).get('alignment',{}).get('pipelineSha256')==pipeline_hash:continue
 t=time.time();raw=np.load(p);d=json.loads(src.read_text());ws=align(raw['emission'],raw['times'],d['lines'],labels);lines=[]
 for i,source in enumerate(d['lines']):
  words=[{k:v for k,v in w.items() if k!='line'} for w in ws if w['line']==i]
  for w in words:w['end']=min(w['end'],e['duration'])
  # Compare shared ASR/reference words only; never fabricate missing boundaries.
  aw=source['asrWords'];ref=[letters(w['text']) for w in words];hyp=[letters(w['word']) for w in aw]
  for op in Levenshtein.opcodes(ref,hyp):
   if op.tag=='equal':
    for j,k in zip(range(op.src_start,op.src_end),range(op.dest_start,op.dest_end)):
     words[j]['asrStartDelta']=round(words[j]['start']-aw[k]['start'],3)
  flags=[]
  if source.get('unmatched'):flags.append('unmatched-transcript')
  if source['editRate']>.35:flags.append('transcript-disagreement')
  if any(w['acousticScore']<.12 for w in words):flags.append('weak-acoustic-evidence')
  if any(abs(w.get('asrStartDelta',0))>1.2 for w in words):flags.append('boundary-disagreement')
  lines.append({'text':source['text'],'sourceLine':source['sourceLine'],'start':words[0]['start'],'end':words[-1]['end'],'reviewFlags':flags,'words':words})
 data={'schemaVersion':'word-alignment-v2','exhibitId':e['exhibitId'],'audioFile':e['audioFile'],'audioSha256':e['audioSha256'],'duration':e['duration'],'sourceLyricsSha256':e['sourceTextSha256'],'alignment':{'pipelineSha256':pipeline_hash,'engine':'wav2vec2-base-960h CTC Viterbi','transcriptEngine':json.loads((cache/'lyrics-asr'/(e['exhibitId']+'.json')).read_text()).get('method','faster-whisper small.en int8 + source reconciliation'),'transcriptReview':d['review'],'audioInput':'demucs htdemucs vocals' if (cache/'lyrics-vocals'/(e['exhibitId']+'.wav')).exists() else 'original recording','device':'cpu','timestampResolution':.02,'modelFrameResolutionIsNotAccuracy':True,'manualListeningReviewed':False,'reviewRequiredLines':sum(bool(l['reviewFlags']) for l in lines)},'lines':lines}
 f.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(e['exhibitId'],len(ws),'words',data['alignment']['reviewRequiredLines'],'flagged lines',round(time.time()-t,1),'sec',flush=True)
