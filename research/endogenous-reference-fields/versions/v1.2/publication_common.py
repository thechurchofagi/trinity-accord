from __future__ import annotations
import hashlib, importlib.util, json, os, subprocess, time, urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
BRANCH='research/endogenous-reference-fields-v1-2-20260920'
PREVIOUS_TITLE='Endogenous Reference Fields and Experiential Attribution: A Slow Shared-Modulation Hypothesis and Its Discriminating Tests'
TITLE='Endogenous Reference Fields and Experiential Attribution: A Multidimensional Process Theory of Experience, Subject Boundaries, and Artificial Realization'
REPORT='TA-TR-2026-10'
VERSION='1.2'
DATE='2026-09-20'
PREVIOUS_RECORD=22854705
PREVIOUS_VERSION='1.1'
CONCEPT_RECORD=22852884
CLIENT_BLOB='a0cbc84cc5fd826c06d16456c4adbaa40dabc788'
STATE_FILES={'create-intent.json','deposit.json','preparation-attempt.json','publication-attempt.json','publication-record.json'}
PROTECTED={21675727,21699878,21900592,22761411,22804542,22809019,22830239,22839629,22840604,22842789,22844927,22844928,22846307,22852885,PREVIOUS_RECORD,CONCEPT_RECORD}

def load(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))

def save(name,value):
    if name not in STATE_FILES:
        raise RuntimeError('unexpected state file')
    p=ROOT/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def persist_states(names):
    allowed={str((ROOT/n).relative_to(REPO)) for n in names if (ROOT/n).exists()}
    if not allowed:
        return
    subprocess.run(['git','config','user.name','github-actions[bot]'],cwd=REPO,check=True)
    subprocess.run(['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],cwd=REPO,check=True)
    subprocess.run(['git','add','--',*sorted(allowed)],cwd=REPO,check=True)
    staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=REPO,text=True).splitlines()
    if not set(staged)<=allowed:
        raise RuntimeError('unexpected staged path')
    if staged:
        subprocess.run(['git','commit','-m','research: preserve TA10 v1.2 publication state [skip ci]'],cwd=REPO,check=True)
        subprocess.run(['git','push','origin','HEAD:'+BRANCH],cwd=REPO,check=True)

def client():
    old=REPO/'research/reading-trinity-accord/publish_zenodo.py'
    data=old.read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if actual!=CLIENT_BLOB:
        raise RuntimeError('established Zenodo client changed')
    spec=importlib.util.spec_from_file_location('ta10v12client',old)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    token=os.environ.get('ZENODO_ACCESS_TOKEN')
    if not token:
        raise RuntimeError('publication credential unavailable')
    return m.Zenodo(token)

def read(z,path,authenticated=True):
    for attempt,delay in enumerate((0,3,8,15)):
        if delay:
            time.sleep(delay)
        try:
            return z.request(path,authenticated=authenticated)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError):
            if attempt==3:
                raise

def validate_record_id(rid):
    if type(rid) is not int or rid<=0 or rid in PROTECTED:
        raise RuntimeError('invalid/protected record id')
    return rid

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('--persist-states',action='store_true')
    a=p.parse_args()
    if a.persist_states:
        persist_states(STATE_FILES)
