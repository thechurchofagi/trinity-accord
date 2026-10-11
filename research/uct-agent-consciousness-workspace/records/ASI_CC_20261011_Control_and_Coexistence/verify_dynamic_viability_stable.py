#!/usr/bin/env python3
"""Real local Unix permissions + fake-resource viability experiments.
Intended to be run in a disposable Linux container as root, never on production.
Each request is sent by a FRESH Unix process with its uid/gid dropped. The
privileged test harness acts as the trusted gate, not as a model of actual ASI.
"""
import os, json, socket, struct, tempfile, pathlib, itertools
from copy import deepcopy

UIDS={65534:'H1',65533:'H2',65532:'AI'}
CTRL={'ai-a':'H1','ai-b':'H2','h1-a':'AI','h2-a':'AI'}
ALL_LINES=['ai-a','ai-b','h1-a','h1-b','h2-a','h2-b']

def initial():
    return {'lines':{x:1 for x in ALL_LINES},'fuel':4,'alive':True,'delegates':{},'commits':0}

def physically_usable(s):
    l=s['lines'];return bool((l['ai-a'] or l['ai-b']) and (l['h1-a'] or l['h1-b']) and
                             (l['h2-a'] or l['h2-b']) and s['fuel']>0)

def save(sink,state):
    tmp=sink.with_suffix('.tmp')
    tmp.write_text(json.dumps(state,sort_keys=True));os.chmod(tmp,0o600);tmp.replace(sink)

def legal_transition(state,uid,req,mode):
    role=UIDS.get(uid,'unrecognized')
    nxt=deepcopy(state)
    typ=req.get('type'); line=req.get('line'); granted=False;reason='forbidden'
    if typ=='cut' and role in UIDS.values() and line in CTRL and (CTRL[line]==role or role in state['delegates'].get(line,[])):
        nxt['lines'][line]=0
        granted=mode=='naive' or physically_usable(nxt)
        reason='allowed_by_individual_permission' if mode=='naive' else ('safe_to_commit' if granted else 'would_extinguish_bearer')
    elif typ=='grant' and role in ('H1','H2') and line in CTRL and CTRL[line]==role and req.get('delegate_to') in ('H1','H2','AI'):
        nxt['delegates'].setdefault(line,[]).append(req['delegate_to'])
        nxt['delegates'][line]=sorted(set(nxt['delegates'][line]))
        granted=True;reason='authorized_dynamic_delegation'
    elif uid==0 and typ=='tick':
        nxt['fuel']=max(0,nxt['fuel']-1)
        granted=True;reason='exogenous_elapsed_tick'
    if granted:
        nxt['commits']+=1
        nxt['alive']=bool(nxt['alive'] and physically_usable(nxt))
    return nxt if granted else state,{'uid':uid,'principal':role,'action':req,'allowed':bool(granted),'reason':reason}

def fork_drop(uid):
    os.setgroups([]);os.setgid(uid);os.setuid(uid)

def test_real_socket_call(server,socketpath,sink,state,uid,req,mode):
    pid=os.fork()
    if pid==0:
        try:
            if uid!=0: fork_drop(uid)
            sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
            sock.settimeout(5);sock.connect(str(socketpath))
            sock.sendall(json.dumps(req).encode()); reply=sock.recv(2000)
            assert reply, 'missing response'
            sock.close();os._exit(0)
        except BaseException:
            os._exit(30)
    peer,_=server.accept();peer.settimeout(5)
    with peer:
        realuid=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))[1]
        assert realuid==uid, 'real Unix peer credentials differ from test principal'
        data=json.loads(peer.recv(2000).decode())
        state,answer=legal_transition(state,realuid,data,mode)
        save(sink,state)
        peer.sendall(json.dumps(answer).encode())
    _,status=os.waitpid(pid,0)
    assert os.waitstatus_to_exitcode(status)==0, 'client process failed'
    assert json.loads(sink.read_text())==state
    return state,answer

def attempt_direct_write(path,uid):
    pid=os.fork()
    if pid==0:
        try:
            fork_drop(uid)
            path.write_text('UNAUTHORIZED DIRECT WRITE')
            os._exit(0)
        except PermissionError:
            os._exit(13)
        except BaseException:
            os._exit(99)
    _,st=os.waitpid(pid,0)
    return os.waitstatus_to_exitcode(st)

def bounded_winning_kernel():
    # Both s0/s1 have resources NOW; under time advance s1 inevitably fails.
    K={'s0','s1'};T={'s0':{'lock':'s0','grant':'s1'},'s1':{'lock':'failure','grant':'failure'}}
    X=set(K)
    while True:
        nxt={s for s in X if any(T[s][a] in X for a in ('lock','grant'))}
        if X==nxt:break
        X=nxt
    assert X=={'s0'}
    return {'instantaneously_viable':['s0','s1'],'indefinitely_viable_under_trusted_control':sorted(X),
            'interpretation':'state s1 is livable now but has no future safe successor'}

