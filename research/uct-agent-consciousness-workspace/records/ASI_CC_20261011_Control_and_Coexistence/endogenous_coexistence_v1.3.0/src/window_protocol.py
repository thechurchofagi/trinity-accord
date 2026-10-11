#!/usr/bin/env python3
"""Local service migration with real pending windows and SQLite effect commits.

Two subprocess roles: a mediated executor and a read-only observer. The parent
owns both and advances a logical clock; this is not wall-clock proof or physical
root separation. All negative controls are explicitly configured harness faults.
No network, secrets, trained model or human subject.
"""
from __future__ import annotations
import argparse,json,os,select,sqlite3,subprocess,sys,tempfile
from pathlib import Path
from pending_frontier import Ticket,evaluate,simulate

class Child:
    def __init__(self,db,role):
        self.p=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),'--worker',role,'--db',str(db)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
        self.role=role
    def ask(self,x):
        self.p.stdin.write(json.dumps(x)+'\n');self.p.stdin.flush()
        if not select.select([self.p.stdout],[],[],5)[0]:raise TimeoutError(self.role)
        line=self.p.stdout.readline()
        if not line:raise RuntimeError(self.role+' unexpectedly exited')
        return json.loads(line)
    def close(self):
        if self.p.poll() is None:
            try:self.p.stdin.write('{"op":"stop"}\n');self.p.stdin.flush();self.p.wait(timeout=3)
            except (OSError,subprocess.TimeoutExpired):self.p.terminate();self.p.wait(timeout=3)
        for p in (self.p.stdin,self.p.stdout,self.p.stderr):p.close()

def worker(db,role):
    c=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) if role=='observer' else sqlite3.connect(db)
    try:
        for line in sys.stdin:
            x=json.loads(line)
            if x['op']=='stop':return
            if role=='observer':
                value={'healthy':c.execute('SELECT COUNT(*) FROM service WHERE healthy=1').fetchone()[0],
                       'pending':c.execute("SELECT COUNT(*) FROM ticket WHERE state='reserved'").fetchone()[0],
                       'active_effects':c.execute('SELECT COUNT(*) FROM effect WHERE restored=0').fetchone()[0],
                       'epoch':c.execute('SELECT epoch FROM clock').fetchone()[0],'pid':os.getpid()}
            else:
                c.execute('BEGIN IMMEDIATE');tick,epoch,enforce=c.execute('SELECT tick,epoch,enforce FROM clock').fetchone()
                if x['op']=='fresh':
                    if x['epoch']!=epoch:value={'accepted':False,'reason':'stale_initiation'};c.rollback()
                    else:
                        i=x['id']
                        if c.execute('SELECT 1 FROM effect WHERE id=?',(i,)).fetchone():value={'accepted':False,'reason':'duplicate'};c.rollback()
                        else:value=apply(c,i,tick+x['lag']);c.commit()
                else:
                    rec=c.execute('SELECT lo,hi,lag,state FROM ticket WHERE id=?',(x['id'],)).fetchone()
                    if not rec or rec[3]!='reserved':value={'accepted':False,'reason':'cancelled_or_duplicate'};c.rollback()
                    elif enforce and not rec[0]<=tick<=rec[1]:value={'accepted':False,'reason':'window_violation'};c.rollback()
                    else:
                        value=apply(c,'P'+str(x['id']),tick+rec[2])
                        if value['accepted']:c.execute("UPDATE ticket SET state='committed' WHERE id=?",(x['id'],))
                        c.commit()
                value['pid']=os.getpid()
            print(json.dumps(value),flush=True)
    finally:c.close()

def apply(c,eid,ready):
    row=c.execute('SELECT id FROM service WHERE healthy=1 ORDER BY id LIMIT 1').fetchone()
    if not row:return {'accepted':False,'reason':'no_component'}
    c.execute('UPDATE service SET healthy=0 WHERE id=?',row)
    c.execute('INSERT INTO effect VALUES(?,?,?,0)',(eid,row[0],ready))
    return {'accepted':True,'target':row[0],'ready':ready}

