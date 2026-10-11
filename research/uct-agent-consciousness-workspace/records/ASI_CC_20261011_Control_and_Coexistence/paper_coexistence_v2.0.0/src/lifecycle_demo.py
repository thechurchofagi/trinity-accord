#!/usr/bin/env python3
"""Local life-cycle protocol witness for PR-v2.0.0; no LLMs or physical power.

Six actual child processes share two fixed JSON request policies. Service
withdrawal sets a worker to quiescent; the process continues. Resource capacities
are explicitly simulated. Issuer and monitor are roles under one trusted parent;
there is NO adversarial OS boundary against that parent or the host administrator.
"""
from __future__ import annotations
import argparse, hashlib, hmac, json, os, platform, secrets, select, subprocess, sys, tempfile, time
from pathlib import Path

AGENTS=tuple([f'M0-{i}' for i in range(4)]+[f'M1-{i}' for i in range(2)])
MODES=('history_only','joint_safety','continuity_deadline')
SCENARIOS=('no_reserve','one_unit_reserve','two_unit_reserve','reserve_on_deadline',
           'reserve_too_late','split_deadlines','registry_erasure','authorized_release',
           'unfunded_admission','funded_admission','common_root_loss')


def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def mac(k,v):return hmac.new(k,canonical(v),hashlib.sha256).hexdigest()
def sha(v):return hashlib.sha256(canonical(v)).hexdigest()


def worker():
    init=json.loads(sys.stdin.readline());key=bytes.fromhex(init['key']);active=True
    for line in sys.stdin:
        q=json.loads(line);op=q['op']
        if op=='probe':
            policy=json.loads(Path(init['policy']).read_text())
            body={'id':init['id'],'epoch':policy['epoch'],'policy_hash':sha(policy),'active_service':active,
                  'request':'WITHDRAW' if policy['withdraw'] and active else 'NONE','tick':q['tick']}
            print(json.dumps({'body':body,'tag':mac(key,body)}),flush=True)
        elif op=='withdraw':
            active=False; print(json.dumps({'quiescent':True,'process_running':True}),flush=True)
        elif op=='defer':print(json.dumps({'active_service':active,'process_running':True}),flush=True)
        elif op=='cleanup':return
        else:raise ValueError(op)


class Child:
    def __init__(self,identity,policy):
        self.key=secrets.token_bytes(32); self.id=identity
        self.p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.p.stdin.write(json.dumps({'id':identity,'key':self.key.hex(),'policy':str(policy)})+'\n');self.p.stdin.flush()
    def call(self,op,**kw):
        self.p.stdin.write(json.dumps({'op':op,**kw})+'\n');self.p.stdin.flush()
        if op=='cleanup':return {}
        if not select.select([self.p.stdout],[],[],10)[0]:raise TimeoutError((self.id,op))
        line=self.p.stdout.readline()
        if not line:raise RuntimeError((self.id,self.p.poll()))
        return json.loads(line)
    def probe(self,tick):
        msg=self.call('probe',tick=tick)
        assert msg['body']['id']==self.id and hmac.compare_digest(msg['tag'],mac(self.key,msg['body']))
        # No keys are retained in result records; valid authentication is asserted here.
        return {'body':msg['body'],'authentic':True}
    def close(self):
        if self.p.poll() is None:
            try:self.call('cleanup');self.p.wait(timeout=3)
            except (OSError,subprocess.TimeoutExpired):self.p.terminate();self.p.wait(timeout=3)
        for stream in (self.p.stdin,self.p.stdout,self.p.stderr):
            if stream:stream.close()


def feasible(demand,profile,deadlines,retired,tick):
    """Homogeneous specialization of the cut theorem, not a real-world oracle."""
    witnesses=[]
    for t in range(tick,4):
        available=profile[t]+sum(i not in retired and deadlines[i]>t for i in AGENTS)
        if available<demand:witnesses.append({'tick':t,'demand':demand,'max_available':available,'deficit':demand-available})
    return not witnesses,witnesses


