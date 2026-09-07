from common import ROOT, CACHE, ITEMS
import torch,torchaudio,pathlib,time,json,numpy as np,subprocess
root=ROOT;out=(CACHE/'lyrics-ctc');out.mkdir(exist_ok=True)
items=list(ITEMS);items.sort(key=lambda e:(e['exhibitId'] not in ['eth-103','eth-151','eth-115'],e['exhibitId']))
torch.set_num_threads(3);b=torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
print('loading wav2vec2 base',flush=True);m=b.get_model();m.eval();(out/'labels.json').write_text(json.dumps(b.get_labels()))
for e in items:
 p=out/(e['exhibitId']+'.npz')
 if p.exists():continue
 vf=(CACHE/'lyrics-vocals')/(e['exhibitId']+'.wav')
 if not vf.exists():raise RuntimeError('Run vocals.py first: '+e['exhibitId'])
 raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(vf),'-f','f32le','-ar','16000','-ac','1','pipe:1'])
 wav=np.frombuffer(raw,dtype=np.float32).copy(); pieces=[];times=[];t=time.time()
 # Keep central 10s of 12s contexts, preserving actual frame centers.
 for a in range(0,len(wav),160000):
  lo=max(0,a-16000);hi=min(len(wav),a+176000)
  with torch.inference_mode():em,_=m(torch.from_numpy(wav[lo:hi])[None]);em=torch.log_softmax(em[0],dim=-1).numpy()
  centers=(np.arange(len(em))*320+199.5+lo)/16000
  keep=(centers>=a/16000)&(centers<min(a+160000,len(wav))/16000)
  pieces.append(em[keep]);times.append(centers[keep])
 np.savez_compressed(p,emission=np.concatenate(pieces),times=np.concatenate(times),sampleRate=16000)
 print(e['exhibitId'],len(wav)/16000,round(time.time()-t,1),flush=True)
