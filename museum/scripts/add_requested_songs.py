"""Recover the four author-requested NFT pairs from the pinned CAR inventory.

Run once against the edition before v1.23.0. Originals are copied, never rewritten.
"""
from pathlib import Path
import concurrent.futures, hashlib, io, json, re, subprocess, tempfile, urllib.request
from PIL import Image
from prepare_sources import extract

P = Path(__file__).resolve().parents[1]
R = P.parent
D = P / 'dist'
COMMIT = '62de6d3913157800e0e04e7f8a8262cfe5cf5a7e'
H = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_text())
def write(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

choices = {
    27: ('时间对齐', 'Timeline Alignment', 'Super Intelligence'),
    103: ('Unspoken', 'Unspoken', 'Unspoken'),
    115: ('方生方死', 'Square Souls', 'Square Souls'),
    151: ('The Oracle', 'The Oracle', 'The Oracle'),
}
sources = read(D / 'data/sources.json')
assert not {f'eth-{n:03}' for n in choices} & {e['id'] for e in sources['items']}, 'Already added'
index = read(R / 'nft-text-descriptions/chronicle-index.json')['entries']
cars = read(R / 'nft-text-descriptions/nft-cars-manifest.json')['files']
entries, jobs = [], []
for row in index:
    n = row['ordinal']
    if n not in choices:
        continue
    eid = f'eth-{n:03}'
    display, english, song = choices[n]
    source_path = 'nft-text-descriptions/' + row['file']
    raw = subprocess.check_output(['git', 'show', COMMIT + ':' + source_path], cwd=R)
    text = raw.decode()
    if n == 27:
        lyrics = text.split('Lyrics:\n', 1)[1].split('Principle of Time Alignment:', 1)[0].strip()
    else:
        start = re.search(r'^' + re.escape(song) + r'\s*$', text, re.I | re.M)
        assert start, eid
        lyrics = re.split(r'^-{5,}\s*$', text[start.start():], maxsplit=1, flags=re.M)[0].strip()
    lyrics = '\n'.join(line.rstrip() for line in lyrics.splitlines())
    assert len(lyrics.splitlines()) > 20 and 'The ASIMilestones Legacy' not in lyrics
    (D / f'data/records/{eid}.md').write_bytes(raw)
    entry = dict(id=eid, ordinal=n, title=row['name'], displayTitle=display, en=english,
        songTitle=song, date=row['datetime'], contract=row['contract'], tokenId=row['token_id'],
        block=row['block'], sourceCommit=COMMIT, sourcePath=source_path, sourceSha256=H(raw),
        sourceUrl=f'https://github.com/thechurchofagi/trinity-accord/blob/{COMMIT}/{source_path}',
        tokenUrl=f"https://etherscan.io/nft/{row['contract']}/{row['token_id']}",
        localRecord=f'data/records/{eid}.md', lyrics=lyrics, media=[],
        audioStatus=dict(state='own_recording', recordingExhibit=eid))
    entries.append(entry)
    matches = [m for m in cars if m['role'] == 'media' and m['contract'].lower() == row['contract'].lower() and m['token_id'] == row['token_id']]
    assert len(matches) == 2, eid
    jobs.extend((eid, m) for m in matches)

def recover(job):
    eid, m = job
    url = 'https://arweave.net/' + m['txid']
    car = urllib.request.urlopen(url, timeout=90).read()
    assert H(car) == m['sha256'], 'CAR digest mismatch'
    raw, present, count = extract(car, dict(root_cid=m['cid'], leaf_path=m['leaf']))
    kind = 'image' if m['leaf'].startswith('image.') else 'audio'
    file = 'assets/' + eid + ('.webp' if kind == 'image' else '.mp3')
    dst = D / file
    assert not dst.exists(), file
    extra = {}
    if kind == 'image':
        im = Image.open(io.BytesIO(raw)); im.load()
        extra['sourceDimensions'] = list(im.size)
        im.thumbnail((2048, 2048)); im.convert('RGB').save(dst, 'WEBP', quality=94)
        processing = 'Complete original image fitted within 2048px, WebP quality 94; no cropping or generative editing.'
    else:
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(raw); tmp.flush()
            subprocess.run(['ffmpeg', '-v', 'error', '-i', tmp.name, '-vn', '-codec:a', 'libmp3lame', '-b:a', '128k', str(dst)], check=True)
        extra['duration'] = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', str(dst)]))
        processing = 'Complete original recording transcoded to MP3 128 kbps; no trimming or remix.'
    print(eid, kind, extra.get('duration', extra.get('sourceDimensions')), flush=True)
    return eid, dict(kind=kind, file=file, sha256=H(dst.read_bytes()), bytes=dst.stat().st_size,
        originalFileSha256=H(raw), originalFileBytes=len(raw), arweaveUrl=url,
        carSha256=H(car), indexedRootCid=m['cid'], indexedRootPresentInCar=present,
        verifiedCarBlocks=count, leafPath=m['leaf'], processing=processing,
        verificationScope='CAR and included block SHA-256 checks; no fresh chain consensus or metadata binding claim.', **extra)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    for eid, media in pool.map(recover, jobs):
        next(e for e in entries if e['id'] == eid)['media'].append(media)
assert all({m['kind'] for m in e['media']} == {'image', 'audio'} for e in entries)
sources['items'].extend(entries)
write(D / 'data/sources.json', sources)
write(P / 'scene/requested-songs-results.json', entries)
print('Four original image/audio pairs recovered and verified.', flush=True)
