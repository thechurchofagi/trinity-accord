"""Align the single English voice to words, then attach reviewed Chinese sentences."""
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
import numpy as np
import torch, torchaudio
sys.path.insert(0, str(Path(__file__).parent / 'lyrics'))
from ctc_alignment import align

p = argparse.ArgumentParser(); p.add_argument('--cache', required=True); a = p.parse_args()
root = Path(__file__).resolve().parents[1]; dist = root / 'dist'; cache = Path(a.cache); cache.mkdir(exist_ok=True, parents=True)
manifest = dist / 'data/guide-audio.json'; data = json.loads(manifest.read_text())
translation_file = root / 'content/guide-translations.json'
translations = {i['id']: i['lines'] for i in json.loads(translation_file.read_text())['items']}
torch.set_num_threads(3)
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
model = bundle.get_model().eval(); labels = bundle.get_labels()
for track in data['tracks'] + data['inspectionTracks']:
    if track['language'] != 'en': continue
    key = 'stop-' + str(track['stop']) if 'stop' in track else 'flaw-' + str(track['flaw'])
    lines = translations[key]
    assert all(l['zh'] for l in lines)
    assert ' '.join(l['en'] for l in lines) == track['text']
    audio = dist / track['file']; assert hashlib.sha256(audio.read_bytes()).hexdigest() == track['sha256']
    target = cache / (track['sha256'] + '.npz')
    if not target.exists():
        raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(audio),'-f','f32le','-ar','16000','-ac','1','pipe:1'])
        wav = np.frombuffer(raw,dtype=np.float32).copy(); pieces=[]; times=[]
        for start in range(0,len(wav),160000):
            lo=max(0,start-16000); hi=min(len(wav),start+176000)
            with torch.inference_mode():
                emission,_=model(torch.from_numpy(wav[lo:hi])[None]); emission=torch.log_softmax(emission[0],dim=-1).numpy()
            centers=(np.arange(len(emission))*320+199.5+lo)/16000
            keep=(centers>=start/16000)&(centers<min(start+160000,len(wav))/16000)
            pieces.append(emission[keep]); times.append(centers[keep])
        np.savez_compressed(target,emission=np.concatenate(pieces),times=np.concatenate(times))
    # Existing measured cue spans provide broad search windows; the acoustic
    # model supplies word boundaries, never equal divisions of speech time.
    old=[]; cursor=0
    for cue in track['cues']:
        count=len(cue['text'].split()); old.append((cursor,cursor+count,cue)); cursor+=count
    inputs=[]; cursor=0
    for line in lines:
        count=len(line['en'].split()); covered=[c for lo,hi,c in old if lo<cursor+count and hi>cursor]
        assert covered
        inputs.append(dict(text=line['en'],start=covered[0]['start'],end=covered[-1]['end'])); cursor+=count
    raw=np.load(target); words=align(raw['emission'],raw['times'],inputs,labels); cues=[]
    for index,line in enumerate(lines):
        row=[{k:v for k,v in w.items() if k!='line'} for w in words if w['line']==index]
        for word in row: word['end']=min(word['end'],track['duration'])
        cues.append(dict(text=line['en'],textZh=line['zh'],start=row[0]['start'],end=row[-1]['end'],words=row))
    track['cues']=cues
    track.setdefault('provenance',{})['captionTiming']='Acoustic English word boundaries with Chinese sentence translations; shared music-caption rendering'
    track['captionAlignment']=dict(engine='wav2vec2-base-960h CTC Viterbi',audioInput='Delivered English narration MP3',audioSha256=track['sha256'],translationSha256=hashlib.sha256(translation_file.read_bytes()).hexdigest(),frameResolution=.02,manualListeningReviewed=False,weakAcousticWords=sum(w['acousticScore']<.12 for w in words))
    print(key,len(words),'aligned words',track['captionAlignment']['weakAcousticWords'],'weak acoustic words',flush=True)
data['tracks']=[t for t in data['tracks'] if t['language']=='en']
data['inspectionTracks']=[t for t in data['inspectionTracks'] if t['language']=='en']
data['languageEditions']={'audio':'en','subtitles':['en','zh-Hans']}
data['voiceReview']='One English Qwen Aiden voice for the whole tour and all three inspections. English acoustic word timing and reviewed Chinese sentence translations use the shared music-caption renderer. Independent recognition review covers new takes; no human listening certification is claimed.'
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('BILINGUAL_GUIDES_COMPLETE',len(data['tracks']),len(data['inspectionTracks']),flush=True)
