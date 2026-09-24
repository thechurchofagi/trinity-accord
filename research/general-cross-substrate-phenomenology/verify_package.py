#!/usr/bin/env python3
import json,re,subprocess,sys,tempfile
from pathlib import Path
from publication_common import ROOT,STEM,VERSION,validate_local_package
expected,digest=validate_local_package();pub=ROOT/'published'
md=(pub/f'{STEM}-v{VERSION}.md').read_text()
if re.search(r'[\u4e00-\u9fff]',md):raise RuntimeError('Unexpected non-English content')
if 'No DOI has been assigned' in md:raise RuntimeError('Unresolved DOI')
for n in range(1,28):
 if not re.search(r'^'+str(n)+r'\. ',md,re.M):raise RuntimeError('Missing reference '+str(n))
with tempfile.TemporaryDirectory() as t:
 out=Path(t)/'results.json'
 subprocess.run([sys.executable,str(pub/'gcp_checks.py'),'--output',str(out)],check=True,stdout=subprocess.DEVNULL)
 if json.loads(out.read_text())!=json.loads((pub/'gcp_results.json').read_text()):raise RuntimeError('Reproduction mismatch')
print('PASS: exact reviewed package, 27 references, English only, finite constructions reproduced; manifest',digest)