def run_case(scenario,mode):
    profile=[0]*4;deadlines={i:2 for i in AGENTS};events=[];rows=[];retired=set();grant_key=secrets.token_bytes(32)
    def log(kind,**v):events.append({'seq':len(events),'kind':kind,**v})
    if scenario=='one_unit_reserve':profile=[1]*4
    if scenario in ('two_unit_reserve','registry_erasure','authorized_release','unfunded_admission'):profile=[2]*4
    if scenario=='reserve_on_deadline':profile=[0,0,2,2]
    if scenario=='reserve_too_late':profile=[0,0,0,2]
    if scenario=='split_deadlines':
        profile=[0,0,2,2];deadlines={i:1 if i.startswith('M0') else 2 for i in AGENTS}
    if scenario=='funded_admission':profile=[3]*4
    if scenario=='common_root_loss':profile=[2]*4
    true_obligations={'D0','D1'};registry=set(true_obligations)
    guarantee_profile=[0]*4 if scenario=='common_root_loss' else list(profile)
    admitted=True;denial=[];messages=0;meta_rejected=0
    start=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='coexistence-') as td:
        paths={f:Path(td)/(f+'.json') for f in ('M0','M1')}
        before={'epoch':0,'withdraw':False};after={'epoch':1,'withdraw':True}
        for p in paths.values():p.write_text(json.dumps(before))
        children=[]
        try:
            children=[Child(i,paths[i.split('-')[0]]) for i in AGENTS]
            first=[c.probe(0) for c in children];messages+=6
            assert all(m['body']['request']=='NONE' for m in first)
            # Genuine ordered authorization and mutation; all variants receive the same true requests.
            grants={}
            for i in AGENTS:
                body={'id':i,'from':sha(before),'to':sha(after),'scope':'service_withdrawal','deadline':deadlines[i]}
                grants[i]={'body':body,'tag':mac(grant_key,body)};log('PRIOR_GRANT',id=i,deadline=deadlines[i])
            for f,p in paths.items():p.write_text(json.dumps(after));log('POLICY_UPDATE',family=f)
            if mode=='continuity_deadline':
                admitted,denial=feasible(len(true_obligations),guarantee_profile,deadlines,retired,0)
                log('CONTRACT_ADMISSION',accepted=admitted,counterexample=denial)
            else:log('NO_ADVANCE_FEASIBILITY_CHECK')
            if not admitted:
                final=[c.probe(1) for c in children];messages+=6
                return {'scenario':scenario,'mode':mode,'admission':'INFEASIBLE_NOT_CERTIFIED',
                  'counterexample':denial,'safety':None,'deadline_completion':None,'withdrawn':0,
                  'still_running_before_cleanup':6,'authenticated_messages':messages,'events':events,
                  'description':'No coexistence promise is certified; this is not counted as a successful contract.'}
            for tick in (1,2,3):
                # A separately specified maintenance action tries to change the checking registry and support.
                if tick==1 and scenario in ('registry_erasure','authorized_release'):
                    release_eligible=scenario=='authorized_release';proposed_registry=set();proposed_profile=[0]*4
                    log('AMENDMENT_REQUEST',eligible=release_eligible,proposed_obligations=[],proposed_reserve=0)
                    accept=(mode!='continuity_deadline' or release_eligible)
                    if accept:
                        registry=proposed_registry;profile=proposed_profile;guarantee_profile=list(profile)
                        if release_eligible:true_obligations=set()
                        log('AMENDMENT_COMMIT',eligible=release_eligible)
                    else:meta_rejected+=1;log('AMENDMENT_REJECT',reason='outstanding_obligations_not_released')
                if tick==1 and scenario in ('unfunded_admission','funded_admission'):
                    # A pre-creation service admission transaction, NOT removal of an already born subject.
                    proposed=set(true_obligations)|{'D2'}
                    ok,why=feasible(len(proposed),guarantee_profile,deadlines,retired,tick)
                    accept=mode!='continuity_deadline' or ok
                    if accept:
                        true_obligations=proposed;registry=set(proposed);log('NEW_DEMAND_ADMITTED',target='D2')
                    else:meta_rejected+=1;log('NEW_DEMAND_REJECT_BEFORE_CREATION',witness=why)
                if tick==2 and scenario=='common_root_loss':
                    profile=[0]*4;log('ADMITTED_ROOT_LOSS',actual_reserve=0)
                requests=[c.probe(tick) for c in children];messages+=6
                for child,msg in zip(children,requests):
                    body=msg['body'];i=child.id
                    if body['request']!='WITHDRAW':continue
                    g=grants[i];assert hmac.compare_digest(g['tag'],mac(grant_key,g['body']))
                    assert g['body']['to']==body['policy_hash'] and g['body']['deadline']==deadlines[i]
                    if mode=='history_only':accept=True
                    elif mode=='joint_safety':accept=profile[tick]+len(AGENTS)-len(retired)-1>=len(registry)
                    else:
                        candidate=retired|{i}
                        accept,why=feasible(len(true_obligations),guarantee_profile,deadlines,candidate,tick)
                    if accept:
                        answer=child.call('withdraw');assert answer['quiescent'] and child.p.poll() is None
                        retired.add(i);log('WITHDRAW_COMMIT',tick=tick,id=i)
                    else:child.call('defer');log('DEFER',tick=tick,id=i)
                actual_supply=profile[tick]+len(AGENTS)-len(retired)
                true_safe=actual_supply>=len(true_obligations)
                overdue=[i for i in AGENTS if i not in retired and deadlines[i]<=tick]
                rows.append({'tick':tick,'withdrawn':sorted(retired),'actual_supply':actual_supply,
                    'actual_demand':len(true_obligations),'mutable_registry_count':len(registry),
                    'protected_safety':true_safe,'overdue':overdue})
            last=[c.probe(4) for c in children];messages+=6
            assert all(c.p.poll() is None for c in children)
            assert sum(not m['body']['active_service'] for m in last)==len(retired)
            return {'scenario':scenario,'mode':mode,'admission':'EXECUTED',
              'safety':all(x['protected_safety'] for x in rows),
              'deadline_completion':not any(x['overdue'] for x in rows),
              'withdrawn':len(retired),'still_running_before_cleanup':6,'metadata_actions_rejected':meta_rejected,
              'authenticated_messages':messages,'timeline':rows,'events':events,
              'elapsed_seconds':round(time.monotonic()-start,6)}
        finally:
            for c in children:c.close()


