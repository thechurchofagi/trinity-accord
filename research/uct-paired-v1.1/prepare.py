#!/usr/bin/env python3
"""Assemble reviewed sources and retain provenance; no publication or credentials."""
from pathlib import Path
import base64,difflib,hashlib,io,json,subprocess,zipfile,zlib
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
P=ROOT/'package'
B_COMMIT='4cfddb377aa585a3447f140ec92fc55163181d4e'
A_SHA='ee74a633c098a37142dcf80e5bf2a11ce8018661b81a153da1523ee8ffddfc8e'
B_SHA='89c36d96909ff7124ca4985b5f743a859da5d412182335d8d7e8f49bb15bf909'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data if isinstance(data,bytes) else data.encode())
def show(commit,path):
    return subprocess.check_output(['git','show',commit+':'+path],cwd=REPO)
def main():
    subprocess.run(['git','fetch','--depth=1','--no-tags','origin',B_COMMIT],cwd=REPO,check=True)
    bbase='research/unified-consciousness-theory-ii/published/'
    old=show(B_COMMIT,bbase+'unified-consciousness-theory-ii-v1.0.md')
    write(P/'baselines/source-b-v1.0.md',old)
    zipbytes=show(B_COMMIT,bbase+'unified-consciousness-theory-ii-audit-bundle-v1.0.zip')
    if sha(zipbytes)!='78e3feb6f0db32d47e41ef671771cb92a77517a0ae4c49a6070f3bdb05b94228':
        raise RuntimeError('Original B audit ZIP digest mismatch')
    archive=zipfile.ZipFile(io.BytesIO(zipbytes));names=set()
    for item in archive.infolist():
        if item.is_dir():continue
        name=Path(item.filename).name
        if name in names or not name or item.file_size>2_000_000:raise RuntimeError('Invalid archived member')
        names.add(name);write(P/'baselines/B_v1.0_audit'/name,archive.read(item))
    if len(names)!=15:raise RuntimeError('Unexpected B audit membership')
    trace=zlib.decompress(base64.b64decode((P/'baselines/source-trace-v0.54.zlib.b64').read_text(),validate=False))
    if sha(trace)!='a7ab735a3dcee366a870cd0439fcfc721100f3f95dfea0eb97651b4dfdfc81d9':
        raise RuntimeError('Restored historical ledger digest mismatch')
    write(P/'baselines/source-trace-v0.54.md',trace)
    edits=[]
    for part in ('b-edits-1.json','b-edits-2.json'):
        q=json.loads((P/part).read_text())
        if sha(old)!=q['source_sha256']:raise RuntimeError('B baseline digest mismatch')
        edits+=q['edits']
    lines=old.decode().splitlines(keepends=True)
    ordered=sorted(edits,key=lambda e:(e['start'],e['end']))
    for prev,nxt in zip(ordered,ordered[1:]):
        if prev['end']>nxt['start']:raise RuntimeError('Overlapping source edits')
    for e in reversed(ordered):lines[e['start']:e['end']]=e['text'].splitlines(keepends=True)
    b=''.join(lines).encode()
    write(P/'manuscripts/source-b-before-link-fix.md',b)
    if sha(b)!=q['result_sha256']:raise RuntimeError('B edited source digest mismatch')
    text=b.decode();wrong='[doi:__A_DOI__.](https://doi.org/__A_DOI__.)'
    if text.count(wrong)!=1:raise RuntimeError('Companion DOI punctuation fix target mismatch')
    b=text.replace(wrong,'[doi:__A_DOI__](https://doi.org/__A_DOI__).').encode()
    write(P/'manuscripts/source-b.md',b)
    chunks=sorted((P/'source-parts').glob('a*.md'))
    if len(chunks)!=7:raise RuntimeError('A source requires exactly seven parts')
    # Comparing build-1 bytes with the reviewed local manuscript identified
    # exactly two extra terminal blank lines at text-transfer chunk boundaries.
    # Remove only those exact bytes; retain the original whole-source hash gate.
    normalized=[]
    for x in chunks:
        data=x.read_bytes()
        if x.name in ('a01.md','a06refs.md'):
            if not data.endswith(b'\n\n\n'):raise RuntimeError('Transfer boundary changed')
            data=data[:-1]
        normalized.append(data)
    a=b''.join(normalized);write(P/'manuscripts/source-a.md',a)
    report={'a_sha256':sha(a),'a_expected':A_SHA,'b_sha256':sha(b),'b_expected':B_SHA,
            'source_b_v1_sha256':sha(old),'source_b_commit':B_COMMIT,
            'source_b_audit_zip_sha256':sha(zipbytes),'restored_source_trace_sha256':sha(trace),
            'transfer_normalization':'One extra trailing newline removed from each of a01.md and a06refs.md; reviewed full-source digest unchanged.',
            'a_parts':{x.name:sha(x.read_bytes()) for x in chunks},
            'baselines':{str(x.relative_to(P)):sha(x.read_bytes()) for x in sorted((P/'baselines').rglob('*')) if x.is_file()},
            'state':'PASS' if sha(a)==A_SHA and sha(b)==B_SHA else 'FAIL'}
    write(P/'audit/source-provenance.json',json.dumps(report,indent=2)+'\n')
    write(P/'audit/b-revision.diff',''.join(difflib.unified_diff(old.decode().splitlines(True),b.decode().splitlines(True),fromfile='B-v1.0-published',tofile='B-v1.1-template')))
    apub=REPO/'research/unified-consciousness-theory-i/published/unified-consciousness-theory-i-v1.0.md'
    if apub.is_file():
        write(P/'baselines/source-a-v1.0.md',apub.read_bytes())
        write(P/'audit/a-revision.diff',''.join(difflib.unified_diff(apub.read_text().splitlines(True),a.decode().splitlines(True),fromfile='A-v1.0-published',tofile='A-v1.1-template')))
    print(json.dumps({k:v for k,v in report.items() if k not in ('baselines','a_parts')},indent=2))
    if report['state']!='PASS':raise RuntimeError('Source transfer failed integrity check')
    for script in ('check_rc4.py','check_transformations.py','reproduce_shared_models.py'):
        subprocess.run(['python3',str(P/'verification'/script)],cwd=P,check=True)
    da=json.loads((ROOT/'deposit-a.json').read_text());db=json.loads((ROOT/'deposit-b.json').read_text())
    if da['version']!='1.1' or db['version']!='1.1':raise RuntimeError('Wrong reserved edition')
    subprocess.run(['python3',str(P/'build.py'),'--a-doi',da['doi'],'--b-doi',db['doi']],cwd=P,check=True)
if __name__=='__main__':main()
