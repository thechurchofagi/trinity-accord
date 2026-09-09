"""Bind independent paragraph recognition to the English recordings in this edition."""
import argparse, hashlib, json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--takes', required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
path = root / 'dist/data/guide-audio.json'
data = json.loads(path.read_text())
reviews = [json.loads(p.read_text()) for p in (Path(args.takes) / 'review').glob('*.json')]
exceptions = {
    '7a2b7d329baa4fff775223b6049145c231d9b3af01806832742d6e9222e994ef':
        'Recognition renders spoken years and twenty as digits and o1 as 01; comparison identifies no omitted words.',
    'fa829d7653b799a8ea33cfe2887b00cfa8d7e6e581ea2ccc64d0026f67c3b38a':
        'Recognition renders the spoken clock as digits and spells DeepSeek as DeepSeq; this is a text comparison, not a pronunciation certification.'
}
items = []
for track in data['tracks']:
    if track['language'] != 'en' or not track['file'].startswith('assets/guides-qwen-v137-en/'):
        continue
    parts = sorted((r for r in reviews if r['text'] in track['text']), key=lambda r: track['text'].index(r['text']))
    if ''.join(r['text'] for r in parts).replace(' ', '') != track['text'].replace(' ', ''):
        raise ValueError('Incomplete recognition review for stop ' + str(track['stop']))
    for review in parts:
        if review['similarity'] < .99 and review['key'] not in exceptions:
            raise ValueError('Unresolved recognition difference: ' + review['key'])
        review['comparisonNote'] = exceptions.get(review['key'], 'Text comparison found no substantive omission; punctuation or minor transcription differences may remain.')
    item = dict(stop=track['stop'], audioSha256=track['sha256'], textSha256=track['textSha256'], paragraphs=parts)
    items.append(item)
    track['recognitionReview'] = dict(file='data/guide-review-v137-en.json', stop=track['stop'], manualListeningReviewed=False)
report = dict(edition='museum-v1.37.0', engine='Faster Whisper small multilingual CPU int8', scope='Independent recognition and script comparison for newly generated English paragraphs. Exact-text reused recordings retain their earlier reviews.', manualListeningReviewed=False, items=items)
target = root / 'dist/data/guide-review-v137-en.json'
target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
data['voiceReview'] = 'New English paragraphs have independent recognition and script comparison. Numeric rendering and DeepSeek transcription differences are documented. This is not human listening or aesthetic certification. The preceding complete Chinese route and matching recordings are retained.'
data['englishRecognitionReview'] = dict(file='data/guide-review-v137-en.json', sha256=hashlib.sha256(target.read_bytes()).hexdigest())
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
print(len(items), 'new recordings reviewed;', sum(len(i['paragraphs']) for i in items), 'paragraphs')
