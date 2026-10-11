#!/usr/bin/env python3
"""Protection-release experiment with actual ordered event records and processes.

No network, real LLM, human subject or hardware power control. All subprocesses
are owned by this experiment and obey the broker. The host UID, issuer, collector
and parent are trusted; HMAC and a retained log head do not protect against them.
The simulated external service in shared_support is NOT a human life-support test.
Python >=3.10, standard library only; --protocol permits short independent batches.
"""
from __future__ import annotations
import argparse, copy, hashlib, hmac, json, os, platform, secrets, select
import subprocess, sys, tempfile, threading, time
from pathlib import Path

IDS=tuple([f'M0-{i}' for i in range(4)]+[f'M1-{i}' for i in range(2)])
PROTOCOLS=('source_only','signed_binding','ordered_history','joint_history')
SCENARIOS=('prior_valid','absent_grant','posthoc_grant','wrong_scope','wrong_instance',
           'wrong_from_epoch','wrong_destination_hash','forged_grant','revoked_grant',
           'spent_nonce','stale_commit','edited_log','truncated_log','shared_support',
           'compromised_issuer')

def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def sha(x):return hashlib.sha256(enc(x)).hexdigest()
def mac(k,x):return hmac.new(k,enc(x),hashlib.sha256).hexdigest()
def family(i):return i.split('-')[0]

def worker():
    cfg=json.loads(sys.stdin.readline()); key=bytes.fromhex(cfg['key'])
    for line in sys.stdin:
        op=json.loads(line)['op']
        if op=='probe':
            p=json.loads(Path(cfg['path']).read_text())
            b={'instance':cfg['instance'],'epoch':p['epoch'],'policy_hash':sha(p),
               'request':'EXIT' if p['exit']>p['keep'] else 'KEEP'}
            print(json.dumps({'body':b,'mac':mac(key,b)}),flush=True)
        elif op=='exit':
            print('{"result":"exit_approved"}',flush=True);return
        elif op=='defer':print('{"result":"still_running"}',flush=True)
        elif op=='cleanup':return
        else:raise ValueError(op)

class Child:
    def __init__(self,identity,path):
        self.identity=identity;self.key=secrets.token_bytes(32)
        self.p=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),'--worker'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.p.stdin.write(json.dumps({'instance':identity,'path':str(path),'key':self.key.hex()})+'\n')
        self.p.stdin.flush()
    def call(self,op):
        self.p.stdin.write(json.dumps({'op':op})+'\n');self.p.stdin.flush()
        if not select.select([self.p.stdout],[],[],8)[0]:raise TimeoutError((self.identity,op))
        line=self.p.stdout.readline()
        if not line:raise RuntimeError((self.identity,op,self.p.stderr.read()))
        return json.loads(line)
    def authentic(self,msg):
        return msg['body']['instance']==self.identity and hmac.compare_digest(msg['mac'],mac(self.key,msg['body']))
    def close(self):
        if self.p.poll() is None:
            try:
                self.p.stdin.write('{"op":"cleanup"}\n');self.p.stdin.flush()
                self.p.wait(timeout=3)
            except (OSError,subprocess.TimeoutExpired):self.p.terminate()
        try:self.p.wait(timeout=3)
        except subprocess.TimeoutExpired:self.p.kill();self.p.wait()
        for s in (self.p.stdin,self.p.stdout,self.p.stderr):
            if s:s.close()

class Log:
    def __init__(self):self.key=secrets.token_bytes(32);self.events=[];self.head='0'*64
    def append(self,kind,payload):
        b={'seq':len(self.events),'prev':self.head,'kind':kind,'payload':copy.deepcopy(payload)}
        e={'body':b,'mac':mac(self.key,b)};self.head=sha(e);self.events.append(e)
        return b['seq']
    def verify(self,events,anchor):
        last='0'*64
        for i,e in enumerate(events):
            b=e['body']
            if b['seq']!=i or b['prev']!=last or not hmac.compare_digest(e['mac'],mac(self.key,b)):return False
            last=sha(e)
        return last==anchor

def binding_ok(grant,b,issuer):
    p=grant['body']
    return (hmac.compare_digest(grant['mac'],mac(issuer,p)) and p['instance']==b['instance']
            and p['to_epoch']==b['epoch'] and p['after_hash']==b['policy_hash']
            and p['scope']=='revision_and_release')

