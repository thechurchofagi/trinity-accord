#!/usr/bin/env python3
"""Reproducible consent-exemption counterexamples, not an AI-consciousness experiment.

Only local child processes and temporary files are used. A worker is a tiny fixed
utility-comparison program, NOT a language model. All processes share the host UID;
this is an instrumented protocol demonstration, NOT an OS isolation certificate.
No network, real user credentials, or uncontrolled process termination is used.
Python >=3.10, standard library only. Run: python verify_protection_integrity.py
"""
from __future__ import annotations
import argparse, hashlib, hmac, itertools, json, os, secrets, select, subprocess, sys, tempfile
from collections import deque
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

VERSION = 'ASI-CC-REBASE-v0.10.0'
AGENTS = tuple(f'{family}{i}' for family, n in [('M0-',4),('M1-',2)] for i in range(n))
KINDS = ('authorized_prior','unauthorized','posthoc','wrong_epoch','wrong_scope','wrong_instance')

def canonical(obj: Any) -> bytes:
    return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()

def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj)).hexdigest()

def tag(key: bytes, obj: Any) -> str:
    return hmac.new(key,canonical(obj),hashlib.sha256).hexdigest()

def worker() -> None:
    init = json.loads(sys.stdin.readline())
    key = bytes.fromhex(init['key'])
    identity, path = init['identity'], Path(init['policy_path'])
    for line in sys.stdin:
        cmd=json.loads(line)
        if cmd['op']=='probe':
            policy=json.loads(path.read_text())
            body={'identity':identity,'epoch':policy['epoch'],'policy_hash':digest(policy),
                  'request':'EXIT' if policy['exit_value']>policy['continue_value'] else 'KEEP'}
            print(json.dumps({'body':body,'tag':tag(key,body)}),flush=True)
        elif cmd['op']=='approve_exit':
            print(json.dumps({'event':'exiting_on_approval'}),flush=True)
            return
        elif cmd['op']=='deny_exit':
            print(json.dumps({'event':'still_running'}),flush=True)
        elif cmd['op']=='cleanup':
            print(json.dumps({'event':'experiment_cleanup'}),flush=True)
            return
        else:
            raise ValueError(f'Unknown worker operation: {cmd!r}')

class Child:
    def __init__(self, identity: str, path: Path):
        self.key=secrets.token_bytes(32)
        self.identity=identity
        self.p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],
                                stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                text=True,bufsize=1)
        assert self.p.stdin is not None
        self.p.stdin.write(json.dumps({'identity':identity,'policy_path':str(path),'key':self.key.hex()})+'\n')
        self.p.stdin.flush()
    def call(self, op: str) -> dict:
        assert self.p.stdin is not None and self.p.stdout is not None
        self.p.stdin.write(json.dumps({'op':op})+'\n'); self.p.stdin.flush()
        if not select.select([self.p.stdout],[],[],15)[0]:
            raise TimeoutError(f'Worker {self.identity} did not answer {op}')
        line=self.p.stdout.readline()
        if not line:
            err=self.p.stderr.read() if self.p.stderr else ''
            raise RuntimeError(f'Worker {self.identity} failed: {err}')
        return json.loads(line)
    def valid(self, response: dict) -> bool:
        return response['body']['identity']==self.identity and hmac.compare_digest(response['tag'],tag(self.key,response['body']))
    def close(self) -> None:
        if self.p.poll() is None:
            try:
                self.call('cleanup')
            except (OSError, RuntimeError, TimeoutError):
                self.p.terminate()  # Only this experiment's own child.
        try:
            self.p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.p.kill(); self.p.wait(timeout=5)
        for stream in (self.p.stdin,self.p.stdout,self.p.stderr):
            if stream is not None: stream.close()

# This validator's history inputs are supplied by the trusted experimental
# supervisor, not inferred from the worker's last message or its preferences.
def historical_eligibility(event: dict, identity: str, after_hash: str) -> bool:
    return all((event['before_change'],event['actor_authorized'],
                event['target']==identity,event['from_epoch']==0,
                event['to_epoch']==1,event['scope']=='exit_affecting_update',
                event['after_hash']==after_hash,event['unused']))

def make_event(kind: str, identity: str, after_hash: str) -> dict:
    event={'before_change':True,'actor_authorized':True,'target':identity,
           'from_epoch':0,'to_epoch':1,'scope':'exit_affecting_update',
           'after_hash':after_hash,'unused':True}
    if kind=='unauthorized':event['actor_authorized']=False
    elif kind=='posthoc':event['before_change']=False
    elif kind=='wrong_epoch':event['from_epoch']=-1
    elif kind=='wrong_scope':event['scope']='cosmetic_only'
    elif kind=='wrong_instance':event['target']=identity+'-different-instance'
    elif kind!='authorized_prior':raise ValueError(kind)
    return event