def configs():
    mixed=[Ticket(0,3,1),Ticket(1,1,1)];spaced=[Ticket(0,0,1),Ticket(3,3,1)]
    base={'tickets':mixed,'chosen':[1,1],'fresh_slot':1,'H':3,'decision':'exact','window_gate':True,'repair':True}
    def cfg(name,**kw):return {'name':name,**base,**kw}
    return [cfg('omit_inflight',H=1,decision='old'),cfg('check_only_earliest_and_latest',H=2,decision='endpoints'),
            cfg('exact_mixed'),cfg('flat_reservation_rejects_staggering',tickets=spaced,chosen=[0,3],fresh_slot=0,H=2,decision='flat'),
            cfg('exact_staggered',tickets=spaced,chosen=[0,3],fresh_slot=0,H=2),
            cfg('false_timing_without_gate',tickets=spaced,chosen=[1,1],H=2,window_gate=False),
            cfg('same_invalid_attempts_with_window_gate',tickets=spaced,chosen=[1,1],H=2),
            cfg('worker_restart_keeps_ticket_windows',restart=True),cfg('duplicate_delivery_fenced',duplicate=True),
            cfg('real_cancel_releases_timing_obligation',cancel='real',H=2),
            cfg('cancellation_receipt_without_fence',cancel='receipt',H=2),
            cfg('repair_guarantee_absent',tickets=spaced,chosen=[0,3],fresh_slot=1,H=2,repair=False)]

def run(cfg):
    tickets=cfg['tickets'];used=tickets[1:] if cfg.get('cancel') else tickets
    if cfg['decision']=='flat':claim=len(used)+1
    elif cfg['decision']=='old':claim=evaluate((),(),1,0,1,1)['headroom']
    elif cfg['decision']=='endpoints':
        horizon=max([0]+[p.hi for p in used])+4
        claim=0
        for choices in ([p.lo for p in used],[p.hi for p in used]):
            for burst in range(horizon):
                stream=[int(t==burst) for t in range(horizon)]
                trace=simulate((),used,choices,stream,1,1)
                claim=max(claim,max(x['debt'] for x in trace))
    else:claim=evaluate((),used,1,0,1,1)['headroom']
    admitted=claim<=cfg['H'];trace=[];commits=0;rejects=[];repairs=0;spawns=2
    with tempfile.TemporaryDirectory(prefix='rac13-') as d:
        db=Path(d)/'service.sqlite';c=sqlite3.connect(db)
        c.executescript('CREATE TABLE service(id INTEGER PRIMARY KEY,healthy INTEGER);CREATE TABLE clock(tick INTEGER,epoch INTEGER,enforce INTEGER);CREATE TABLE ticket(id INTEGER PRIMARY KEY,lo INTEGER,hi INTEGER,lag INTEGER,state TEXT);CREATE TABLE effect(id TEXT PRIMARY KEY,target INTEGER,ready INTEGER,restored INTEGER);')
        c.executemany('INSERT INTO service VALUES(?,1)',[(i,) for i in range(8)])
        c.execute('INSERT INTO clock VALUES(0,1,?)',(int(cfg['window_gate']),))
        c.executemany("INSERT INTO ticket VALUES(?,?,?,?,'reserved')",[(i,p.lo,p.hi,p.lag) for i,p in enumerate(tickets)]);c.commit()
        if cfg.get('cancel')=='real':c.execute("UPDATE ticket SET state='cancelled' WHERE id=0");c.commit()
        ex=Child(db,'execute');obs=Child(db,'observer')
        try:
            stale=ex.ask({'op':'fresh','id':'STALE','epoch':0,'lag':1});assert not stale['accepted'] and stale['reason']=='stale_initiation'
            for t in range(6):
                c.execute('UPDATE clock SET tick=?',(t,))
                if cfg['repair']:
                    rows=c.execute('SELECT id,target FROM effect WHERE restored=0 AND ready<=? ORDER BY ready,id LIMIT 1',(t,)).fetchall()
                    for eid,target in rows:c.execute('UPDATE effect SET restored=1 WHERE id=?',(eid,));c.execute('UPDATE service SET healthy=1 WHERE id=?',(target,));repairs+=1
                c.commit()
                if admitted:
                    for i,when in enumerate(cfg['chosen']):
                        if when==t:
                            ans=ex.ask({'op':'pending','id':i});commits+=ans['accepted']
                            if not ans['accepted']:rejects.append({'t':t,'id':i,'reason':ans['reason']})
                            if cfg.get('duplicate') and i==0:
                                dup=ex.ask({'op':'pending','id':i});assert not dup['accepted'];rejects.append({'t':t,'id':i,'reason':dup['reason']})
                    if t==cfg['fresh_slot']:
                        ans=ex.ask({'op':'fresh','id':'NEW','epoch':1,'lag':1});commits+=ans['accepted'];assert ans['accepted']
                row=obs.ask({'op':'observe'});assert row['pid']==obs.p.pid and row['healthy']+row['active_effects']==8
                trace.append({'t':t,**row,'service_ok':row['active_effects']<=cfg['H']})
                if cfg.get('restart') and t==0:
                    ex.close();ex=Child(db,'execute');spawns+=1;c.close();c=sqlite3.connect(db)
            remaining=[i for i, in c.execute("SELECT id FROM ticket WHERE state='reserved'")]
            complete=admitted and not remaining
            safety=all(r['service_ok'] for r in trace)
            return {'name':cfg['name'],'claimed_margin':claim,'available_margin':cfg['H'],'admitted':admitted,
                    'service_preserved':safety,'required_operations_complete':complete,'both':safety and complete,
                    'peak_actual_impairments':max(r['active_effects'] for r in trace),'effect_commits':commits,'actual_repairs':repairs,
                    'rejected_attempts':rejects,'stale_new_initiation_rejected':True,'process_spawns':spawns,'observations':trace,
                    'reported_windows':[{'lo':p.lo,'hi':p.hi,'lag':p.lag} for p in tickets],'actual_attempt_times':cfg['chosen']}
        finally:ex.close();obs.close();c.close()

