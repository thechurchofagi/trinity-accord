#!/usr/bin/env python3
"""Recover exact UCT-MAP-v1.1.1 capsule; authenticity only, not renewed scientific proof."""
import argparse,hashlib,io,json,lzma,pathlib,tarfile
EXPECTED='f4604377a3c6dca5de56bf71883006a03dbf290b7f92af2136e682087ff7bfc3'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--capsule',type=pathlib.Path,default=pathlib.Path(__file__).with_name('UCT_MAP_v1.1.1_Capsule.tar.xz'));ap.add_argument('--output',type=pathlib.Path,default=pathlib.Path('UCT_MAP_v1_1_1_restored'));args=ap.parse_args()
 raw=args.capsule.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=EXPECTED:raise RuntimeError('Capsule hash mismatch')
 payload=lzma.decompress(raw);out=args.output.resolve()
 if out.exists() and any(out.iterdir()):raise RuntimeError('Refuse overwrite nonempty path')
 out.mkdir(parents=True,exist_ok=True)
 with tarfile.open(fileobj=io.BytesIO(payload),mode='r:') as arc:
  for m in arc:
   path=pathlib.PurePosixPath(m.name)
   if not m.isfile() or path.is_absolute() or '..' in path.parts or m.size>9_000_000:raise ValueError('Unsafe archive member: '+m.name)
   dest=out.joinpath(*path.parts);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(arc.extractfile(m).read())
 rows=json.loads((out/'CAPSULE_MEMBER_MANIFEST.json').read_text())
 assert len(rows)==32
 for row in rows:
  body=(out/row['path']).read_bytes()
  if hashlib.sha256(body).hexdigest()!=row['sha256'] or len(body)!=row['bytes']:raise ValueError('Member failed verification: '+row['path'])
 print('UCT-MAP-v1.1.1 capsule restored and all',len(rows),'source members matched. No empirical truth inferred.')
if __name__=='__main__':main()
