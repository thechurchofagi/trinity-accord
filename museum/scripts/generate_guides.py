"""Generate recorded guides from versioned room text using a supplied Kokoro model directory.
Usage: python scripts/generate_guides.py --model-dir /path/to/kokoro
Dependencies: kokoro-onnx, onnxruntime, numpy; ffmpeg on PATH.
Model weights are not bundled. The output manifest records their hashes.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, tempfile, wave
import numpy as np
import onnxruntime as rt
from kokoro_onnx import Kokoro
P=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--model-dir',required=True);args=ap.parse_args();b=Path(args.model_dir)
opts=rt.SessionOptions();opts.intra_op_num_threads=4;opts.inter_op_num_threads=1
k=Kokoro.from_session(rt.InferenceSession(str(b/'kokoro-v1.0.onnx'),sess_options=opts,providers=['CPUExecutionProvider']),str(b/'voices-v1.0.bin'))
manifest={'voice':'af_heart','language':'en-us','speed':0.88,'type':'AI-generated curatorial narration, not historical audio','modelSha256':hashlib.sha256((b/'kokoro-v1.0.onnx').read_bytes()).hexdigest(),'voicesSha256':hashlib.sha256((b/'voices-v1.0.bin').read_bytes()).hexdigest(),'tracks':[]}
for r in json.loads((P/'dist/data/rooms.json').read_text())['rooms']:
 text=r['narration'];parts=[];sr=24000
 for sentence in text.split('. '):
  a,sr=k.create(sentence.replace('NFT','N F T').replace('AI','A I').replace('AGI','A G I'),voice='af_heart',speed=.88,lang='en-us');parts.extend([a,np.zeros(int(sr*.25),dtype=np.float32)])
 a=np.concatenate(parts);peak=float(np.max(np.abs(a)));a=a*min(1,.94/max(peak,1e-6))
 with tempfile.TemporaryDirectory() as tmp:
  wav=Path(tmp)/'speech.wav'
  with wave.open(str(wav),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32767).astype('<i2').tobytes())
  dst=P/'dist/assets'/('guide-'+r['id']+'.mp3');subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-codec:a','libmp3lame','-b:a','80k',str(dst)],check=True)
 manifest['tracks'].append({'room':r['id'],'text':text,'file':'assets/'+dst.name,'duration':len(a)/sr,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()});print(r['id'],round(len(a)/sr,1),'seconds',flush=True)
(P/'dist/data/narration.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
