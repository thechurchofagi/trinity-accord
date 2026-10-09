#!/usr/bin/env python3
"""Restore and verify one frozen research capsule without network access."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, json, tarfile

def digest(data):return hashlib.sha256(data).hexdigest()

def restore(capsule,metadata,output):
    meta=json.loads(metadata.read_text())
    assert digest(capsule.read_bytes())==meta['sha256'],'Capsule SHA256 mismatch'
    output.mkdir(parents=True,exist_ok=True)
    with tarfile.open(capsule,'r:xz') as archive:
        members=archive.getmembers();names=[m.name for m in members]
        assert len(names)==len(set(names)),'Duplicate members'
        for m in members:
            p=PurePosixPath(m.name)
            assert not p.is_absolute() and '..' not in p.parts and m.isfile(),m.name
        manifest=json.loads(archive.extractfile('CAPSULE_MEMBER_MANIFEST.json').read())
        expected={r['path']:r for r in manifest['files']}
        assert set(names)==set(expected)|{'CAPSULE_MEMBER_MANIFEST.json'},'Unexpected member set'
        for m in members:
            data=archive.extractfile(m).read()
            if m.name in expected:
                row=expected[m.name]
                assert len(data)==row['bytes'] and digest(data)==row['sha256'],m.name
            target=output/m.name
            if target.exists():assert target.is_file() and target.read_bytes()==data,('Refuse overwrite',str(target))
            else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    print(json.dumps({'status':'RESTORED_AND_ALL_MEMBERS_VERIFIED','release':meta['release'],'verified_members':len(expected),'capsule_sha256':meta['sha256'],'output':str(output)}))

if __name__=='__main__':
    here=Path(__file__).resolve().parent
    p=argparse.ArgumentParser();p.add_argument('--capsule',type=Path,default=here/'UCT_MAP_v1.1.2_Capsule.tar.xz');p.add_argument('--metadata',type=Path,default=here/'CAPSULE.json');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();restore(a.capsule,a.metadata,a.output)
