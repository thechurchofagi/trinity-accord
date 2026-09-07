from common import ROOT, CACHE, ITEMS
import pathlib,json,re,time,hashlib,numpy as np
from rapidfuzz.distance import Levenshtein
root=ROOT;cache=CACHE
pipeline_hash=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
labels=json.loads((cache/'lyrics-ctc/labels.json').read_text());vocab={c:i for i,c in enumerate(labels)}
def letters(s):return re.sub("[^A-Z']",'',s.upper().replace('’',"'"))
def align(em, times, lines):
 words=[];tokens=[];owners=[];ranges=[]
 for li,line in enumerate(lines):
  for text in line['text'].split():
   tt=letters(text)
   if not tt:
    if words and words[-1]['line']==li:words[-1]['text']+=' '+text
    else:raise ValueError('Leading punctuation needs transcript normalization')
    continue
   wi=len(words);words.append({'text':text,'line':li});ranges.append((line['start']-3,line['end']+3))
   if tokens:tokens.append(vocab['|']);owners.append(-1)
   for c in tt:tokens.append(vocab[c]);owners.append(wi)
 # Standard CTC expanded states: blank, token, blank, token, ...
 states=np.zeros(2*len(tokens)+1,dtype=np.int32);states[1::2]=tokens;owners2=np.full(len(states),-1);owners2[1::2]=owners
 skip=np.zeros(len(states),bool);skip[2:]=(states[2:]!=0)&(states[2:]!=states[:-2])
 lo=np.full(len(states),-1e6);hi=np.full(len(states),1e6)
 for s,owner in enumerate(owners2):
  if owner>=0:lo[s],hi[s]=ranges[owner]
 previous=np.full(len(states),-1e10,dtype=np.float32);previous[0]=0
 trace=np.empty((len(em),len(states)),np.uint8)
 for t,frame in enumerate(em):
  one=np.r_[-1e10,previous[:-1]];two=np.r_[[-1e10,-1e10],previous[:-2]];two[~skip]=-1e10
  chosen=(one>previous).astype(np.uint8);best=np.maximum(previous,one);better=two>best;chosen[better]=2;best=np.maximum(best,two)
  # Broad ASR line windows discourage a repeated phrase from jumping verses.
  penalty=np.maximum(lo-times[t],0)+np.maximum(times[t]-hi,0)
  previous=best+frame[states]-np.minimum(penalty*.8,20);trace[t]=chosen
 s=len(states)-1 if previous[-1]>previous[-2] else len(states)-2;path=np.empty(len(em),np.int32)
 for t in range(len(em)-1,-1,-1):path[t]=s;s-=int(trace[t,s])
 for wi,w in enumerate(words):
  mask=owners2[path]==wi;idx=np.flatnonzero(mask)
  if not len(idx):raise ValueError('No CTC path for '+w['text'])
  w.update(start=round(max(0,float(times[idx[0]])-.01),3),end=round(float(times[idx[-1]])+.01,3),acousticScore=round(float(np.exp(em[idx,states[path[idx]]]).mean()),4))
 return words
items=list(ITEMS)
for e in items:
 p=cache/'lyrics-ctc'/(e['exhibitId']+'.npz');src=cache/'lyrics-sung'/(e['exhibitId']+'.json')
 if not p.exists() or not src.exists():raise RuntimeError('Missing acoustic/transcript cache: '+e['exhibitId'])
 f=root/'dist/data/lyrics'/(e['exhibitId']+'.json')
 if f.exists() and f.stat().st_mtime>max(p.stat().st_mtime,src.stat().st_mtime) and json.loads(f.read_text()).get('alignment',{}).get('pipelineSha256')==pipeline_hash:continue
 t=time.time();raw=np.load(p);d=json.loads(src.read_text());ws=align(raw['emission'],raw['times'],d['lines']);lines=[]
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
 data={'schemaVersion':'word-alignment-v2','exhibitId':e['exhibitId'],'audioFile':e['audioFile'],'audioSha256':e['audioSha256'],'duration':e['duration'],'sourceLyricsSha256':e['sourceTextSha256'],'alignment':{'pipelineSha256':pipeline_hash,'engine':'wav2vec2-base-960h CTC Viterbi','transcriptEngine':'faster-whisper small.en int8 + source reconciliation','audioInput':'demucs htdemucs vocals' if (cache/'lyrics-vocals'/(e['exhibitId']+'.wav')).exists() else 'original recording','device':'cpu','timestampResolution':.02,'modelFrameResolutionIsNotAccuracy':True,'manualListeningReviewed':False,'reviewRequiredLines':sum(bool(l['reviewFlags']) for l in lines)},'lines':lines}
 f.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(e['exhibitId'],len(ws),'words',data['alignment']['reviewRequiredLines'],'flagged lines',round(time.time()-t,1),'sec',flush=True)
