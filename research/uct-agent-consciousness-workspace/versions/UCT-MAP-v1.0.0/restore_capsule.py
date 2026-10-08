#!/usr/bin/env python3
"""Restore the fixed FA20261008 capsule; verifies hashes and rejects unsafe paths.
This materializes saved review decisions, not a fresh semantic certification.
"""
import argparse, base64, hashlib, io, json, lzma, pathlib, tarfile

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=pathlib.Path, default=pathlib.Path('restored_capsule'))
    args = ap.parse_args()
    root = pathlib.Path(__file__).resolve().parent
    parts = json.loads((root/'capsule'/'PARTS.json').read_text())
    chunks = []
    for p in parts:
        raw = (root/'capsule'/p['file']).read_bytes()
        if len(raw) != p['bytes'] or hashlib.sha256(raw).hexdigest() != p['sha256']:
            raise ValueError('Capsule part hash mismatch: '+p['file'])
        chunks.append(b''.join(raw.split()))
    compressed = base64.b64decode(b''.join(chunks), validate=True)
    if hashlib.sha256(compressed).hexdigest() != 'e5d7413f54c13664b127f0d31d5a4c5f8b507b7ba73c77000715cb653842e84d':
        raise ValueError('Compressed capsule hash mismatch')
    raw = lzma.decompress(compressed)
    if len(raw) != 430080:
        raise ValueError('Unexpected uncompressed archive size')
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output must be absent or empty; existing work will not be overwritten')
    out.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as archive:
        for member in archive.getmembers():
            name = pathlib.PurePosixPath(member.name)
            if not member.isfile() or name.is_absolute() or '..' in name.parts or member.size > 2000000:
                raise ValueError('Unsafe archive member: '+member.name)
            target = out.joinpath(*name.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as stream:
                target.write_bytes(stream.read())
    for record in json.loads((out/'MANIFEST.json').read_text()):
        raw = (out/record['path']).read_bytes()
        if len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('Restored file hash mismatch: '+record['path'])
    print('Verified capsule restored to', out)
    print('Read README.md; inspect rebuild_review.py before execution.')
    print('No actual or phenomenal premise is discharged by restoration.')

if __name__ == '__main__':
    main()