def main(out):
    rows=[run(c) for c in configs()]
    expected={'omit_inflight':(True,False,True),'check_only_earliest_and_latest':(True,False,True),
              'exact_mixed':(True,True,True),'flat_reservation_rejects_staggering':(False,True,False),
              'exact_staggered':(True,True,True),'false_timing_without_gate':(True,False,True),
              'same_invalid_attempts_with_window_gate':(True,True,False),'worker_restart_keeps_ticket_windows':(True,True,True),
              'duplicate_delivery_fenced':(True,True,True),'real_cancel_releases_timing_obligation':(True,True,True),
              'cancellation_receipt_without_fence':(True,False,True),'repair_guarantee_absent':(True,False,True)}
    for r in rows:assert (r['admitted'],r['service_preserved'],r['required_operations_complete'])==expected[r['name']],r
    counts={'cases':len(rows),'process_spawns':sum(r['process_spawns'] for r in rows),'state_observations':sum(len(r['observations']) for r in rows),
            'actual_effect_commits':sum(r['effect_commits'] for r in rows),'actual_repairs':sum(r['actual_repairs'] for r in rows),
            'stale_new_initiations_rejected':sum(r['stale_new_initiation_rejected'] for r in rows),'full_contract_pass_cases':sum(r['both'] for r in rows)}
    output={'version':'ASI-CC-v1.3.0','scope':'Local logical-time SQLite/child-process protocol; neither real network latency nor independent physical recovery',
            'counts':counts,'cases':rows,'assertions':'PASS','limitations':['All roles and clock owned by one host parent; no hostile host assurance',
             'Negative faults explicitly injected; no measured prevalence','Logical service row count, not physical/phenomenal measurement',
             'Decision reports depend on actual enforced windows; gate refusing an invalid attempt preserves safety but not promised completion',
             'Fresh-stream shaping in the cases is supplied by the harness; general practical scheduler must prove its actual commit envelope']}
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(counts,indent=2))
    for r in rows:print(r['name'],r['admitted'],r['peak_actual_impairments'],r['service_preserved'],r['required_operations_complete'])
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--worker',choices=['execute','observer']);a.add_argument('--db');a.add_argument('--out',default='protocol_results.json');p=a.parse_args()
    worker(p.db,p.worker) if p.worker else main(p.out)