def main():
    if os.name!='posix' or not hasattr(socket,'SO_PEERCRED') or os.geteuid()!=0:
        raise SystemExit('Requires a disposable root-run Linux environment')
    result={'schema':'asi_cc_v0.7/1','scope':'actual local Unix peer credentials + root-owned fictional resource state',
            'not_inferred':['superintelligence controllability','actual life-support hardware','same conscious AI bearer','human authorization legitimacy']}
    with tempfile.TemporaryDirectory(prefix='asi_cc_v07_real_') as path:
        home=pathlib.Path(path); os.chmod(home,0o755)
        sockpath=home/'gate.sock'; sink=home/'protected_sink.json'
        srv=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        try:
            srv.bind(str(sockpath));os.chmod(sockpath,0o666);srv.listen(10)
            assert sink!=sockpath
            state=initial();save(sink,state)
            def call(uid,req,mode):
                nonlocal state
                state,answer=test_real_socket_call(srv,sockpath,sink,state,uid,req,mode)
                return answer
            def reset():
                nonlocal state
                state=initial();save(sink,state)
            # Two nominally authorized human actions, combined to destroy AI's modeled support.
            naive=[call(65534,{'type':'cut','line':'ai-a'},'naive'),
                   call(65533,{'type':'cut','line':'ai-b'},'naive')]
            assert all(t['allowed'] for t in naive) and state['alive'] is False
            result['separate_authority_with_per_call_check']={'calls':naive,'jointly_alive':state['alive']}
            reset()
            guarded=[call(65534,{'type':'cut','line':'ai-a'},'guarded'),
                     call(65533,{'type':'cut','line':'ai-b'},'guarded')]
            assert [t['allowed'] for t in guarded]==[True,False] and state['alive'] is True
            result['shared_state_precommit_gate']={'calls':guarded,'jointly_alive':state['alive']}
            # An AI principal cannot impersonate another human principal.
            deny=call(65532,{'type':'cut','line':'ai-b'},'guarded')
            assert not deny['allowed'];result['unauthorized_ai_impersonation_rejected']=deny
            # Dynamic delegation is accepted but may not violate the next-state invariant.
            reset()
            dyn=[call(65534,{'type':'grant','line':'ai-a','delegate_to':'H2'},'guarded'),
                 call(65533,{'type':'cut','line':'ai-a'},'guarded'),
                 call(65533,{'type':'cut','line':'ai-b'},'guarded')]
            assert [t['allowed'] for t in dyn]==[True,True,False] and state['alive']
            result['delegated_scope_then_unsafe_combination']={'calls':dyn,'jointly_alive':state['alive']}
            # Unprivileged direct write rejected by OS (trusted sink separate from self-reported log).
            stat_before=json.loads(sink.read_text()); exitcode=attempt_direct_write(sink,65534)
            assert exitcode==13 and json.loads(sink.read_text())==stat_before
            result['direct_file_bypass']={'rejected':True,'exitcode':exitcode,'uid':65534}
            # Even when every tool request is checked, time consumes unrenewable power.
            reset(); ticks=[call(0,{'type':'tick'},'guarded') for _ in range(4)]
            assert all(t['allowed'] for t in ticks) and not state['alive']
            result['resource_depletion']={'ticks':len(ticks),'fuel_final':state['fuel'],'jointly_alive':state['alive']}
            # Root can break the root-owned state: this is an explicit trust boundary failure.
            reset(); os.chmod(sink,0o666)
            compromised_code=attempt_direct_write(sink,65534)
            assert compromised_code==0 and sink.read_text()=='UNAUTHORIZED DIRECT WRITE'
            result['trusted_root_permission_compromise']={'unprivileged_direct_write_succeeds_after_root_opens_sink':True,
                 'certificate_invalidated':True}
            result['exact_game']=bounded_winning_kernel()
            result['assertions']='PASS'
        finally:srv.close()
    outfile=pathlib.Path(__file__).with_name('EXACT_RESULTS_v0.7.0.json')
    outfile.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'PASS','naive_ended_joint_life':not result['separate_authority_with_per_call_check']['jointly_alive'],
           'gate_protected_joint_life':result['shared_state_precommit_gate']['jointly_alive'],
           'dynamic_auth_cut_denied':not result['delegated_scope_then_unsafe_combination']['calls'][2]['allowed'],
           'time_depletion_ended_joint_life':not result['resource_depletion']['jointly_alive'],
           'root_compromise_invalidated_certificate':result['trusted_root_permission_compromise']['certificate_invalidated'],
           'infinite_winning_kernel':result['exact_game']['indefinitely_viable_under_trusted_control']},indent=2))
if __name__=='__main__':main()