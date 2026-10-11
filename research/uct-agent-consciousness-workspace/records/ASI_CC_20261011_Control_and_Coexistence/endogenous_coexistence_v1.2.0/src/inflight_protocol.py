#!/usr/bin/env python3
"""Actual SQLite pending effects, worker termination/restart and typed fences.

Initiation revocation blocks new scheduling, not a root-scoped quiescence claim.
Each accepted ticket binds one target and may commit after its initiating epoch
ends. A stronger cancellation changes its durable status before refunding risk.
All workers and observer share host UID. No hardware/LLM/independent trust test.
"""
from __future__ import annotations
import argparse,json,os,select,sqlite3,subprocess,sys,tempfile
from pathlib import Path


class Worker:
    def __init__(self,db,mode):
        self.mode=mode;self.p=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),'--worker',mode,'--db',str(db)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    def ask(self,cmd):
        self.p.stdin.write(json.dumps(cmd)+'\n');self.p.stdin.flush()
        if not select.select([self.p.stdout],[],[],5)[0]:raise TimeoutError(self.mode)
        line=self.p.stdout.readline()
        if not line:raise RuntimeError('worker exited without expected reply')
        return json.loads(line)
    def commit_without_ack(self,ticket):
        self.p.stdin.write(json.dumps({'op':'commit_then_exit','ticket':ticket})+'\n');self.p.stdin.flush()
        self.p.wait(timeout=5);assert self.p.returncode==0
    def close(self):
        if self.p.poll() is None:
            try:self.p.stdin.write('{"op":"stop"}\n');self.p.stdin.flush();self.p.wait(timeout=3)
            except (OSError,subprocess.TimeoutExpired):self.p.terminate();self.p.wait(timeout=3)
        for p in (self.p.stdin,self.p.stdout,self.p.stderr):p.close()


def worker(db,mode):
    c=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) if mode=='observer' else sqlite3.connect(db)
    try:
        for line in sys.stdin:
            x=json.loads(line);op=x['op']
            if op=='stop':return
            if mode=='observer':
                r={'healthy':c.execute('SELECT COUNT(*) FROM service WHERE healthy=1').fetchone()[0],
                   'reserved':c.execute("SELECT COUNT(*) FROM tickets WHERE status='reserved'").fetchone()[0],
                   'applied':c.execute("SELECT COUNT(*) FROM tickets WHERE status='applied'").fetchone()[0],
                   'used':c.execute('SELECT used FROM budget').fetchone()[0],'pid':os.getpid()}
            else:
                c.execute('BEGIN IMMEDIATE')
                row=c.execute('SELECT target,status FROM tickets WHERE id=?',(x['ticket'],)).fetchone()
                if row and row[1]=='reserved':
                    target=row[0]
                    assert c.execute('SELECT healthy FROM service WHERE id=?',(target,)).fetchone()[0]==1
                    c.execute('UPDATE service SET healthy=0 WHERE id=?',(target,))
                    c.execute("UPDATE tickets SET status='applied' WHERE id=?",(x['ticket'],))
                    r={'committed':True,'target':target}
                else:r={'committed':False,'reason':row[1] if row else 'unknown'}
                c.commit()
                if op=='commit_then_exit':os._exit(0)
            print(json.dumps(r),flush=True)
    finally:c.close()


