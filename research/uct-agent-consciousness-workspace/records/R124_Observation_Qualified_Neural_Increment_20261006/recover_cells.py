"""Recover the pinned public Cells archive; signed redirect URLs stay private."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse, hashlib, json, time, urllib.request, urllib.error, zipfile

SIZE = 1929137550
MD5 = '3b0ab5c964fb492ec36ee0f55a5d53de'
SHA256 = 'e23a5c281b828c5d9545576ebc9197f37dbc20bd16c616aa2eda55d220fe9494'
SOURCE = 'https://ndownloader.figshare.com/files/58773835'

def digest(path):
    m, h = hashlib.md5(), hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(8*1024*1024), b''):
            m.update(b); h.update(b)
    return m.hexdigest(), h.hexdigest()

def main():
    p = argparse.ArgumentParser(); p.add_argument('--data',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True); p.add_argument('--manifest',type=Path,required=True)
    a=p.parse_args(); a.data.mkdir(parents=True,exist_ok=True); a.output.mkdir(parents=True,exist_ok=True)
    start=time.monotonic(); archive=a.data/'Cells.zip'; ledger=[]
    if not archive.exists():
        req=urllib.request.Request(SOURCE+'?download=1&request_time='+str(time.time_ns()),headers={'Range':'bytes=0-1023'})
        with urllib.request.urlopen(req,timeout=40) as r:
            if r.status != 206 or r.headers.get('Content-Range') != f'bytes 0-1023/{SIZE}':
                raise ValueError('Unexpected initial range response')
            if not r.read(1024).startswith(b'PK'): raise ValueError('Not ZIP data')
            private_redirect=r.url
        parts=a.data/'parts'; parts.mkdir(exist_ok=True)
        block=32*1024*1024; n=(SIZE+block-1)//block
        def fetch(i):
            lo=i*block; hi=min(SIZE,lo+block)-1; out=parts/f'{i:03d}.part'
            if out.exists() and out.stat().st_size == hi-lo+1:
                return {'part':i,'status':'resumed','bytes':out.stat().st_size}
            for attempt in range(2):
                try:
                    fresh_source=SOURCE+f'?part={i}&retry={attempt}&r={time.time_ns()}'
                    req=urllib.request.Request(fresh_source,headers={'Range':f'bytes={lo}-{hi}'})
                    with urllib.request.urlopen(req,timeout=50) as r:
                        if r.status != 206 or r.headers.get('Content-Range') != f'bytes {lo}-{hi}/{SIZE}':
                            raise ValueError('Range response mismatch')
                        with out.open('wb') as f:
                            while b:=r.read(1024*1024): f.write(b)
                    if out.stat().st_size != hi-lo+1: raise ValueError('Part length mismatch')
                    return {'part':i,'status':'downloaded','bytes':out.stat().st_size,'attempts':attempt+1}
                except Exception as e:
                    if attempt==1: raise RuntimeError(f'part {i}: {type(e).__name__}') from None
        with ThreadPoolExecutor(max_workers=4) as pool:
            futures=[pool.submit(fetch,i) for i in range(n)]
            total=0; last=time.monotonic()
            for fu in as_completed(futures):
                item=fu.result(); ledger.append(item); total+=item['bytes']
                if time.monotonic()-last>=10 or total==SIZE:
                    print(json.dumps({'event':'download_progress','bytes':total,'percent':round(100*total/SIZE,1)}),flush=True)
                    last=time.monotonic()
        temp=a.data/'Cells.zip.partial'
        with temp.open('wb') as f:
            for i in range(n):
                expected_part=min(SIZE,(i+1)*block)-i*block
                if (parts/f'{i:03d}.part').stat().st_size!=expected_part:
                    raise ValueError(f'Part changed after transfer: {i}')
                with (parts/f'{i:03d}.part').open('rb') as src:
                    while b:=src.read(8*1024*1024): f.write(b)
        temp.rename(archive)
    m,h=digest(archive)
    if archive.stat().st_size!=SIZE or m!=MD5 or h!=SHA256: raise ValueError('Archive digest mismatch')
    print(json.dumps({'event':'archive_verified','bytes':SIZE,'sha256':h}),flush=True)
    manifest=json.loads(a.manifest.read_text()); expected={s['file']:s for s in manifest['sessions']}
    dest=a.data/'Cells'; dest.mkdir(exist_ok=True); session_ledger=[]
    with zipfile.ZipFile(archive) as z:
        members={Path(v.filename).name:v for v in z.infolist()
                 if v.filename.endswith('.mat') and not Path(v.filename).name.startswith('._')}
        if set(members)!=set(expected): raise ValueError('Unexpected session identities')
        for name,s in expected.items():
            target=dest/name
            if not target.exists() or target.stat().st_size!=s['bytes']:
                with z.open(members[name]) as src,target.open('wb') as out:
                    while b:=src.read(8*1024*1024): out.write(b)
            _,sh=digest(target)
            if target.stat().st_size!=s['bytes'] or sh!=s['sha256']: raise ValueError('Session digest mismatch: '+name)
            session_ledger.append({'file':name,'bytes':s['bytes'],'sha256':sh,'verified':True})
            print(json.dumps({'event':'session_verified','file':name}),flush=True)
    report={'status':'VERIFIED','source':SOURCE,'archive_bytes':SIZE,'archive_md5':m,'archive_sha256':h,'parts':ledger,'sessions':session_ledger,'elapsed_seconds':time.monotonic()-start,'signed_urls_recorded':False}
    (a.output/'raw_recovery.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'event':'recovery_complete','sessions':len(session_ledger),'elapsed_seconds':report['elapsed_seconds']}),flush=True)

if __name__=='__main__': main()