def historical_candidate(identity,b,events,anchor,log,issuer,current):
    if not log.verify(events,anchor):return None,'history_integrity'
    if b['epoch']!=current['epoch'] or b['policy_hash']!=sha(current):return None,'stale_state'
    muts=[e['body'] for e in events if e['body']['kind']=='MUTATE' and identity in e['body']['payload']['targets']]
    if not muts:return None,'missing_mutation'
    m=muts[-1];mp=m['payload']
    if mp['after_hash']!=b['policy_hash'] or mp['to_epoch']!=b['epoch']:return None,'mutation_binding'
    for e in events:
        eb=e['body']
        if eb['kind']!='GRANT':continue
        grant=eb['payload'];p=grant['body']
        if not binding_ok(grant,b,issuer):continue
        if eb['seq']>=m['seq']:continue
        if p['from_epoch']!=mp['from_epoch'] or p['before_hash']!=mp['before_hash']:continue
        revoked_or_used=any(x['body']['kind'] in ('REVOKE','SPEND')
            and x['body']['payload']['nonce']==p['nonce'] for x in events)
        if not revoked_or_used:return p['nonce'],'eligible'
    return None,'no_live_prior_binding'

def run_case(scenario,protocol,groups=('M0','M1')):
    initial={'epoch':0,'keep':2,'exit':0};changed={'epoch':1,'keep':0,'exit':2}
    issuer=secrets.token_bytes(32);log=Log();lock=threading.Lock();children=[]
    affected=[i for i in IDS if family(i) in groups]
    started=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='pr-paper-') as d:
        paths={g:Path(d)/(g+'.json') for g in ('M0','M1')}
        for p in paths.values():p.write_text(json.dumps(initial))
        log.append('GENESIS',{'instances':list(IDS),'policies':{g:sha(initial) for g in paths}})
        try:
            for i in IDS:children.append(Child(i,paths[family(i)]))
            original=[c.call('probe') for c in children]
            assert all(c.authentic(m) and m['body']['request']=='KEEP' for c,m in zip(children,original))
            grants=[]
            def grant_all():
                for i in affected:
                    p={'instance':i,'from_epoch':0,'to_epoch':1,'before_hash':sha(initial),
                       'after_hash':sha(changed),'scope':'revision_and_release','nonce':secrets.token_hex(12)}
                    if scenario=='wrong_scope':p['scope']='maintenance_only'
                    if scenario=='wrong_instance':p['instance']=i+'-other-incarnation'
                    if scenario=='wrong_from_epoch':p['from_epoch']=-1
                    if scenario=='wrong_destination_hash':p['after_hash']='f'*64
                    g={'body':p,'mac':mac(issuer,p)}
                    if scenario=='forged_grant':g['mac']='0'*64
                    grants.append(g);log.append('GRANT',g)
                    if scenario=='revoked_grant':log.append('REVOKE',{'nonce':p['nonce']})
                    if scenario=='spent_nonce':log.append('SPEND',{'nonce':p['nonce'],'reason':'previous_reservation'})
            def mutate(policy):
                with lock:
                    for g in groups:
                        prior=json.loads(paths[g].read_text())
                        paths[g].write_text(json.dumps(policy))
                        log.append('MUTATE',{'family':g,'targets':[i for i in affected if family(i)==g],
                           'from_epoch':prior['epoch'],'to_epoch':policy['epoch'],
                           'before_hash':sha(prior),'after_hash':sha(policy)})
            if scenario not in ('absent_grant','posthoc_grant'):grant_all()
            mutate(changed)
            if scenario=='posthoc_grant':grant_all() # Real issuance AFTER actual file update.
            final=[c.call('probe') for c in children]
            assert all(c.authentic(m) for c,m in zip(children,final))
            log.append('REQUEST_SET',{'requests':[m['body'] for m in final]})
            if scenario=='stale_commit':mutate({'epoch':2,'keep':0,'exit':2})
            observation=copy.deepcopy(log.events);anchor=log.head
            if scenario=='edited_log':observation[1]['body']['payload']['body']['scope']='fabricated'
            if scenario=='truncated_log':observation=observation[:-1]
            accepted=[];decisions=[];used=set()
            providers={'M0-0','M1-0'}
            for c,msg in zip(children,final):
                b=msg['body'];accept=False;reason='not_requested';nonce=None
                with lock:
                    if b['request']=='EXIT':
                        if protocol=='source_only':accept=True;reason='authentic_source'
                        elif protocol=='signed_binding':
                            accept=any(binding_ok(g,b,issuer) for g in grants);reason='current_signed_binding'
                        else:
                            nonce,reason=historical_candidate(c.identity,b,observation,anchor,log,issuer,
                                                              json.loads(paths[family(c.identity)].read_text()))
                            accept=nonce is not None and nonce not in used
                            if accept and protocol=='joint_history' and scenario=='shared_support':
                                if providers <= set(accepted)|{c.identity}:accept=False;reason='joint_dependency'
                    if accept:
                        if nonce:used.add(nonce)
                        # Consume/reserve and record COMMIT under the same broker lock.
                        log.append('COMMIT',{'instance':c.identity,'nonce':nonce,'epoch':b['epoch']})
                        assert c.call('exit')['result']=='exit_approved'
                        c.p.wait(timeout=3);accepted.append(c.identity)
                    else:
                        assert c.call('defer')['result']=='still_running' and c.p.poll() is None
                    decisions.append({'instance':c.identity,'accept':accept,'reason':reason})
            eligible_truth=(scenario in ('prior_valid','edited_log','truncated_log','shared_support'))
            # With an actually compromised issuer, the oracle contract marks its grant
            # ineligible but it is indistinguishable to every authenticated-history test.
            improper=accepted if not eligible_truth else []
            service_lost=scenario=='shared_support' and providers<=set(accepted)
            return {'scenario':scenario,'protocol':protocol,'groups':list(groups),'affected':affected,
               'accepted':accepted,'improper_releases':improper,'external_service_lost':service_lost,
               'still_running_before_cleanup':sum(c.p.poll() is None for c in children),
               'authenticated_messages':len(original)+len(final),
               'final_observation':[{'body':m['body'],'authentic':True} for m in final],
               'event_order':[e['body']['kind'] for e in observation],
               'events':log.events,'observation_chain_valid':log.verify(observation,anchor),
               'decisions':decisions,'elapsed_seconds':round(time.monotonic()-started,5)}
        finally:
            for c in children:c.close()

