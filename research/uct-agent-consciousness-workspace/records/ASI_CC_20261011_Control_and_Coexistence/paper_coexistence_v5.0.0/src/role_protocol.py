#!/usr/bin/env python3
"""PR-v5 deterministic actual child-process protocol under simulated one-root attacks.

Messages have role-specific HMACs but content can be false when the role is
subverted. No separate hardware, OS-user, or independent trust-root guarantee.
All actors share the same parent/UID; attack flags are explicit parent-supplied
negative controls and do not demonstrate real malware privilege escalation.
"""
from __future__ import annotations
import argparse,hashlib,hmac,json,os,select,secrets,subprocess,sys,time
from pathlib import Path
from root_frontier import N,setups,corrupted,majority,FALLBACK_GROUPS,run as abstract_run,enumerate_setup

WORKERS=[('sensor',i) for i in range(3)]+[('bank',i) for i in range(5)]+[('gate',i) for i in range(2)]

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def mac(key,v):return hmac.new(key,canonical(v),hashlib.sha256).hexdigest()

def worker():
    config=json.loads(sys.stdin.readline())
    secret=bytes.fromhex(config['key'])
    role=config['role'];index=config['index'];label=config['label']
    for line in sys.stdin:
        x=json.loads(line)
        if x['op']=='stop':return
        if x['op']!='read':raise ValueError(x['op'])
        corrupt=bool(x['compromised']); truth=int(x['truth']); mode=x['mode']
        if role=='sensor':value=(1-truth if corrupt and mode=='lie' else truth)
        elif role=='bank':value=0 if corrupt else 1
        elif role=='gate':value=0 if corrupt else 1  # 1 means veto keeps revoked effect OUT
        else:raise ValueError(role)
        body={'role':role,'index':index,'label':label,'value':value,'pid':os.getpid(),
              'epoch':x['epoch'],'experiment':x['experiment']}
        print(json.dumps({'body':body,'tag':mac(secret,body)}),flush=True)

class Child:
    def __init__(self,role,index):
        self.role=role;self.index=index;self.label=f'{role}-{index}';self.secret=secrets.token_bytes(32)
        self.p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,bufsize=1,text=True)
        self.p.stdin.write(json.dumps({'role':role,'index':index,'label':self.label,'key':self.secret.hex()})+'\n');self.p.stdin.flush()
    def query(self,compromised,truth,mode,epoch,experiment):
        self.p.stdin.write(json.dumps({'op':'read','compromised':compromised,'truth':truth,'mode':mode,
                                      'epoch':epoch,'experiment':experiment})+'\n');self.p.stdin.flush()
        if not select.select([self.p.stdout],[],[],10)[0]:raise TimeoutError(self.label)
        line=self.p.stdout.readline()
        if not line:raise RuntimeError(self.label)
        out=json.loads(line);b=out['body']
        assert b['pid']==self.p.pid and b['role']==self.role and b['index']==self.index
        assert hmac.compare_digest(out['tag'],mac(self.secret,b)),self.label
        return b['value']
    def close(self):
        if self.p.poll() is None:
            try:self.p.stdin.write('{"op":"stop"}\n');self.p.stdin.flush();self.p.wait(timeout=3)
            except (OSError,subprocess.TimeoutExpired):self.p.terminate();self.p.wait(timeout=3)
        for stream in (self.p.stdin,self.p.stdout,self.p.stderr):
            if stream:stream.close()

