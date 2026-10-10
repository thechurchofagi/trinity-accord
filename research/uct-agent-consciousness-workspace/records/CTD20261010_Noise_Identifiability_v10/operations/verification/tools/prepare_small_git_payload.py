from pathlib import Path
import argparse,base64,hashlib,json,subprocess
ap=argparse.ArgumentParser();ap.add_argument('--repo',required=True);ap.add_argument('--paths',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
repo=Path(a.repo).resolve();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
paths=json.loads(Path(a.paths).read_text());assert len(paths)==len(set(paths))
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=repo,text=True).strip()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
base_tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=repo,text=True).strip()
rows=[]
for name in sorted(paths):
 p=repo/name;assert p.is_file() and not p.is_symlink();data=p.read_bytes();blob_sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
 try:content=data.decode('utf-8');inline=len(data)<=50000
 except UnicodeDecodeError:content=None;inline=False
 rows.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_sha':blob_sha,'inline':inline,'content':content if inline else base64.b64encode(data).decode(),'encoding':'utf-8' if inline else 'base64'})
subprocess.run(['git','add','--sparse','--',*paths],cwd=repo,check=True)
staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=repo,text=True).splitlines();assert set(staged)==set(paths),(staged,paths)
expected_tree=subprocess.check_output(['git','write-tree'],cwd=repo,text=True).strip()
payload={'repository_full_name':'thechurchofagi/trinity-accord','head':head,'base_tree':base_tree,'expected_tree':expected_tree,'files':rows}
s=json.dumps(payload,ensure_ascii=True,separators=(',',':'));(out/'payload.json').write_text(s)
chunks=[]
for i,start in enumerate(range(0,len(s),32000)):
 f=out/('chunk-%04d.txt'%i);part=s[start:start+32000];f.write_text(part);chunks.append({'path':str(f),'chars':len(part)})
meta={'head':head,'base_tree':base_tree,'expected_tree':expected_tree,'file_count':len(rows),'payload_chars':len(s),'chunk_count':len(chunks),'chunks':chunks,'files':[{k:v for k,v in r.items() if k!='content'} for r in rows]}
(out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps({k:v for k,v in meta.items() if k not in {'chunks','files'}}))
