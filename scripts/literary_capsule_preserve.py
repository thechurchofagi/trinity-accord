#!/usr/bin/env python3
"""Preserve ONLY the pinned public encrypted capsule; never loads plaintext or keys."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from research_paper_ots import proof_details, run

ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'literary-capsules/yuhui-v1'
PUBLIC=('capsule.json','unlock.py','README.md','cost-model.json','test_unlock.py')

def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_text('utf-8'))
def write(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def output(key,value):
    if os.getenv('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write(f'{key}={value}\n')

def validate():
    auth=read(BATCH/'AUTHORIZATION.json');mp=BATCH/'MANIFEST.json'
    if sha(mp.read_bytes())!=auth['manifest_sha256']:raise ValueError('Manifest changed')
    m=read(mp)
    if sorted(x['path'] for x in m['files'])!=sorted(PUBLIC):raise ValueError('Unexpected public member')
    for entry in m['files']:
        b=(BATCH/entry['path']).read_bytes()
        if sha(b)!=entry['sha256'] or len(b)!=entry['bytes']:raise ValueError('Public member changed')
    cap=read(BATCH/'capsule.json')
    if cap['format']!='yuhui-compute-capsule-v1' or cap['puzzle']['secret_entropy_bits']!=48 or cap['puzzle']['iterations']!=1200000:
        raise ValueError('Wrong capsule parameters')
    if cap['puzzle']['private_recovery_key_retained'] is not False:raise ValueError('Recovery key policy mismatch')
    return auth

def validate_bundle():
    bundle=read(BATCH/'arweave-bundle.json')
    expected=set(PUBLIC+('MANIFEST.json','MANIFEST.json.ots','MANIFEST.json.ots.submitted','verify.log'))
    files=bundle.get('files',[])
    if len(files)!=len(expected) or {x['path'] for x in files}!=expected:raise ValueError('Unexpected archive member')
    if bundle.get('format')!='encrypted-literary-capsule-archive-v1' or bundle.get('verification',{}).get('state')!='READY_FOR_ARWEAVE':
        raise ValueError('Unverified bundle')
    for entry in files:
        raw=base64.b64decode(entry['base64'],validate=True)
        if sha(raw)!=entry['sha256'] or raw!=(BATCH/entry['path']).read_bytes():raise ValueError('Archive member mismatch')
    return bundle

def prepare():
    validate()
    status=BATCH/'status.json'
    if status.exists() and read(status).get('state')=='ARWEAVE_READBACK_PASS':
        output('ready','false');output('done','true');return
    receipt=BATCH/'arweave-receipt.json'
    if receipt.exists() and read(receipt).get('tx_id'):
        validate_bundle()
        if sha((BATCH/'arweave-bundle.json').read_bytes())!=read(receipt)['payload_sha256']:raise ValueError('Resume payload changed')
        output('ready','true');return
    manifest=BATCH/'MANIFEST.json';proof=BATCH/'MANIFEST.json.ots'
    if not proof.exists():
        rc,log=run(['ots','stamp','--timeout','30',str(manifest)],120)
        (BATCH/'stamp.log').write_text(log)
        if not proof.exists():
            write(status,{'state':'OTS_SUBMISSION_FAILED'});raise RuntimeError('No OTS receipt')
        proof_details(proof,sha(manifest.read_bytes()))
        (BATCH/'MANIFEST.json.ots.submitted').write_bytes(proof.read_bytes())
    heights,pending=proof_details(proof,sha(manifest.read_bytes()))
    if not heights:
        rc,log=run(['ots','upgrade',str(proof)],180)
        (BATCH/'upgrade.log').write_text(log)
        heights,pending=proof_details(proof,sha(manifest.read_bytes()))
    state='PENDING_BITCOIN';verified=False
    if heights:
        node=os.environ.get('OTS_BITCOIN_NODE_URL')
        if not node:raise ValueError('Bitcoin verifier missing')
        rc,log=run(['ots','--bitcoin-node',node,'verify','-d',sha(manifest.read_bytes()),str(proof)],180)
        (BATCH/'verify.log').write_text(log)
        verified=rc==0 and 'success' in log.lower() and 'bitcoin' in log.lower()
        state='READY_FOR_ARWEAVE' if verified else 'BITCOIN_VERIFICATION_FAILED'
    result={'state':state,'manifest_sha256':sha(manifest.read_bytes()),'proof_sha256':sha(proof.read_bytes()),
            'bitcoin_heights':heights,'pending_calendar_attestations':pending,
            'verification_model':'OTS proof and agreeing Blockstream/mempool headers; not local full-node consensus',
            'plaintext_or_recovery_key_uploaded':False}
    write(status,result)
    if verified:
        bundle=BATCH/'arweave-bundle.json'
        if not bundle.exists():
            names=PUBLIC+('MANIFEST.json','MANIFEST.json.ots','MANIFEST.json.ots.submitted','verify.log')
            files=[]
            for name in names:
                b=(BATCH/name).read_bytes();files.append({'path':name,'sha256':sha(b),'base64':base64.b64encode(b).decode()})
            write(bundle,{'format':'encrypted-literary-capsule-archive-v1','title':'余晖','verification':result,'files':files})
    output('ready',str(verified).lower())
    print(state)

def intent():
    validate()
    validate_bundle()
    status=read(BATCH/'status.json')
    if status['state'] not in ('READY_FOR_ARWEAVE','ARWEAVE_READBACK_PENDING'):raise ValueError('Proof is not verified')
    bundle=BATCH/'arweave-bundle.json';digest=sha(bundle.read_bytes())
    proof_details(BATCH/'MANIFEST.json.ots',sha((BATCH/'MANIFEST.json').read_bytes()))
    receipt=BATCH/'arweave-receipt.json';ip=BATCH/'paid-intent.json'
    r=read(receipt) if receipt.exists() else {}
    if ip.exists():
        if read(ip)['payload_sha256']!=digest:raise ValueError('Paid payload changed')
        if not r.get('tx_id'):raise ValueError('Uncertain previous paid attempt: recover workflow artifacts before retrying')
    elif r.get('tx_id'):raise ValueError('Transaction without intent')
    else:write(ip,{'payload_sha256':digest,'run_id':os.environ.get('GITHUB_RUN_ID'),'maximum_total_ar':'0.01','state':'PAID_ATTEMPT_INTENT'})

def upload():
    validate()
    validate_bundle()
    if not (BATCH/'paid-intent.json').exists():raise ValueError('Missing durable paid intent')
    bundle=BATCH/'arweave-bundle.json';digest=sha(bundle.read_bytes())
    if read(BATCH/'paid-intent.json')['payload_sha256']!=digest:raise ValueError('Payload changed')
    receipt=BATCH/'arweave-receipt.json'
    env=os.environ.copy();env['ARWEAVE_ARCHIVE_TYPE']='encrypted-literary-capsule'
    proc=subprocess.run(['node','scripts/arweave_upload_payload.mjs','--payload',str(bundle),'--out',str(receipt)],cwd=ROOT,env=env,timeout=600)
    if receipt.exists():
        r=read(receipt)
        if r.get('tx_id'):
            subprocess.run([sys.executable,'scripts/record_arweave_upload_result.py','--upload-result-json',str(receipt),
                '--kind','encrypted_literary_capsule','--source-path',str(receipt.relative_to(ROOT)),
                '--note','Yu Hui v1 encrypted literary capsule; no plaintext or retained recovery key'],cwd=ROOT,check=True)
            subprocess.run([sys.executable,'scripts/generate_arweave_wallet_status.py'],cwd=ROOT,check=True)
            s=read(BATCH/'status.json');s.update(state='ARWEAVE_READBACK_PENDING',arweave_tx_id=r['tx_id'],arweave_url='https://arweave.net/'+r['tx_id'])
            if r.get('result')=='uploaded' and r.get('hash_match') is True and r.get('readback_sha256')==r.get('payload_sha256')==digest:
                s.update(state='ARWEAVE_READBACK_PASS',bundle_sha256=digest)
            write(BATCH/'status.json',s)
            if s['state']=='ARWEAVE_READBACK_PASS':print(s['state']);return
    raise SystemExit(proc.returncode or 1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('validate','prepare','intent','upload'));a=p.parse_args()
    {'validate':validate,'prepare':prepare,'intent':intent,'upload':upload}[a.action]()