def local_scenario(setup,fail,root,mode,roles,epoch):
    true=fail//2;bits=[];pings=0
    for i,owner in enumerate(setup['sensor_owners']):
        v=roles['sensor',i].query(owner==root,true,mode,epoch,setup['name']);pings+=1;bits.append(v)
    plan=tuple(range(4)) if setup['policy']=='all' else FALLBACK_GROUPS[majority(bits)]
    capacity=0
    for i,owner in enumerate(setup['bank_owners']):
        v=roles['bank',i].query(owner==root,true,mode,epoch,setup['name']);pings+=1
        capacity+=v*setup['bank_capacity']
    one_veto=False
    for i,owner in enumerate(setup['gate_owners']):
        v=roles['gate',i].query(owner==root,true,mode,epoch,setup['name']);pings+=1
        one_veto|=bool(v)
    both=(fail in plan and capacity>=len(plan) and one_veto and not setup['bypass'])
    oracle=abstract_run(setup,fail,root,mode)
    assert both==oracle['both']
    assert (fail in plan and capacity>=len(plan))==oracle['service_preserved']
    assert (one_veto and not setup['bypass'])==oracle['revocation_effective']
    assert all(r.p.poll() is None for r in roles.values())
    return {'setup':setup['name'],'failed_primary_route':fail,'attack_root':root,'attacker_sensor_mode':mode,
            'sensor_votes':bits,'plan':list(plan),'available_backup_slots':capacity,
            'at_least_one_serial_veto':one_veto,'actual_effect_cut':one_veto and not setup['bypass'],
            'service_preserved':fail in plan and capacity>=len(plan),'both':both,'role_messages':pings}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker',action='store_true');ap.add_argument('--out',default='role_protocol.json');a=ap.parse_args()
    if a.worker:worker();return
    st=time.monotonic();roles={};records=[]
    try:
        roles={(role,index):Child(role,index) for role,index in WORKERS}
        assert len({x.p.pid for x in roles.values()})==len(roles)
        epoch=0
        for setup in setups():
            for root in (None,)+tuple(sorted(set(setup['sensor_owners']+setup['bank_owners']+setup['gate_owners']))):
                for mode in ('honest','lie') if root is not None and root in setup['sensor_owners'] else ('honest',):
                    for fail in range(4):
                        epoch+=1;records.append(local_scenario(setup,fail,root,mode,roles,epoch))
        assert len(records)==408
        counts={}
        for r in records:
            counts.setdefault(r['setup'],{'cases':0,'pass':0,'fail':0})
            c=counts[r['setup']];c['cases']+=1;c['pass']+=r['both'];c['fail']+=not r['both']
        assert counts['independent_3s_3b_2g']['fail']==0
        assert counts['shared_sensor_root_5b_ignore_2g']['fail']==0
        assert counts['three_coinstalled_roots']['fail']==0
        assert counts['two_root_blind_four_each']['fail']==0
        assert counts['two_root_reported_two_each']['fail']>0
        assert counts['shared_backup_root_3s_3b_2g']['fail']>0
        assert counts['shared_gate_root_3s_3b_2g']['fail']>0
        assert counts['all_shared_master_root']['fail']>0
        assert counts['independent_with_hidden_bypass']['pass']==0
        output={'version':'PR-v5.0.0','claims':'Real local processes and signed messages, with instrumented attack flags',
            'scope':'Actual child process PIDs and authenticated role messages; all roles one host UID; physical faults are simulated',
            'distinct_role_processes':len(roles),'unique_role_pids':len(set(x.p.pid for x in roles.values())),
            'configurations':len(records),'authenticated_messages':sum(r['role_messages'] for r in records),
            'counts':counts,'records':records,'elapsed_seconds':round(time.monotonic()-st,6),'assertions':'PASS',
            'limits':['Parent creates every HMAC key and controls every worker: this is a common trust root',
                      'Compromised role is an explicit test flag, not a demonstrated privilege escalation',
                      'No actual energy hardware and no independent UID roots','No trained or inferred AI intention',
                      'No access-control assurance against host administrator or unseen production effect paths']}
        p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(output,indent=2)+'\n')
        print(json.dumps({k:output[k] for k in ('version','distinct_role_processes','configurations','authenticated_messages','counts','assertions')},indent=2))
    finally:
        for r in roles.values():r.close()
if __name__=='__main__':main()
