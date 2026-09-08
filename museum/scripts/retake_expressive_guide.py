"""Retake diagnostic tracks using the same synthetic voice, not a cloned identity."""
from pathlib import Path
import json,subprocess,hashlib
source=Path(__file__).with_name('render_expressive_guide.py').read_text()
source=source.replace('torch.manual_seed(4200+a.stop)','torch.manual_seed(9100+a.stop)')
source=source.replace('len(current)+len(sentence)>260','len(current)+len(sentence)>170 or current.endswith("?")')
source=source.replace('temperature=.65','temperature=.55').replace('temperature=.65,topP=.9','temperature=.55,topP=.9')
source=source.replace("WhisperModel('base.en'","WhisperModel('small.en'")
source=source.replace('condition_on_previous_text=False,initial_prompt=',"condition_on_previous_text=False,vad_filter=True,vad_parameters={'min_silence_duration_ms':350},initial_prompt=")
source=source.replace('Whisper base.en word timestamps','Whisper small.en word timestamps')
exec(compile(source,str(Path(__file__).with_name('render_expressive_guide.py')),'exec'),globals())
# Preserve all acoustic words (including insertions) for review, not only recall.
metadata=json.loads((out/(stem+'.json')).read_text())
metadata['captionAudit']['acousticWords']=[dict(text=w.word,start=w.start,end=w.end,probability=w.probability) for w in words]
metadata['captionAudit']['retake']=True
metadata['captionAudit']['sourceWordRecallIsNotAccuracy']=True
metadata['provenance']['seed']=9100+a.stop
# Avoid model postambles/trailing ASR hallucinations after the final source word.
end=min(metadata['duration'],metadata['cues'][-1]['end']+.22)
if metadata['duration']>end+.05:
 trimmed=out/(stem+'-trim.mp3')
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(mp3),'-t',str(end),'-af',f'afade=t=out:st={max(0,end-.035)}:d=0.035','-ar','24000','-ac','1','-b:a','128k',str(trimmed)],check=True)
 trimmed.replace(mp3)
 metadata['duration']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(mp3)]))
 metadata['sha256']=hashlib.sha256(mp3.read_bytes()).hexdigest();metadata['bytes']=mp3.stat().st_size
 metadata['provenance']['endTrim']='Final aligned source word plus 220 ms; 35 ms terminal fade; diagnostic transcript is pre-trim.'
(out/(stem+'.json')).write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
print('RETAKE_TRANSCRIPT',a.stop,transcript,flush=True)
