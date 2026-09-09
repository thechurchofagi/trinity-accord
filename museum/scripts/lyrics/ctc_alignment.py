"""Shared acoustic CTC alignment for recorded speech and songs."""
import re,numpy as np
def letters(s):return re.sub("[^A-Z']",'',s.upper().replace('’',"'"))
def align(em, times, lines, labels):
 vocab={c:i for i,c in enumerate(labels)}
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
