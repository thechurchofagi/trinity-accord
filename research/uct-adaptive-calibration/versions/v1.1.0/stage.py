#!/usr/bin/env python3
"""Extract EXACT author-frozen preprint assets from the pinned source package.

Recompilation is prohibited for this release. The proof of identity is the
full original ZIP SHA256 and three exact member checksums.
"""
from pathlib import Path
import hashlib, json, zipfile
BASE=Path(__file__).resolve().parent
ZIP='Adaptive_Consequence_Calibration_DOI_Preparation_v1.1.0.zip'
MANUSCRIPT='Learning_What_to_Preserve_v1.1.0.md'
PDF='Learning_What_to_Preserve_v1.1.0.pdf'
PACKAGE_HASH='90c65558fd168996241876d45a3b66c038eb351d8242e2d77e08df0bc82beda5'
EXPECTED={
 PDF:(410208,'20671c736396b95070ccd7be1af989de4e8ceef987bc6ae531ca1d5dda003f16'),
 MANUSCRIPT:(70093,'b909666f526dada17c5cedd1f7b87f2c83a411a64d1c37b51727c7a3176093bb'),
 ZIP:(2626447,PACKAGE_HASH)
}
def digest(b):return hashlib.sha256(b).hexdigest()
def check(name,b):
    size,sha=EXPECTED[name]
    if len(b)!=size or digest(b)!=sha:raise RuntimeError(f'Frozen publication identity mismatch: {name}')
    return {'name':name,'bytes':size,'sha256':sha}
def main():
    source=BASE/'source-package.zip'
    data=source.read_bytes()
    check(ZIP,data)
    out=[check(ZIP,data)]
    (BASE/ZIP).write_bytes(data)
    with zipfile.ZipFile(source,'r') as z:
        if z.testzip() is not None:raise RuntimeError('Corrupt archive member')
        prefix='Adaptive_Consequence_Calibration_v1.1.0/'
        for member,name in [(PDF,PDF),('manuscript.md',MANUSCRIPT)]:
            b=z.read(prefix+member)
            out.append(check(name,b))
            (BASE/name).write_bytes(b)
        manifest=json.loads(z.read(prefix+'publication/EXPECTED_ARTIFACTS.json'))
        row={item['path']:item for item in manifest['files']}
        for member,name in [(PDF,PDF),('manuscript.md',MANUSCRIPT)]:
            if row[member]['sha256']!=EXPECTED[name][1] or row[member]['bytes']!=EXPECTED[name][0]:
                raise RuntimeError('Bundle publication manifest differs from pinned source')
    receipt=json.loads((BASE/'PREPUBLICATION_RECEIPT.json').read_text())
    if {f['path'] for f in receipt['files']}!=set(EXPECTED):raise RuntimeError('Publication identity file set changed')
    print(json.dumps({'state':'EXACT_FROZEN_ARTIFACTS_PASS','report':'UCT-GD-2026-01',
          'version':'1.1.0','files':out},indent=2),flush=True)
if __name__=='__main__':main()
