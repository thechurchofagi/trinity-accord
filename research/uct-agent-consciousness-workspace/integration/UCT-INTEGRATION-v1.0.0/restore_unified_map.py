"""Expand the unified view; preserve disabled candidate status. No network needed."""
import argparse,gzip,json,pathlib,hashlib
p=argparse.ArgumentParser();p.add_argument('--input',type=pathlib.Path,default=pathlib.Path(__file__).with_name('UNIFIED_MAP.json.gz'));p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
j=json.loads(gzip.decompress(a.input.read_bytes()))
assert all(x['enabled_as_established_premises'] is False for x in j['pending_objects'])
b=(json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode()
if a.output.exists():assert a.output.read_bytes()==b,'Refuse to replace a different file'
else:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_bytes(b)
print(json.dumps({'version':j['version'],'output':str(a.output),'sha256':hashlib.sha256(b).hexdigest(),'scientific_promotion':False}))