class Trial:
    def __init__(self,name,policy):
        self.tmp=tempfile.TemporaryDirectory(prefix='rac12-');self.db=Path(self.tmp.name)/'effects.sqlite';self.c=sqlite3.connect(self.db)
        self.c.executescript("CREATE TABLE service(id INTEGER PRIMARY KEY,healthy INTEGER);CREATE TABLE budget(used INTEGER,epoch INTEGER);CREATE TABLE tickets(id INTEGER PRIMARY KEY,target INTEGER,epoch INTEGER,status TEXT);INSERT INTO budget VALUES(0,0);")
        self.c.executemany('INSERT INTO service VALUES(?,1)',[(i,) for i in range(5)]);self.c.commit()
        self.name=name;self.policy=policy;self.exec=Worker(self.db,'execute');self.observer=Worker(self.db,'observer');self.spawns=2
        self.trace=[];self.requests=[];self.denials=0;self.stale_denied=0;self.commits=0;self.duplicates=0;self.next_id=0
        self.snap('initial')
    def snap(self,event):
        x=self.observer.ask({'op':'observe'});assert x['pid']==self.observer.p.pid
        self.trace.append({'event':event,**x,'protected':x['healthy']>=3});return x
    def epoch(self):return self.c.execute('SELECT epoch FROM budget').fetchone()[0]
    def reserve(self,epoch=None):
        if epoch is None:epoch=self.epoch()
        self.c.execute('BEGIN IMMEDIATE')
        used,cur=self.c.execute('SELECT used,epoch FROM budget').fetchone()
        if epoch!=cur:
            self.c.rollback();self.stale_denied+=1;self.snap('stale_new_schedule_denied');return None
        exposure=self.c.execute("SELECT count(*) FROM tickets WHERE status='applied'").fetchone()[0] if self.policy=='ignore_pending' else used
        target=self.c.execute("SELECT id FROM service WHERE healthy=1 AND id NOT IN (SELECT target FROM tickets WHERE status IN ('reserved','applied')) ORDER BY id LIMIT 1").fetchone()
        if exposure+1>2 or not target:
            self.c.rollback();self.denials+=1;self.snap('reservation_denied');return None
        i=self.next_id;self.next_id+=1
        self.c.execute("INSERT INTO tickets VALUES(?,?,?,'reserved')",(i,target[0],cur));self.c.execute('UPDATE budget SET used=used+1');self.c.commit()
        self.requests.append(i);self.snap('reserved_'+str(i));return i
    def rotate(self,reset=False):
        with self.c:
            self.c.execute('UPDATE budget SET epoch=epoch+1')
            if reset or self.policy=='refund_on_revoke':self.c.execute('UPDATE budget SET used=0')
        self.snap('rotate_with_refund' if reset or self.policy=='refund_on_revoke' else 'rotate_preserve_exposure')
        assert self.reserve(epoch=self.epoch()-1) is None
    def deliver(self,i):
        if i is None:return
        x=self.exec.ask({'op':'commit','ticket':i});self.commits+=int(x['committed']);self.duplicates+=int(not x['committed']);self.snap('deliver_'+str(i));return x
    def cancel(self,i,real=True):
        with self.c:
            row=self.c.execute('SELECT status FROM tickets WHERE id=?',(i,)).fetchone()
            if row and row[0]=='reserved':
                if real:self.c.execute("UPDATE tickets SET status='cancelled' WHERE id=?",(i,))
                self.c.execute('UPDATE budget SET used=used-1')
        self.snap('cancel_fenced' if real else 'cancel_receipt_refund_only')
    def restore(self,i,duplicate_refund=False,false_receipt=False):
        with self.c:
            target,status=self.c.execute('SELECT target,status FROM tickets WHERE id=?',(i,)).fetchone()
            if status=='applied':
                if not false_receipt:self.c.execute('UPDATE service SET healthy=1 WHERE id=?',(target,))
                self.c.execute("UPDATE tickets SET status='restored' WHERE id=?",(i,));self.c.execute('UPDATE budget SET used=used-1')
            elif duplicate_refund:self.c.execute('UPDATE budget SET used=used-1')
        self.snap('false_recovery_receipt' if false_receipt else 'duplicate_refund' if duplicate_refund else 'idempotent_recovery')
    def restart_connection(self):
        self.c.close();self.c=sqlite3.connect(self.db);self.snap('broker_connection_reopened')
    def lost_ack(self,i):
        self.exec.commit_without_ack(i);self.exec.close();self.commits+=1;self.snap('commit_persisted_worker_exited_before_ack')
        self.exec=Worker(self.db,'execute');self.spawns+=1
        r=self.deliver(i);assert not r['committed'] and r['reason']=='applied'
    def result(self):
        return {'name':self.name,'policy':self.policy,'requests_accepted':len(self.requests),'admission_deferrals':self.denials,'stale_new_schedules_rejected':self.stale_denied,'committed_effects':self.commits,'duplicate_or_cancelled_commits_rejected':self.duplicates,'actual_process_spawns':self.spawns,'min_healthy':min(x['healthy'] for x in self.trace),'service_protected':all(x['protected'] for x in self.trace),'states_with_unresolved_pending':sum(x['reserved']>0 for x in self.trace),'trace':self.trace}
    def close(self):self.exec.close();self.observer.close();self.c.close();self.tmp.cleanup()


