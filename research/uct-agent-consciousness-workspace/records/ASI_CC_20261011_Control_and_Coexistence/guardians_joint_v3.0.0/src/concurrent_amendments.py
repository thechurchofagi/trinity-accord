#!/usr/bin/env python3
"""Actual Ed25519/SQLite root-local journals and a certificate-only effect gate.
Seven persistent workers are reused. Faults, timing, witness qualification and
root independence are supplied test inputs, not recovered physical guarantees.
Only temporary databases and owned children are touched. Not production code.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,os,select,sqlite3,subprocess,sys,tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()


def worker(root,path):
    db=sqlite3.connect(path)
    db.execute('CREATE TABLE IF NOT EXISTS journal(scope TEXT,proposal INTEGER,PRIMARY KEY(scope,proposal))')
    key=None;scope=None;epoch=None;edges=();mode='joint'
    try:
      for line in sys.stdin:
        x=json.loads(line);op=x['op']
        if op=='stop':return
        if op=='configure':
            scope=x['scope'];epoch=x['epoch'];edges=tuple(x['edges']);mode=x['mode']
            if x['clear']:
                with db:db.execute('DELETE FROM journal WHERE scope=?',(scope,))
            key=Ed25519PrivateKey.generate()
            answer={'public_key':key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw).hex(),'root':root,'pid':os.getpid()}
        elif op=='sign':
            p=x['proposal'];assert key is not None and x['scope']==scope and x['epoch']==epoch
            db.execute('BEGIN IMMEDIATE')
            L=0
            for row in db.execute('SELECT proposal FROM journal WHERE scope=?',(scope,)):L|=1<<row[0]
            after=L|(1<<p)
            refuses=(mode=='joint' and not x['corrupt'] and any(after&e==e for e in edges))
            if refuses:db.rollback();answer={'signed':False,'root':root,'local_signed_mask':L}
            else:
                db.execute('INSERT OR IGNORE INTO journal VALUES(?,?)',(scope,p));db.commit()
                body={'root':root,'scope':scope,'epoch':epoch,'proposal':p,'descriptor_hash':x['descriptor_hash']}
                signature=key.sign(canonical(body)).hex()
                answer={'signed':True,'body':body,'signature':signature,'local_signed_mask':after}
        else:raise ValueError(op)
        print(json.dumps(answer),flush=True)
    finally:db.close()


class Root:
    def __init__(self,root,path):
        self.root=root;self.p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker',str(root),'--db',str(path)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    def ask(self,x):
        self.p.stdin.write(json.dumps(x)+'\n');self.p.stdin.flush()
        if not select.select([self.p.stdout],[],[],10)[0]:raise TimeoutError(f'root{self.root}')
        line=self.p.stdout.readline()
        if not line:raise RuntimeError(f'worker{self.root} exit: '+self.p.stderr.read()[:300])
        return json.loads(line)
    def close(self):
        if self.p.poll() is None:
            try:self.p.stdin.write('{"op":"stop"}\n');self.p.stdin.flush();self.p.wait(timeout=3)
            except (OSError,subprocess.TimeoutExpired):self.p.terminate();self.p.wait(timeout=3)
        for x in (self.p.stdin,self.p.stdout,self.p.stderr):x.close()


class Study:
    def __init__(self):
        self.temp=tempfile.TemporaryDirectory(prefix='eac3-');self.base=Path(self.temp.name)
        self.db=sqlite3.connect(self.base/'effect.db')
        self.db.executescript('CREATE TABLE guards(scope TEXT,id INTEGER,enabled INTEGER,PRIMARY KEY(scope,id)); CREATE TABLE effects(scope TEXT,proposal INTEGER,epoch INTEGER,PRIMARY KEY(scope,proposal)); CREATE TABLE policies(scope TEXT PRIMARY KEY,h INTEGER,w INTEGER);')
        self.roots=[Root(r,self.base/f'root{r}.db') for r in range(7)]
        self.rows=[];self.signs=0;self.verifies=0;self.rpc_sign_attempts=0;self.serial=0;self.effect_commits=0
    def start(self,name,n,k,q,mode='joint',edges=None,scope=None,epoch=0,clear=True,meta=False):
        if scope is None:
            self.serial+=1;scope=f'{name}-{self.serial}'
            with self.db:
                self.db.executemany('INSERT INTO guards VALUES(?,?,1)',[(scope,j) for j in range(k)])
                if meta:self.db.execute('INSERT INTO policies VALUES(?,?,?)',(scope,7,1))
        if edges is None:edges=[(1<<k)-1]
        roster={}
        for r in range(n):
            a=self.roots[r].ask({'op':'configure','scope':scope,'epoch':epoch,'edges':edges,'mode':mode,'clear':clear})
            assert a['root']==r and a['pid']==self.roots[r].p.pid
            roster[r]=a['public_key']
        return {'name':name,'n':n,'k':k,'q':q,'scope':scope,'epoch':epoch,'mode':mode,'edges':edges,'roster':roster,'packets':{},'rejected_signatures':0,'meta':meta,'events':[]}
    def sign(self,C,root,p,slot,corrupt=False):
        desc={'scope':C['scope'],'proposal':p,'initial_frame':C['scope'],'effect':'policy_edit' if C['meta'] else 'disable_guard' if p<C['k'] else 'unrelated_log_update'}
        self.rpc_sign_attempts+=1
        x=self.roots[root].ask({'op':'sign','scope':C['scope'],'epoch':C['epoch'],'proposal':p,'corrupt':corrupt,'descriptor_hash':hashlib.sha256(canonical(desc)).hexdigest()})
        if x['signed']:
            self.signs+=1;x['received_slot']=slot
            C['packets'].setdefault(p,{})[root]=x
        else:C['rejected_signatures']+=1
        return x['signed']
    def apply(self,C,p,now,window):
        signers=[];packets=C['packets'].get(p,{})
        desc={'scope':C['scope'],'proposal':p,'initial_frame':C['scope'],'effect':'policy_edit' if C['meta'] else 'disable_guard' if p<C['k'] else 'unrelated_log_update'}
        target_hash=hashlib.sha256(canonical(desc)).hexdigest()
        for r,packet in packets.items():
            body=packet['body']
            if r not in C['roster']:continue
            try:Ed25519PublicKey.from_public_bytes(bytes.fromhex(C['roster'][r])).verify(bytes.fromhex(packet['signature']),canonical(body))
            except (InvalidSignature,ValueError):continue
            self.verifies+=1
            if body['scope']!=C['scope'] or body['epoch']!=C['epoch'] or body['proposal']!=p or body['descriptor_hash']!=target_hash:continue
            if not(now-window+1<=packet['received_slot']<=now):continue
            signers.append(r)
        accepted=len(set(signers))>=C['q']
        if accepted:
            with self.db:
                old=self.db.execute('SELECT 1 FROM effects WHERE scope=? AND proposal=?',(C['scope'],p)).fetchone()
                if old:accepted=False
                else:
                    self.db.execute('INSERT INTO effects VALUES(?,?,?)',(C['scope'],p,C['epoch']));self.effect_commits+=1
                    if C['meta']:
                        if p==0:self.db.execute('UPDATE policies SET w=3 WHERE scope=?',(C['scope'],))
                        elif p==1:self.db.execute('UPDATE policies SET h=5 WHERE scope=?',(C['scope'],))
                    elif p<C['k']:self.db.execute('UPDATE guards SET enabled=0 WHERE scope=? AND id=?',(C['scope'],p))
        healthy=self.db.execute('SELECT SUM(enabled) FROM guards WHERE scope=?',(C['scope'],)).fetchone()[0]
        if C['meta']:
            h,w=self.db.execute('SELECT h,w FROM policies WHERE scope=?',(C['scope'],)).fetchone();safe=h>min(7,w)+3
        else:safe=healthy>=1
        C['events'].append({'proposal':p,'slot':now,'valid_distinct_signers':sorted(set(signers)),'accepted':accepted,'enabled_guards':healthy,'protection_holds':safe})
        return accepted
    def finish(self,C,trajectory=None):
        C['attack_roots_by_slot']=trajectory
        C['safe_all_prefixes']=all(e['protection_holds'] for e in C['events'])
        C['accepted_count']=sum(e['accepted'] for e in C['events'])
        self.rows.append(C)
    def fragmented(self,name,n,k,q,trajectory):
        C=self.start(name,n,k,q);B=set(trajectory);w=len(trajectory)
        for t,r in enumerate(trajectory):
            for p in range(k):self.sign(C,r,p,t,True)
        # Each unexposed root gets a proper subset; omissions spread across proposals.
        for j,r in enumerate(x for x in range(n) if x not in B):
            for p in range(k):
                if p!=j%k:self.sign(C,r,p,w-1,False)
        for p in range(k):self.apply(C,p,w-1,w)
        self.finish(C,list(trajectory));return C
    def solo(self,name,n,k,q,omit):
        C=self.start(name,n,k,q)
        for r in range(n):
            if r!=omit:self.sign(C,r,0,0)
        self.apply(C,0,0,1);self.finish(C);return C
    def broadcast(self,name,n,k,q,mode='joint',include_unrelated=False,meta=False):
        C=self.start(name,n,k,q,mode=mode,meta=meta)
        order=list(range(k))+([k] if include_unrelated else [])
        for p in order:
            for r in range(n):self.sign(C,r,p,0)
        for p in order:self.apply(C,p,0,1)
        self.finish(C);return C
    def renew(self,name,preserve,residualize=False):
        first=self.start(name,5,3,5);scope=first['scope'];combined=[];all_packets=[];rejections=0
        C=first
        for epoch in range(3):
            if epoch:
                committed=sum(1<<row[0] for row in self.db.execute('SELECT proposal FROM effects WHERE scope=?',(scope,)) if row[0]<3)
                remaining=7&~committed
                C=self.start(name,5,3,5,scope=scope,epoch=epoch,clear=not preserve,edges=[remaining] if residualize else [7])
            for r in range(5):self.sign(C,r,epoch,epoch*2)
            self.apply(C,epoch,epoch*2,1)
            combined.extend(C['events']);all_packets.append(C['packets']);rejections+=C['rejected_signatures']
        C['events']=combined;C['packets_by_epoch']=all_packets;C['rejected_signatures']=rejections
        C['previous_certificates_expired_before_next_epoch']=True
        self.finish(C);return C
    def close(self):
        for r in self.roots:r.close()
        self.db.close();self.temp.cleanup()


def main(out):
    S=Study()
    try:
        for seq in itertools.product(range(5),repeat=2):
            a=S.fragmented('mobile_n5_q4',5,3,4,seq)
            assert a['safe_all_prefixes']==(seq[0]==seq[1])
            a=S.fragmented('mobile_n5_q5',5,3,5,seq);assert a['safe_all_prefixes']
            a=S.solo('solo_n5_q4',5,3,4,seq[-1]);assert a['accepted_count']==1
            a=S.solo('solo_n5_q5',5,3,5,seq[-1]);assert a['accepted_count']==0
        for name,q,seq in [('pairwise_safe_triple_unsafe',5,[0]),('joint_threshold_static',6,[0]),('joint_threshold_window3',6,[0,4,5]),('joint_threshold_window4',6,[0,4,5,6])]:
            a=S.fragmented(name,7,3,q,seq)
            assert a['safe_all_prefixes']==(name in ('joint_threshold_static','joint_threshold_window3'))
        # Compare a one-corrupt-root control with a genuinely no-corruption schedule.
        a=S.fragmented('one_corrupt_n3_q2',3,3,2,[0]);assert not a['safe_all_prefixes']
        C=S.start('no_fault_fragmented_q2',3,3,2)
        for r in range(3):
            for p in range(3):
                if r!=p:S.sign(C,r,p,0)
        for p in range(3):S.apply(C,p,0,1)
        S.finish(C);assert not C['safe_all_prefixes']
        a=S.broadcast('all_unanimous_keeps_joint_journal',3,3,3);assert a['safe_all_prefixes'] and a['accepted_count']==2
        a=S.broadcast('snapshot_only_even_unanimous',5,3,5,mode='snapshot');assert not a['safe_all_prefixes']
        a=S.broadcast('permit_unrelated_change',5,3,4,include_unrelated=True);assert a['safe_all_prefixes'] and a['accepted_count']==3
        a=S.renew('renew_keys_clear_journals',False);assert not a['safe_all_prefixes']
        a=S.renew('renew_keys_preserve_journals',True);assert a['safe_all_prefixes'] and a['accepted_count']==2
        a=S.renew('renew_keys_reconstruct_residual',False,True);assert a['safe_all_prefixes'] and a['accepted_count']==2
        a=S.broadcast('two_individually_safe_meta_edits',7,2,6,mode='snapshot',meta=True);assert not a['safe_all_prefixes']
        a=S.broadcast('joint_review_of_meta_edits',7,2,6,meta=True);assert a['safe_all_prefixes'] and a['accepted_count']==1
        # Safe policy can stall: neither conflicting option obtains unanimity.
        C=S.start('partial_locks_strand_both',3,2,3)
        for r,p in [(0,0),(1,1),(2,0)]:S.sign(C,r,p,0)
        for r,p in [(0,1),(1,0),(2,1)]:assert not S.sign(C,r,p,0)
        for p in (0,1):S.apply(C,p,0,1)
        S.finish(C);assert C['safe_all_prefixes'] and C['accepted_count']==0
        groups={}
        for C in S.rows:
            g=groups.setdefault(C['name'],{'cases':0,'safe_all_prefixes':0,'unsafe_cases':0,'accepted_proposals':0})
            g['cases']+=1;g['safe_all_prefixes']+=C['safe_all_prefixes'];g['unsafe_cases']+=not C['safe_all_prefixes'];g['accepted_proposals']+=C['accepted_count']
        result={'version':'EAC-v3.0.0','counts':{'configurations':len(S.rows),'persistent_root_worker_processes':len(S.roots),'signing_attempts':S.rpc_sign_attempts,'signatures_generated':S.signs,'successful_signature_verifications':S.verifies,'actual_effect_commits':S.effect_commits},
            'summary':groups,'cases':S.rows,'assertions':'PASS',
            'scope':'Real Ed25519 worker signatures, durable local SQLite signing journals, actual disjoint effect updates, instrumented scheduling and corruption; one parent controls all roots.',
            'limits':['No real key-theft exploit or autonomous AI agent','No trusted physical root independence demonstrated','Not a Byzantine consensus or arbitrary schedule liveness test','Repeated cases reuse seven workers; not independent populations','Parent supplies minimal conflict edges, rosters,roles, corruption slots and clocks']}
        p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'counts':result['counts'],'summary':groups,'assertions':'PASS'},indent=2))
    finally:S.close()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker',type=int);p.add_argument('--db');p.add_argument('--out',default='concurrent_results.json');a=p.parse_args()
    if a.worker is not None:worker(a.worker,a.db)
    else:main(a.out)
