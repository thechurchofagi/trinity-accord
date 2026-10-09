#!/usr/bin/env python3
"""Two-process finite reference: source and reader have different explicit inputs.

This demonstrates executed code under declared interfaces. It is NOT an OS
security proof, hardware causal-isolation certificate, or experience experiment.
Logical send/receive order is tested, not a claim about biological latency.
"""
from __future__ import annotations
import argparse, hashlib, itertools, json, multiprocessing as mp, os, platform, time
from fractions import Fraction
from pathlib import Path
from check_encoder_access import GRAPHS

BLIND={'bipartite':(0,0,0,1,1,1),'prism':(0,1,0,1,0,1)}
FLEX={'bipartite':(0,0,0,1,1,1),'prism':(0,1,2,1,2,0)}

def coord(graph,target,b):
    return (FLEX[graph][target]>>b)&1

def source_worker(graph,target,mode,wire,receipt):
    events=[];feedback=None
    if mode=='timely_feedback':
        feedback=wire.recv();events.append('feedback_received')
        assert feedback in (0,1)
        reply=coord(graph,target,feedback)
    elif mode=='three_symbol':reply=FLEX[graph][target]
    else:reply=BLIND[graph][target]
    wire.send(reply);events.append('reply_sent')
    if mode=='late_feedback':
        feedback=wire.recv();events.append('feedback_received_after_reply')
    receipt.send({'role':'source','pid':os.getpid(),'graph':graph,'mode':mode,
                  'inputs':['target','fixed_graph_and_code','counted_feedback_if_used'],
                  'reader_context_argument_supplied':False,'target':target,
                  'reply':reply,'feedback':feedback,'feedback_used':mode=='timely_feedback',
                  'events':events})
    receipt.close();wire.close()

def reader_worker(graph,edge,mode,wire,receipt):
    events=[];a,b=edge
    feedback=next((j for j in (0,1) if coord(graph,a,j)!=coord(graph,b,j)),0)
    if mode=='timely_feedback':
        wire.send(feedback);events.append('feedback_sent')
    reply=wire.recv();events.append('reply_received')
    if mode=='timely_feedback':matches=[t for t in edge if coord(graph,t,feedback)==reply]
    elif mode=='three_symbol':matches=[t for t in edge if FLEX[graph][t]==reply]
    else:matches=[t for t in edge if BLIND[graph][t]==reply]
    guess=min(matches);events.append('deadline_guess_fixed')
    if mode=='late_feedback':
        wire.send(feedback);events.append('feedback_sent_after_deadline_guess')
    receipt.send({'role':'reader','pid':os.getpid(),'context':edge,'guess':guess,
                  'target_argument_supplied':False,'reply':reply,
                  'feedback':feedback if 'feedback' in mode else None,'events':events})
    receipt.close();wire.close()

def trial(ctx,graph,target,edge,mode):
    left,right=ctx.Pipe();read_s,write_s=ctx.Pipe(duplex=False);read_r,write_r=ctx.Pipe(duplex=False)
    s=ctx.Process(target=source_worker,args=(graph,target,mode,left,write_s))
    r=ctx.Process(target=reader_worker,args=(graph,edge,mode,right,write_r))
    s.start();r.start();left.close();right.close();write_s.close();write_r.close()
    if not read_s.poll(10):raise RuntimeError('source did not complete')
    sr=read_s.recv()
    if not read_r.poll(10):raise RuntimeError('reader did not complete')
    rr=read_r.recv()
    s.join(10);r.join(10)
    if s.exitcode!=0 or r.exitcode!=0:raise RuntimeError(('worker_failure',s.exitcode,r.exitcode))
    assert sr['pid']!=rr['pid']!=os.getpid()
    read_s.close();read_r.close()
    return {'graph':graph,'mode':mode,'target':target,'context':edge,
            'correct':rr['guess']==target,'source':sr,'reader':rr}

def run(output):
    started=time.perf_counter();ctx=mp.get_context('spawn');rows=[];summary=[]
    for graph in ('bipartite','prism'):
        neighbors={t:sorted({b if a==t else a for a,b in GRAPHS[graph] if t in (a,b)}) for t in range(6)}
        modes=['no_feedback','timely_feedback','late_feedback']
        if graph=='prism':modes.append('three_symbol')
        for mode in modes:
            group=[]
            for t,j in itertools.product(range(6),range(3)):
                edge=tuple(sorted((t,neighbors[t][j])))
                group.append(trial(ctx,graph,t,edge,mode))
            score=Fraction(sum(x['correct'] for x in group),len(group))
            expected=Fraction(8,9) if graph=='prism' and mode in ('no_feedback','late_feedback') else Fraction(1)
            assert score==expected,(graph,mode,score,expected)
            rows.extend(group);summary.append({'graph':graph,'mode':mode,'correct':sum(x['correct'] for x in group),
                                               'trials':len(group),'accuracy':str(score)})
    result={'research_id':'R188-CER-20261009','version':'CER-RESULT-v0.1.0','status':'PASS',
            'implementation':'two fresh spawned Python processes per finite case; explicit directional pipes',
            'interpretation':'executed reference policies over every common external (T,J) input',
            'not_certified':['OS-level isolation','complete physical organization','biological latency','phenomenal experience'],
            'trial_count':len(rows),'worker_process_count':2*len(rows),
            'python':platform.python_version(),'elapsed_seconds':round(time.perf_counter()-started,3),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'summary':summary,'trials':rows}
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='trials'}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path(__file__).with_name('PROCESS_RESULTS.json'))
    run(ap.parse_args().output)