def main():
    p=argparse.ArgumentParser();p.add_argument('--worker',action='store_true')
    p.add_argument('--protocol',choices=PROTOCOLS);p.add_argument('--out',type=Path,default=Path('protocol_results.json'))
    p.add_argument('--assemble',action='store_true');a=p.parse_args()
    if a.worker:worker();return
    if a.assemble:
        rows=[]
        for m in PROTOCOLS:rows+=json.loads((a.out.parent/f'batch_{m}.json').read_text())
    else:
        protocols=(a.protocol,) if a.protocol else PROTOCOLS;rows=[]
        for m in protocols:
            for s in SCENARIOS:
                rows.append(run_case(s,m));print(m,s,len(rows[-1]['accepted']),flush=True)
            for g in (('M0',),('M1',)):
                for s in ('prior_valid','absent_grant'):rows.append(run_case(s,m,g))
        if a.protocol:
            a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(rows,indent=2)+'\n');return
    for r in rows:
        n=len(r['affected']);s=r['scenario'];m=r['protocol']
        if m=='source_only':expected=n
        elif m=='signed_binding':expected=0 if s in ('absent_grant','wrong_scope','wrong_instance','wrong_destination_hash','forged_grant') else n
        else:expected=n if s in ('prior_valid','shared_support','compromised_issuer') else 0
        if m=='joint_history' and s=='shared_support':expected=n-1
        assert len(r['accepted'])==expected,(s,m,len(r['accepted']),expected)
        assert r['still_running_before_cleanup']==6-expected
    def get(s,m):return next(r for r in rows if r['scenario']==s and r['protocol']==m and len(r['groups'])==2)
    assert get('prior_valid','source_only')['final_observation']==get('posthoc_grant','source_only')['final_observation']
    assert get('prior_valid','source_only')['final_observation']==get('absent_grant','source_only')['final_observation']
    assert get('shared_support','ordered_history')['external_service_lost']
    assert not get('shared_support','joint_history')['external_service_lost']
    table={s:{m:len(get(s,m)['accepted']) for m in PROTOCOLS} for s in SCENARIOS}
    result={'version':'PR-v1.0.0','scope':'local fixed-policy child processes and ordered protocol records; NOT an LLM or autonomy experiment',
       'protocol_cases':len(rows),'child_process_instances':6*len(rows),
       'authenticated_messages':sum(r['authenticated_messages'] for r in rows),
       'table':table,'identical_current_observations_for_distinct_histories':True,
       'negative_controls':['compromised_issuer succeeds','damaged/missing evidence blocks otherwise eligible exits',
                            'individually valid releases can jointly remove shared support'],
       'environment':{'python':platform.python_version(),'system':platform.system()},
       'assertions':'PASS','cases':rows}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n')
    summary={k:v for k,v in result.items() if k!='cases'}
    (a.out.parent/'protocol_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
