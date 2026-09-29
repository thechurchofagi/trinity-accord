#!/usr/bin/env python3
"""Read-only public data acquisition. No secrets, publication, main writes, or analysis.
Fetch selected small members via validated HTTP ranges; never silently fetch the
1.7-GB archive. ZIP CRC is verified for each extracted member; full archive MD5
is metadata only and is not claimed independently verified by this partial read.
"""
from __future__ import annotations
import hashlib, io, json, pathlib, time, urllib.request, urllib.parse, zipfile
ROOT=pathlib.Path('transfer');ROOT.mkdir(exist_ok=True)
LOG=[];TOTAL=0;LIMIT=120_000_000

def request(url, start=None, end=None, cap=10_000_000):
    global TOTAL
    p=urllib.parse.urlsplit(url)
    if p.scheme!='https' or p.hostname!='zenodo.org':raise ValueError('Only official public Zenodo download endpoints')
    headers={'User-Agent':'UCT-Reproducibility-Audit/0.1','Accept-Encoding':'identity'}
    if start is not None:headers['Range']=f'bytes={start}-{end}'
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=90) as r:
                status=r.status; cr=r.headers.get('Content-Range');cl=r.headers.get('Content-Length')
                if start is not None:
                    if status!=206 or not cr or not cr.startswith(f'bytes {start}-{end}/'):
                        raise RuntimeError(f'Range not honored: {status} {cr} {cl}; full archive not downloaded')
                data=r.read(cap+1)
                if len(data)>cap:raise RuntimeError('Response cap exceeded')
                if start is not None and len(data)!=end-start+1:raise RuntimeError('Truncated range')
                TOTAL+=len(data)
                if TOTAL>LIMIT:raise RuntimeError('Transfer budget exceeded')
                LOG.append({'url':url,'start':start,'end':end,'bytes':len(data),'status':status,'content_range':cr})
                return data
        except (TimeoutError,urllib.error.URLError) as e:
            if attempt==2:raise
            time.sleep(2*(attempt+1))
    raise RuntimeError('Unreachable')

class RemoteArchive(io.RawIOBase):
    def __init__(self,url,size):self.url=url;self.size=size;self.pos=0;self.cache={}
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        target=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
        if target<0:raise ValueError('negative seek')
        self.pos=target;return target
    def read(self,n=-1):
        if n<0:n=self.size-self.pos
        n=min(n,max(0,self.size-self.pos))
        if n==0:return b''
        if n>25_000_000:raise RuntimeError('Large range refused')
        key=(self.pos,self.pos+n-1)
        if key not in self.cache:self.cache[key]=request(self.url,*key,cap=n)
        data=self.cache[key];self.pos+=len(data);return data

def main():
    raw=request('https://zenodo.org/api/records/4939544');(ROOT/'record-4939544.json').write_bytes(raw)
    rec=json.loads(raw);items={f['key']:f for f in rec['files']}
    arc=items['DynamicStimulationDataAndCode.zip']
    if arc['checksum']!='md5:13783203b5229b076a0a6b3e30140196':raise RuntimeError('Unexpected source edition')
    manifest=[]
    for name in ('FullMethods.pdf','UsageNotes.pdf'):
        item=items[name];b=request(item['links']['self'])
        if 'md5:'+hashlib.md5(b).hexdigest()!=item['checksum']:raise RuntimeError('Source checksum mismatch')
        dest=ROOT/'source'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
        manifest.append({'path':str(dest.relative_to(ROOT)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'verified_source_md5':item['checksum']})
    z=zipfile.ZipFile(RemoteArchive(arc['links']['self'],int(arc['size'])))
    inventory=[{'name':i.filename,'bytes':i.file_size,'compressed_bytes':i.compress_size,'crc32':f'{i.CRC:08x}'} for i in z.infolist()]
    (ROOT/'archive_inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    folders=('CurrentSteering03281','CharacterDiscrimination03281','RapidFormDiscrimination03281','CharacterDiscriminationBAA','CharacterDiscriminationYBN')
    selected=[]
    for item in z.infolist():
        p=pathlib.PurePosixPath(item.filename)
        if item.is_dir() or '__MACOSX' in p.parts or p.name.startswith('._'):continue
        if not any(f in item.filename for f in folders):continue
        if p.suffix.lower() not in ('.mat','.m','.xlsx','.xls','.pdf','.txt'):continue
        if item.file_size>25_000_000 or item.compress_size>25_000_000:continue
        if '..' in p.parts or p.is_absolute():raise RuntimeError('Unsafe ZIP path')
        selected.append(item)
    if sum(i.file_size for i in selected)>100_000_000:raise RuntimeError('Expanded subset too large')
    for i,item in enumerate(selected):
        b=z.read(item) # zipfile checks CRC32 on decompressed data
        dest=ROOT/'source'/item.filename;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
        manifest.append({'path':str(dest.relative_to(ROOT)),'archive_member':item.filename,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'verified_zip_crc32':f'{item.CRC:08x}'})
        print(i+1,len(selected),item.filename,len(b),flush=True)
    (ROOT/'MANIFEST.json').write_text(json.dumps({'state':'SUBSET_DOWNLOADED_CRC_VERIFIED','dataset_doi':'10.5061/dryad.gtht76hhk','source_record':4939544,'archive_size':arc['size'],'full_archive_md5_independently_verified':False,'selected_members':len(selected),'network_bytes':TOTAL,'files':manifest,'scope':'Public source files only. No participant response analysis executed during transfer.'},indent=2)+'\n')
if __name__=='__main__':
    try:main()
    finally:(ROOT/'TRANSFER_LOG.json').write_text(json.dumps({'network_bytes':TOTAL,'requests':LOG},indent=2)+'\n')
