"""Import inspected offline voice artifacts by text hash, never by stale stop order."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess
p=argparse.ArgumentParser();p.add_argument('--first',required=True);p.add_argument('--retakes',required=True);a=p.parse_args()
P=Path(__file__).resolve().parents[1];D=P/'dist';H=lambda b:hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
manifest=read(D/'data/guide-audio.json');assert len(manifest['tracks'])==16
archive=P/'history/guide-audio-v1.32-edge.json'
if not archive.exists():write(archive,manifest)
folder=D/'assets/guides-expressive';folder.mkdir(exist_ok=True)
first=Path(a.first);retakes=Path(a.retakes);audit=[]
for old_index in range(8):
 stem=f'{old_index:02}-en';root=retakes if old_index in [1,2,3,6] else first
 metadata=root/(stem+'.json');audio=root/(stem+'.mp3');t=read(metadata)
 assert H(audio.read_bytes())==t['sha256'];assert t['language']=='en';assert t['provenance']['model']=='Chatterbox Turbo 350M'
 candidates=[i for i,x in enumerate(manifest['tracks']) if x['language']=='en' and x['textSha256']==t['textSha256']];assert len(candidates)==1
 ix=candidates[0];previous=manifest['tracks'][ix];assert previous['text']==t['text'];t['stop']=previous['stop']
 # Retakes were already trimmed. First takes use the last aligned source word,
 # with a small tail retained, not any recognised model/ASR postamble.
 target=folder/f"{t['stop']:02}-en.mp3";end=min(t['duration'],t['cues'][-1]['end']+.22)
 before=t['sha256']
 if root==first and t['duration']>end+.05:
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(audio),'-t',str(end),'-af',f'afade=t=out:st={max(0,end-.035)}:d=0.035','-ar','24000','-ac','1','-b:a','128k',str(target)],check=True)
  t['provenance']['endTrim']='Last aligned source word plus 220ms; 35ms terminal fade. Diagnostic transcript is pre-trim.'
 else:shutil.copyfile(audio,target)
 t.update(file=str(target.relative_to(D)),sha256=H(target.read_bytes()),bytes=target.stat().st_size,duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(target)])))
 assert t['cues'][-1]['end']<t['duration'];assert t['textSha256']==H(t['text'].encode())
 t['provenance']['sourceArtifactRun']=34173946588 if root==retakes else 34173312397;t['provenance']['sourceAudioSha256']=before
 audit.append(dict(stop=t['stop'],file=t['file'],sha256=t['sha256'],duration=t['duration'],provenance=t['provenance'],captionAudit=t['captionAudit']))
 manifest['tracks'][ix]=t
manifest['defaultPlaybackRate']=1.0
manifest['voiceReview']='English uses newly generated Chatterbox Turbo built-in synthetic voice; four passages re-recorded after acoustic review. English captions map audio-derived recognition to the exact script, with spelling gaps recorded. Chinese remains Xiaoxiao. No human-listening certification or voice-identity cloning.'
write(D/'data/guide-audio.json',manifest)
write(D/'data/narration-provenance.json',dict(schema='trinity-museum.narration-provenance.v1',edition='museum-v1.32.0',aiGenerated=True,boundary='2026 curatorial narration only; not historical NFT audio.',method=manifest['voiceReview'],tracks=sorted(audit,key=lambda x:x['stop']),modelSource='https://huggingface.co/ResembleAI/chatterbox-turbo',codeSource='https://github.com/resemble-ai/chatterbox/tree/5de7a54aa4e5e2baadb0182dde554908b48b85c2'))
path=D/'museum.js';s=path.read_text().replace('Xiaoxiao（中文）与 Aria（英文）','Xiaoxiao（中文）与 Chatterbox Turbo（英文，生成式合成声音）').replace('Xiaoxiao (Chinese) and Aria (English)','Xiaoxiao (Chinese) and Chatterbox Turbo (English, generative synthetic voice)').replace("tx('中文导览','ENGLISH GUIDE')","tx('中文导览 · AI 合成','ENGLISH GUIDE · AI VOICE')")
s=s.replace('d=Math.max(1.5,view.distance)','d=Math.max(1.25,view.distance)').replace('new THREE.Vector3(p.x,p.y+.38,p.z+d)','new THREE.Vector3(p.x+.22,p.y+.38,p.z+d)')
s=s.replace("if(position.index===0)roomView();", "if(position.index===0||s.room===3)roomView();")
s=s.replace('new THREE.Vector3(x,y,roomIndex===0?20:z-12)','new THREE.Vector3(x,roomIndex===3?y+1.6:y,roomIndex===0?20:z-12)')
s=s.replace("let began=false;const begin=()=>{if(!began&&request===inspectionRequest){began=true;if(!touring){playGuide(-1);}}};", "let began=false;const begin=()=>{if(!began&&request===inspectionRequest){began=true;if(!touring){playGuide(-1);}else{$('caption-text').textContent='';$('tour-caption').hidden=true;}}};")
s=s.replace("${link('./data/space-design.json',", "${link('./data/narration-provenance.json',tx('合成配音来源与字幕校对','AI narration provenance and caption audit'))}${link('./data/space-design.json',")
path.write_text(s)
path=D/'tour-plan.js';s=path.read_text();start=s.index('export const tourStops=')+len('export const tourStops=');end=s.index(';\nexport const tourDuration',start);stops=json.loads(s[start:end]);stops[4]['cameraShots']=[dict(at=12,exhibit='canon-1'),dict(at=40,exhibit='canon-2'),dict(at=66,exhibit='canon-3')];path.write_text(s[:start]+json.dumps(stops,ensure_ascii=False,indent=2)+s[end:])
for t in manifest['tracks']:
 stop=stops[t['stop']];assert t['duration']<stop.get('musicAt',stop['seconds']),'Narration exceeds its station'
# Keep a source-linked audition page, not a second museum or a second codebase.
parts=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Narration review · Trinity Accord</title><style>body{max-width:800px;margin:3rem auto;padding:0 1.5rem;font:18px/1.6 system-ui;background:#101e28;color:#edf2ed}article{padding:1rem 0;border-bottom:1px solid #49606b}audio{width:100%}a{color:#a9deef}</style><h1>English narration / 英文导览配音</h1><p>AI-generated Chatterbox Turbo narration, using a built-in synthetic voice. Not a historical artwork recording. 2026 策展配音，不是原始作品音轨。</p><p><a href="./">Return to the museum / 返回博物馆</a> · <a href="data/narration-provenance.json">Provenance and acoustic review / 来源与校对</a></p>']
import html
for t in sorted((t for t in manifest['tracks'] if t['language']=='en'),key=lambda t:t['stop']):parts.append(f'<article><h2>{t["stop"]+1:02} · {html.escape(stops[t["stop"]]["exhibit"])}</h2><audio controls preload="none" src="{html.escape(t["file"])}"></audio><p>{html.escape(t["text"])}</p></article>')
parts.append('</html>');(D/'voice-review.html').write_text('\n'.join(parts))
p=P/'README.md';s=p.read_text();s=s.replace('The new guide uses newly synthesized Edge voices, not the proposed OpenAI voice candidates.','The final English guide uses Chatterbox Turbo built-in synthetic voice, with four acoustically reviewed retakes and regenerated captions; Chinese uses Xiaoxiao. No OpenAI voice is claimed.');p.write_text(s+'\nThe listening review page is `dist/voice-review.html`. Per-track provider, model revision, text/audio hashes, acoustic transcript and caption limitations are in `dist/data/narration-provenance.json`.\n')
p=P/'history/CHANGELOG.md';s=p.read_text();s='''## Final staging and narration acceptance

- Correct sRGB/linear lighting, denoise architectural light only, seal both doorway footprints, shift the crystal exit away from its background, enlarge the three Originals, and replace the bright waiting ring with a side reading stand.
- Preserve chronology in the short tour: mirror record before anniversary, no long musical backtrack. Introduce the high Canon room before approaching each of its three separate text panels. Keep the 540-second presentation budget and unobstructed closing sky.
- Replace all eight English guide recordings with Chatterbox Turbo 350M built-in generative synthetic voice. Retake four passages after inspecting audio-derived transcripts, regenerate captions, retain explicit interpolation/recognition limitations, and document AI origin. Chinese and the six manual-inspection recordings remain separate. This is not a claim of human-listening certification.

'''+s;s=s.replace('OpenAI voice audition remains an explicitly uncompleted production choice.','The later final staging section above records the adopted Chatterbox Turbo replacement.');p.write_text(s)
print('ADOPTED_EXPRESSIVE_NARRATION',[(t['stop'],round(t['duration'],2)) for t in audit],flush=True)
