#!/usr/bin/env python3
"""Restore the exact recorded TH/RB release sources; does not perform new semantic review."""
import argparse,base64,hashlib,io,json,lzma,pathlib,tarfile

def main():
    p=argparse.ArgumentParser();p.add_argument('--parts',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parent/'capsule');p.add_argument('--output',type=pathlib.Path,default=pathlib.Path('restored_TH_RB'));a=p.parse_args()
    index=json.loads((a.parts/'PARTS.json').read_text());chunks=[]
    for row in index['parts']:
        b=(a.parts/row['file']).read_bytes()
        if hashlib.sha256(b).hexdigest()!=row['sha256']:raise ValueError('Part hash mismatch')
        chunks.append(b''.join(b.split()))
    blob=base64.b64decode(b''.join(chunks),validate=True)
    if hashlib.sha256(blob).hexdigest()!=index['compressed_sha256']:raise ValueError('Compressed capsule mismatch')
    raw=lzma.decompress(blob)
    if len(raw)!=index['uncompressed_tar_bytes']:raise ValueError('Unexpected tar length')
    out=a.output.resolve()
    if out.exists() and any(out.iterdir()):raise ValueError('Refuse to overwrite nonempty output')
    out.mkdir(parents=True,exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as t:
        for m in t:
            rel=pathlib.PurePosixPath(m.name)
            if not m.isfile() or rel.is_absolute() or '..' in rel.parts or m.size>5000000:raise ValueError('Unsafe capsule member')
            dst=out.joinpath(*rel.parts);dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_bytes(t.extractfile(m).read())
    for row in json.loads((out/'CAPSULE_MANIFEST.json').read_text()):
        b=(out/row['path']).read_bytes()
        if len(b)!=row['bytes'] or hashlib.sha256(b).hexdigest()!=row['sha256']:raise ValueError('Member mismatch: '+row['path'])
    print('Verified restoration:',out)
    print('Read README_ZH.md. The expanded offline ZIP already contains the exact baseline; for Git-only recovery restore the previous UCT-MAP-v1.0.0 graph/ledger before code/build_release.py. Restoration is not a new audit.')
if __name__=='__main__':main()