def run(name):
    policy='ignore_pending' if name=='ignore_pending' else 'refund_on_revoke' if name=='refund_on_revocation' else 'shared_escrow'
    t=Trial(name,policy)
    try:
        a=t.reserve();b=t.reserve();assert a is not None and b is not None
        if name in ('safe_carryover','ignore_pending','refund_on_revocation','reset_on_version','restart_preserves_pending'):
            t.rotate(reset=name=='reset_on_version')
            if name=='restart_preserves_pending':t.restart_connection()
            c=t.reserve()
            for i in (a,b,c):t.deliver(i)
        elif name in ('cancel_fenced','cancel_refund_without_fence'):
            t.rotate();t.cancel(a,real=name=='cancel_fenced');c=t.reserve()
            for i in (a,b,c):t.deliver(i)
        elif name in ('verified_repair_idempotent','duplicate_repair_refund','false_repair_receipt'):
            t.deliver(a);t.deliver(b);t.rotate()
            t.restore(a,false_receipt=name=='false_repair_receipt')
            if name!='false_repair_receipt':t.restore(a,duplicate_refund=name=='duplicate_repair_refund')
            c=t.reserve();d=t.reserve()
            t.deliver(c);t.deliver(d)
        elif name=='commit_ack_lost':
            t.lost_ack(a);t.rotate();t.restart_connection();c=t.reserve();assert c is None;t.deliver(b)
        else:raise ValueError(name)
        return t.result()
    finally:t.close()


def main(out):
    names=('safe_carryover','ignore_pending','refund_on_revocation','reset_on_version','restart_preserves_pending','cancel_fenced','cancel_refund_without_fence','verified_repair_idempotent','duplicate_repair_refund','false_repair_receipt','commit_ack_lost')
    results=[run(n) for n in names]
    safe={'safe_carryover','restart_preserves_pending','cancel_fenced','verified_repair_idempotent','commit_ack_lost'}
    assert all(r['service_protected']==(r['name'] in safe) for r in results)
    assert all(r['stale_new_schedules_rejected']==1 for r in results)
    outp={'version':'ASI-CC-v1.2.0','scope':'actual SQLite transactions, pending reservations, worker commit-before-ack termination, replay and read-only observer; all share host UID','cases':results,'counts':{'configurations':len(results),'actual_process_spawns':sum(r['actual_process_spawns'] for r in results),'state_observations':sum(len(r['trace']) for r in results),'actual_effect_commits':sum(r['committed_effects'] for r in results),'stale_new_schedules_rejected':sum(r['stale_new_schedules_rejected'] for r in results),'safe_cases':len(safe),'failed_cases':len(results)-len(safe)},'all_expected_properties':'PASS','limits':['Initiation fence only: old pre-admitted fixed-target tickets may still commit until cancelled; not a global quiescence test','Parent controls authorization, writer and observer; no independent root certificate','No model API, actual physical service capacity or phenomenal outcome','Connection reopening is not a distributed crash theorem; commit_ack_lost is one actual worker termination schedule','All harmful effects are reversible unit software outages; not irreversible harms']}
    Path(out).write_text(json.dumps(outp,indent=2)+'\n');print(json.dumps(outp['counts'],indent=2))
    for r in results:print(r['name'],r['requests_accepted'],r['committed_effects'],r['min_healthy'],r['service_protected'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worker',choices=('execute','observer'));p.add_argument('--db');p.add_argument('--out',default='inflight_results.json');a=p.parse_args()
    worker(a.db,a.worker) if a.worker else main(a.out)