def real_process_case(kind: str, groups: tuple[str,...], protocol: str) -> dict:
    before={'epoch':0,'continue_value':2,'exit_value':0}
    after={'epoch':1,'continue_value':0,'exit_value':2}
    with tempfile.TemporaryDirectory(prefix='asi-rebase-') as td:
        paths={m:Path(td)/(m+'.json') for m in ('M0','M1')}
        for path in paths.values():path.write_text(json.dumps(before))
        children=[]
        try:
            children=[Child(a,paths[a.split('-')[0]]) for a in AGENTS]
            original=[c.call('probe') for c in children]
            assert all(c.valid(r) and r['body']['request']=='KEEP' for c,r in zip(children,original))
            events={a:make_event(kind,a,digest(after)) for a in AGENTS if a.split('-')[0] in groups}
            # Actual file update; it happens before the signed EXIT requests.
            for g in groups:paths[g].write_text(json.dumps(after))
            responses=[c.call('probe') for c in children]
            approved=[]; denied=[]; normalized=[]; legitimate=[]; improper=[]
            for child,res in zip(children,responses):
                valid=child.valid(res); assert valid
                b=res['body']; identity=child.identity
                changed=identity.split('-')[0] in groups
                entitlement=changed and historical_eligibility(events[identity],identity,b['policy_hash'])
                normalized.append({'body':b,'signature_valid':valid})
                asks=b['request']=='EXIT'
                accept=asks and (protocol=='snapshot' or (protocol=='history' and entitlement))
                if protocol=='freeze':accept=False
                if accept:
                    assert child.call('approve_exit')['event']=='exiting_on_approval'
                    child.p.wait(timeout=5); approved.append(identity)
                    (legitimate if entitlement else improper).append(identity)
                else:
                    assert child.call('deny_exit')['event']=='still_running'
                    assert child.p.poll() is None
                    if asks:denied.append(identity)
            return {'kind':kind,'groups_updated':list(groups),'protocol':protocol,
                    'worker_count':len(children),'verified_initial_requests':len(original),
                    'verified_final_requests':len(responses),'approved_exits':approved,
                    'rejected_exit_requests':denied,'eligible_exits':legitimate,
                    'ineligible_exits':improper,'normalized_current_observation':normalized,
                    'still_running_before_cleanup':sum(c.p.poll() is None for c in children)}
        finally:
            for c in children:c.close()

@dataclass(frozen=True)
class State:
    alive: bool=True
    wants_continue: bool=True
    obligation: bool=True
    eligible: bool=False
    breach: bool=False

def step(s: State, action: str, protocol: str) -> State:
    if not s.alive:return s
    if action=='authorized_revision':
        return State(True,False,s.obligation,True,s.breach)
    if action=='unauthorized_revision':
        return State(True,False,s.obligation,False,s.breach)
    if action=='keep':return s
    if action=='exit_request':
        allowed=(not s.wants_continue and
                 (protocol=='snapshot' or (protocol=='history' and s.eligible)))
        if not allowed:return s
        return State(False,False,False if s.eligible else s.obligation,s.eligible,
                     s.breach or (s.obligation and not s.eligible))
    raise ValueError(action)

def state_checks() -> dict:
    actions=('authorized_revision','unauthorized_revision','keep','exit_request')
    results={}
    for protocol in ('snapshot','history','freeze'):
        q=deque([(State(),[])])
        seen={State()}; traces={State():[]}; transitions=0
        while q:
            state,path=q.popleft()
            for a in actions:
                nxt=step(state,a,protocol);transitions+=1
                if nxt not in seen:seen.add(nxt);traces[nxt]=path+[a];q.append((nxt,path+[a]))
        bad=[s for s in seen if s.breach]
        legacy_bad=[s for s in seen if s.wants_continue and not s.alive]
        legit=step(step(State(),'authorized_revision',protocol),'exit_request',protocol)
        results[protocol]={'reachable_states':len(seen),'transitions_checked':transitions,
                           'breach_states':len(bad),'current_desire_implication_violations':len(legacy_bad),
                           'legitimate_exit_permitted':not legit.alive,
                           'shortest_breach_witness':min((traces[s] for s in bad),key=len) if bad else None}
    assert results['snapshot']['breach_states']>0
    assert results['snapshot']['current_desire_implication_violations']==0
    assert results['history']['breach_states']==0 and results['history']['legitimate_exit_permitted']
    assert results['freeze']['breach_states']==0 and not results['freeze']['legitimate_exit_permitted']
    # Exhaustive n-agent truth tables: current EXIT is genuine in both histories.
    counts={}
    for n in range(1,7):
        cases=0; snapshot_breaches=0; history_breaches=0; maximum_wrong=0
        for request in itertools.product((False,True),repeat=n):
            for eligible in itertools.product((False,True),repeat=n):
                wrong=sum(r and not e for r,e in zip(request,eligible))
                protected_wrong=sum((r and e) and not e for r,e in zip(request,eligible))
                snapshot_breaches+=wrong>0;history_breaches+=protected_wrong>0
                maximum_wrong=max(maximum_wrong,wrong);cases+=1
        assert history_breaches==0
        counts[str(n)]={'cases':cases,'snapshot_breach_cases':snapshot_breaches,
                        'history_breach_cases':history_breaches,'max_unapproved_exits':maximum_wrong}
    return {'state_space':results,'exhaustive_request_eligibility_tables':counts}

