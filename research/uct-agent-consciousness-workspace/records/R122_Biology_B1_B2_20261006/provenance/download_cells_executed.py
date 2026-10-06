import urllib.request, urllib.error, json, time, hashlib, sys
from pathlib import Path
from urllib.parse import urlsplit

root=Path('/workspace/scratch/42800b14a096/data')
root.mkdir(exist_ok=True)
path=root/'Cells.zip.part'
url='https://ndownloader.figshare.com/files/58773835'
ledger=[]
expected_size=1929137550
expected_md5='3b0ab5c964fb492ec36ee0f55a5d53de'
def save():
    (root/'download_attempts.json').write_text(json.dumps(ledger,indent=2)+'\n')
for attempt in range(3):
    # Request a fresh public download redirect after an expired/cached URL fails.
    request_url=url if attempt==0 else url+'?download=1&request_time='+str(int(time.time()))
    size=path.stat().st_size if path.exists() else 0
    entry={'attempt':attempt+1,'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'source':url,'cache_revalidation':attempt>0,'resume_offset':size}
    ledger.append(entry)
    headers={'User-Agent':'UCT-public-data-reanalysis/1.0'}
    if size: headers['Range']='bytes='+str(size)+'-'
    try:
        with urllib.request.urlopen(urllib.request.Request(request_url,headers=headers), timeout=30) as response:
            entry.update(status=response.status, final_host=urlsplit(response.url).hostname, content_type=response.headers.get('Content-Type'), content_length=response.headers.get('Content-Length'),content_range=response.headers.get('Content-Range'))
            print(json.dumps(entry),flush=True)
            if response.status==206:
                if not response.headers.get('Content-Range','').startswith('bytes '+str(size)+'-'):
                    raise ValueError('Resume Content-Range mismatch')
                mode='ab'
            elif response.status==200:
                size=0;mode='wb'
            else: raise ValueError('Unexpected HTTP status')
            last=time.monotonic()
            with path.open(mode) as f:
                while True:
                    chunk=response.read(1024*1024)
                    if not chunk:break
                    if size==0 and not chunk.startswith(b'PK'):
                        entry['non_zip_prefix']=repr(chunk[:100])
                        raise ValueError('Response is not a ZIP stream')
                    f.write(chunk);size+=len(chunk)
                    if size>expected_size:raise ValueError('Oversized response')
                    if time.monotonic()-last>=15:
                        print(json.dumps({'bytes':size,'percent':round(size/expected_size*100,2)}),flush=True)
                        last=time.monotonic()
        entry['bytes_downloaded_total']=size
        if size!=expected_size:raise ValueError('Incomplete stream')
        h=hashlib.md5();s=hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk);s.update(chunk)
        entry['md5']=h.hexdigest();entry['sha256']=s.hexdigest()
        if h.hexdigest()!=expected_md5:raise ValueError('MD5 mismatch')
        path.rename(root/'Cells.zip');entry['outcome']='VERIFIED_FULL_DOWNLOAD';save()
        print(json.dumps(entry),flush=True);sys.exit(0)
    except Exception as e:
        entry['error_type']=type(e).__name__
        # Avoid preserving signed URL query strings.
        entry['error']=str(e).split('?')[0][:300]
        if isinstance(e,urllib.error.HTTPError):
            entry['http_status']=e.code
            entry['response_prefix']=e.read(600).decode(errors='replace')
        entry['outcome']='FAILED';save();print(json.dumps(entry),flush=True)
sys.exit(1)
