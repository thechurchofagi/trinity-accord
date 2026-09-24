#!/usr/bin/env python3
"""Verify the frozen publication package and its reported finite results."""
import json,re,subprocess,sys
from publication_common import ROOT,validate_local_package
expected,digest=validate_local_package()
pub=ROOT/'published';md=(pub/'cross-substrate-phenomenal-comparison-v1.0.md').read_text()
code=re.search(r'```python\n(.*?)\n```',md,re.S).group(1)+'\n'
if code!=(pub/'transport_example.py').read_text(): raise RuntimeError('Appendix/script mismatch')
expected_results=json.loads((pub/'transport_results.json').read_text())
for flags in ([],['-O']):
 result=json.loads(subprocess.check_output([sys.executable,*flags,str(pub/'transport_example.py')],text=True))
 if result!=expected_results: raise RuntimeError('Reproduction failed')
reported=json.loads(re.search(r'### Executed output\n\n```json\n(.*?)\n```',md,re.S).group(1))
if reported!=expected_results: raise RuntimeError('Manuscript/results mismatch')
if 'DOI_PENDING' in md or 'has not been assigned a DOI' in md: raise RuntimeError('Unresolved DOI placeholder')
if re.search(r'[\u4e00-\u9fff]',md): raise RuntimeError('Unexpected Chinese manuscript text')
for n in range(1,17):
 if not re.search(r'^\['+str(n)+r'\]',md,re.M): raise RuntimeError('Missing reference')
print('PASS: exact reviewed files; all 16 references; English only; normal/optimized reproduction; manifest',digest)