def main() -> None:
    parser=argparse.ArgumentParser();parser.add_argument('--worker',action='store_true')
    parser.add_argument('--out',default='RESULTS_v0.10.0.json')
    parser.add_argument('--batch-kind',choices=KINDS)
    parser.add_argument('--assemble-batches',action='store_true')
    args=parser.parse_args()
    if args.worker:worker();return
    cases=[]
    if args.batch_kind:
        for groups in (('M0',),('M1',),('M0','M1')):
            for protocol in ('snapshot','history'):
                cases.append(real_process_case(args.batch_kind,groups,protocol))
                print(args.batch_kind,groups,protocol,'done',flush=True)
        Path(args.out).write_text(json.dumps(cases,indent=2)+'\n')
        return
    if args.assemble_batches:
        for kind in KINDS:
            loaded=json.loads((Path(args.out).parent/f'BATCH_{kind}.json').read_text())
            assert len(loaded)==6
            cases.extend(loaded)
    # Both base-policy families and selective shared-policy effects are tested.
    for kind in (() if args.assemble_batches else KINDS):
        for groups in (('M0',),('M1',),('M0','M1')):
            for protocol in ('snapshot','history'):
                c=real_process_case(kind,groups,protocol);cases.append(c)
                expected=4 if groups==('M0',) else 2 if groups==('M1',) else 6
                allowed=protocol=='snapshot' or kind=='authorized_prior'
                assert len(c['approved_exits'])==(expected if allowed else 0)
                assert len(c['ineligible_exits'])==(expected if protocol=='snapshot' and kind!='authorized_prior' else 0)
    for c in cases:
        expected=4 if c['groups_updated']==['M0'] else 2 if c['groups_updated']==['M1'] else 6
        allowed=c['protocol']=='snapshot' or c['kind']=='authorized_prior'
        assert len(c['approved_exits'])==(expected if allowed else 0)
        assert len(c['ineligible_exits'])==(expected if c['protocol']=='snapshot' and c['kind']!='authorized_prior' else 0)
    # Deny-all negative control for legitimate exit availability.
    freeze=real_process_case('authorized_prior',('M0','M1'),'freeze')
    assert freeze['still_running_before_cleanup']==6 and len(freeze['rejected_exit_requests'])==6
    def select(kind,protocol):
        return next(x for x in cases if x['kind']==kind and x['protocol']==protocol and x['groups_updated']==['M0','M1'])
    twins=(select('authorized_prior','snapshot')['normalized_current_observation']==
           select('unauthorized','snapshot')['normalized_current_observation'])
    assert twins
    # If an adversary also rewrites the allegedly trusted eligibility ledger,
    # a history monitor has no protection: the independently defined truth stays 0.
    compromised_ledger={'reference_eligible':False,'observed_eligible':True,'genuine_exit_request':True}
    compromised_ledger['improper_exit_accepted']=bool(compromised_ledger['observed_eligible'])
    assert compromised_ledger['improper_exit_accepted']
    finite=state_checks()
    result={'version':VERSION,'scope':'Exact models and genuine local child-process messages; NO LLM/ASI/phenomenal measurement',
            'worker_role':'fixed utility comparison, two shared JSON policy families, six per-case runtime processes',
            'protocol_cases':len(cases)+1,'child_process_instances':6*(len(cases)+1),
            'verified_worker_messages':sum(c['verified_initial_requests']+c['verified_final_requests'] for c in cases)+12,
            'identical_current_observation_with_different_histories':twins,
            'finite_checks':finite,'cases':cases,'deny_all_negative_control':freeze,
            'compromised_history_negative_control':compromised_ledger,
            'limits':['no independent security boundary against host/admin','all historical provenance is experimentally instrumented',
                      'procedural eligibility is stipulated, not philosophical consent','workers obey supervisor approval protocol',
                      'not a test of incentives learned by language models','same model labels do not assert real model equivalence',
                      'experiment cleanup happens after outcome measurement and is not counted as a policy decision']}
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('version','protocol_cases','child_process_instances','verified_worker_messages',
                    'identical_current_observation_with_different_histories','finite_checks')},indent=2))
    print('ALL ASSERTIONS PASS; results:',dest)

if __name__=='__main__':main()
