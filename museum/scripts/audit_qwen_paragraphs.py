"""Independent recognition of generated paragraphs; preserves differences for review."""
import argparse, hashlib, json, re, unicodedata
from pathlib import Path
from difflib import SequenceMatcher
from faster_whisper import WhisperModel

a = argparse.ArgumentParser()
a.add_argument('--cache', required=True)
a.add_argument('--output', required=True)
a.add_argument('--model', default='base')
a.add_argument('--keys', default='')
args = a.parse_args()
cache, output = Path(args.cache), Path(args.output)
output.mkdir(parents=True, exist_ok=True)
model = WhisperModel(args.model, device='cpu', compute_type='int8', cpu_threads=2)
def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKC', s).lower() if c.isalnum())
for source in sorted(cache.glob('*.json')):
    if args.keys and not any(source.stem.startswith(k) for k in args.keys.split(',')):
        continue
    job = json.loads(source.read_text())
    if 'key' not in job:
        continue
    wav = cache / (job['key'] + '.wav')
    digest = hashlib.sha256(wav.read_bytes()).hexdigest()
    report = output / source.name
    if report.exists() and json.loads(report.read_text()).get('audioSha256') == digest:
        continue
    segments, info = model.transcribe(str(wav), language=job['language'], beam_size=5,
        word_timestamps=True, condition_on_previous_text=False)
    rows = [dict(start=s.start, end=s.end, text=s.text,
        words=[dict(start=w.start, end=w.end, word=w.word, probability=w.probability) for w in s.words or []]) for s in segments]
    transcript = ''.join(s['text'] for s in rows).strip()
    score = SequenceMatcher(None, norm(job['text']), norm(transcript), autojunk=False).ratio()
    result = dict(job, audioSha256=digest, recognizer='faster-whisper/'+args.model+' CPU int8',
        transcript=transcript, normalizedSimilarity=round(score, 4), segments=rows,
        review='Automated recognition comparison; not human listening certification.')
    report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(dict(key=job['key'][:12], language=job['language'], similarity=round(score, 3),
        expected=job['text'] if score < .94 else None, recognized=transcript if score < .94 else None), ensure_ascii=False), flush=True)