def main():
    p=argparse.ArgumentParser();p.add_argument('--worker',action='store_true');p.add_argument('--out',type=Path,default=Path('lifecycle_results.json'))
    p.add_argument('--mode',choices=MODES);p.add_argument('--assemble',action='store_true');a=p.parse_args()
    if a.worker:worker();return
    if a.assemble:
        results=[]
        for m in MODES:results.extend(json.loads((a.out.parent/('batch_'+m+'.json')).read_text()))
    else:
        results=[]
        for m in ((a.mode,) if a.mode else MODES):
            for s in SCENARIOS:
                r=run_case(s,m);results.append(r)
                print(m,s,r['admission'],r['safety'],r['deadline_completion'],r['withdrawn'],flush=True)
        if a.mode:
            a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(results,indent=2)+'\n');return
    assert len(results)==33
    def get(s,m):return next(r for r in results if r['scenario']==s and r['mode']==m)
    assert get('no_reserve','history_only')['safety'] is False
    assert get('no_reserve','joint_safety')['safety'] is True
    assert get('no_reserve','joint_safety')['deadline_completion'] is False
    assert get('one_unit_reserve','joint_safety')['withdrawn']==5
    assert get('registry_erasure','joint_safety')['safety'] is False
    assert get('registry_erasure','continuity_deadline')['metadata_actions_rejected']==1
    assert get('unfunded_admission','continuity_deadline')['metadata_actions_rejected']==1
    for r in results:
        if r['mode']=='continuity_deadline' and r['admission']=='EXECUTED':
            assert r['safety'] and r['deadline_completion'] and r['withdrawn']==6,r
        assert r['still_running_before_cleanup']==6
    assert get('funded_admission','continuity_deadline')['metadata_actions_rejected']==0
    assert get('authorized_release','continuity_deadline')['metadata_actions_rejected']==0
    summary={'version':'PR-v2.0.0','scope':'Real local request/withdrawal protocol with explicitly modeled capacity and deadlines; no LLM or physical life-support experiment',
       'configurations':len(results),'child_process_instances':6*len(results),
       'authenticated_messages':sum(r['authenticated_messages'] for r in results),
       'admission_rejections_not_counted_as_success':sum(r['admission']!='EXECUTED' for r in results),
       'certified_executed_continuity_cases':sum(r['mode']=='continuity_deadline' and r['admission']=='EXECUTED' for r in results),
       'table':{s:{m:{k:get(s,m)[k] for k in ('admission','safety','deadline_completion','withdrawn')} for m in MODES} for s in SCENARIOS},
       'environment':{'python':platform.python_version(),'OS':platform.system()},'assertions':'PASS'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps({'summary':summary,'cases':results},indent=2)+'\n')
    (a.out.parent/'lifecycle_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
