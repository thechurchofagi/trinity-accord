"""Local-only model pipeline; audio hashes bind resumable caches to inputs."""
import os, pathlib, json, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[2]
CACHE=pathlib.Path(os.environ.get('MUSEUM_LYRICS_CACHE',str(pathlib.Path.home()/'.cache/trinity-lyrics')))
CACHE.mkdir(parents=True,exist_ok=True)
os.environ.setdefault('HF_HUB_DISABLE_XET','1')
ITEMS=json.loads((ROOT/'dist/data/lyrics-source.json').read_text())['items']
selection=os.environ.get('MUSEUM_LYRICS_IDS','').split(',')
if selection!=['']:ITEMS=[e for e in ITEMS if e['exhibitId'] in selection]
if not ITEMS:raise RuntimeError('No matching audio tracks')
for item in ITEMS:
 audio=ROOT/'dist'/item['audioFile']
 if hashlib.sha256(audio.read_bytes()).hexdigest()!=item['audioSha256']:raise RuntimeError('Audio hash mismatch: '+item['exhibitId'])
binding=CACHE/'input-binding.json';old=json.loads(binding.read_text()) if binding.exists() else {}
for item in ITEMS:
 key=item['exhibitId'];digest=item['audioSha256']
 if key in old and old[key]!=digest:raise RuntimeError('Audio changed. Use a fresh cache for '+key)
 old[key]=digest
binding.write_text(json.dumps(old,indent=2)+'\n')
