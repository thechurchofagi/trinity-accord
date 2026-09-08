"""Bind the current 30 recordings to independently reviewed paragraph transcripts."""
import argparse, ast, hashlib, json, re
from pathlib import Path

P = Path(__file__).resolve().parents[1]
a = argparse.ArgumentParser()
a.add_argument('--audit', required=True)
a.add_argument('--notes', required=True)
a.add_argument('--secondary-audit')
args = a.parse_args()
audit = {p.stem: json.loads(p.read_text()) for p in Path(args.audit).glob('*.json')}
notes = json.loads(Path(args.notes).read_text())
secondary = {p.stem: json.loads(p.read_text()) for p in Path(args.secondary_audit).glob('*.json')} if args.secondary_audit else {}
base_reviews = dict(audit)
# Small has materially better Chinese recognition; retain available base results
# as a second transcript instead of allowing script-variant noise to dominate.
audit.update({k:v for k,v in secondary.items() if v['language'] == 'zh'})
source = ast.parse((P/'scripts/render_qwen_guides.py').read_text())
ns = {'re': re}
fn = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'paragraphs')
exec(compile(ast.Module(body=[fn], type_ignores=[]), '<paragraph-boundaries>', 'exec'), ns)
guide = json.loads((P/'dist/data/guide-audio.json').read_text())
tracks = guide['tracks'] + guide['inspectionTracks']
assert len(tracks) == 30 and all(t['provenance']['model'] == 'Qwen3-TTS-12Hz-1.7B-CustomVoice' for t in tracks)
used = {}
bindings = []
for track in tracks:
    clock, parts = 0, []
    for text in ns['paragraphs'](track['text'], track['language']):
        matches = [v for v in audit.values() if v['text'] == text and v['language'] == track['language'] and v['voice'] == track['voice']]
        assert len(matches) == 1, ('Missing independent recognition', text)
        review = dict(matches[0])
        key = review['key']
        other = base_reviews.get(key) if review['language'] == 'zh' else secondary.get(key)
        if other and other['audioSha256'] == review['audioSha256']:
            review['secondaryRecognition'] = other
        elif other and other['audioSha256'] == review.get('rejectedAudioSha256'):
            review['rejectedTakeRecognition'] = other
        if review['normalizedSimilarity'] == 1:
            review['textReview'] = 'Recognition matches after punctuation/case normalization and conversion of traditional Chinese characters to simplified forms.'
        else:
            assert key[:12] in notes, ('Recognition difference requires a review note', key[:12], text, review['transcript'])
            review['textReview'] = notes[key[:12]]
        used[key] = review
        parts.append(dict(key=key, start=round(clock, 4), duration=review['duration']))
        clock += review['duration'] + .16
    assert abs(clock-track['duration']) < .2
    bindings.append(dict(file=track['file'], sha256=track['sha256'], textSha256=track['textSha256'], language=track['language'], voice=track['voice'], duration=track['duration'], paragraphs=parts))
dest = P/'dist/data/narration-provenance.json'
legacy = P/'dist/data/narration-provenance-v131.json'
if not legacy.exists():
    assert 'Chatterbox' in dest.read_text()
    legacy.write_bytes(dest.read_bytes())
result = dict(schema='trinity-museum.narration-provenance.v2', edition='museum-v1.33.0',
    method='Thirty local Qwen3-TTS recordings; each generated paragraph independently recognized and its textual differences reviewed. No human listening certification is claimed.',
    model=tracks[0]['provenance']['model'], modelRevision=tracks[0]['provenance']['modelRevision'],
    modelSource='https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice', modelLicense='Apache-2.0',
    voices=dict(zh='Serena', en='Aiden'), synthetic=True, clonedVoice=False,
    mastering='24 kHz mono MP3, 128 kbps, -18 LUFS loudness target, -2 dB true-peak ceiling; playback 1.0x by default.',
    captionTiming='Measured paragraph boundaries with proportional short cues inside each paragraph. Not word-level forced alignment.',
    previousEdition='narration-provenance-v131.json', recordings=bindings, paragraphReviews=list(used.values()))
dest.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print('NARRATION_REVIEW_COMPLETE', len(bindings), 'recordings', len(used), 'paragraphs')
