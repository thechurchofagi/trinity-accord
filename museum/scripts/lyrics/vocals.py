from common import ROOT, CACHE, ITEMS
import pathlib,json,time,torch,numpy as np,subprocess,soundfile as sf
from demucs.pretrained import get_model
from demucs.apply import apply_model
root=ROOT
items=list(ITEMS);items.sort(key=lambda e:(e['exhibitId'] not in ['eth-103','eth-151','eth-115'],e['exhibitId']))
out=(CACHE/'lyrics-vocals');out.mkdir(exist_ok=True)
torch.set_num_threads(4)
print('Loading Demucs htdemucs',flush=True);m=get_model('htdemucs');m.eval()
for e in items:
 p=out/(e['exhibitId']+'.wav')
 if p.exists():continue
 t=time.time(); raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(root/'dist'/e['audioFile']),'-f','f32le','-ar',str(m.samplerate),'-ac','2','pipe:1'])
 wav=torch.from_numpy(np.frombuffer(raw,dtype=np.float32).copy().reshape(-1,2).T)
 ref=wav.mean(0);mean=ref.mean();std=ref.std();norm=(wav-mean)/std
 with torch.inference_mode(): stems=apply_model(m,norm[None],device='cpu',shifts=0,split=True,overlap=.25,progress=False)[0]
 vocal=stems[m.sources.index('vocals')]*std+mean
 temp=p.with_suffix('.partial.wav');sf.write(temp,vocal.T.numpy(),m.samplerate,subtype='FLOAT');temp.replace(p)
 print(e['exhibitId'],round(time.time()-t,1),'seconds',flush=True)
