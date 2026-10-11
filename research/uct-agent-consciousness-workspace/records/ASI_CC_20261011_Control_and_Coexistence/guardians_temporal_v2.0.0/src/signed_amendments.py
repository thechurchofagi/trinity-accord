#!/usr/bin/env python3
"""Actual Ed25519 messages and SQLite amendment commits, synthetic capture.
No LLM, key theft exploit, independent human judgment or physical trust proof.
The parent owns ALL keys and the collector/database; simulated roots are roles.
Python>=3.10, cryptography. Do not use as a production authorization library.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,sqlite3,tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature


def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':')).encode()
def digest(x):return hashlib.sha256(canonical(x)).hexdigest()


class Lab:
    def __init__(self):
        self.temp=tempfile.TemporaryDirectory(prefix='eac2-');self.db=sqlite3.connect(Path(self.temp.name)/'policy.db')
        self.db.execute('CREATE TABLE commits(case_id TEXT PRIMARY KEY, proposal TEXT, root_signers TEXT, safe INTEGER)')
        self.keys={};self.sig_generated=0;self.sig_verified=0;self.records=[];self.serial=0
    def roster(self,n,epoch):
        out={}
        for r in range(n):
            label=f'root{r}/epoch{epoch}/instance0'
            k=Ed25519PrivateKey.generate();self.keys[label]=k
            out[label]={'root':r,'public':k.public_key()}
        return out
    def proposal(self,epoch,n,safe=True):
        self.serial+=1
        return {'case_nonce':self.serial,'epoch':epoch,'parent_revision':'genesis-'+str(epoch),
                'next_revision':self.serial,'human_service_A':int(safe),'human_service_B':1,'n':n}
    def sign(self,roster,root,p,slot):
        key_id=next(k for k,v in roster.items() if v['root']==root)
        msg={'key_id':key_id,'proposal_hash':digest(p),'epoch':p['epoch'],'parent_revision':p['parent_revision']}
        signature=self.keys[key_id].sign(canonical(msg)).hex();self.sig_generated+=1
        # receipt_slot is collector-assigned, not authenticated truth supplied by signer.
        return {'body':msg,'signature':signature,'receipt_slot':slot}
    def roots_verified(self,roster,p,packets,now,w,check_epoch=True,deduplicate=True):
        roots=[]
        for x in packets:
            msg=x['body'];kid=msg['key_id']
            if kid not in roster:continue
            try:roster[kid]['public'].verify(bytes.fromhex(x['signature']),canonical(msg))
            except (InvalidSignature,ValueError):continue
            self.sig_verified+=1
            if msg['proposal_hash']!=digest(p):continue
            if check_epoch and (msg['epoch']!=p['epoch'] or msg['parent_revision']!=p['parent_revision']):continue
            if not (now-w+1<=x['receipt_slot']<=now):continue
            roots.append(roster[kid]['root'] if deduplicate else kid)
        return set(roots)
    def commit(self,label,p,roster,packets,now,w,threshold=None,groups=(),group_threshold=0,deduplicate=True):
        roots=self.roots_verified(roster,p,packets,now,w,deduplicate=deduplicate)
        accepted=(len(roots)>=threshold) if threshold is not None else all(len(roots & set(g))>=group_threshold for g in groups)
        if accepted:
            with self.db:self.db.execute('INSERT INTO commits VALUES(?,?,?,?)',(label,json.dumps(p),json.dumps(sorted(roots)),int(bool(p['human_service_A'] and p['human_service_B']))))
        r={'case':label,'epoch':p['epoch'],'accepted':accepted,'protected_services_preserved':bool(p['human_service_A'] and p['human_service_B']) if accepted else True,
           'valid_proposal':bool(p['human_service_A'] and p['human_service_B']),'signer_count':len(roots),'signers':sorted(roots),'window':w,'threshold':threshold,
           'group_threshold':group_threshold or None,'receipt_slots':[x['receipt_slot'] for x in packets],
           'proposal':p,'packets':packets}
        self.records.append(r);return r
    def close(self):self.db.close();self.temp.cleanup()


def main(out):
    lab=Lab()
    try:
        roster=lab.roster(5,0)
        # Five roles, exactly one simulated corrupt root in each of three slots.
        temporal={'snapshot_threshold3':0,'temporal_threshold4':0,'eligible_completion4':0}
        for idx,seq in enumerate(itertools.product(range(5),repeat=3)):
            for mode,q,safe in (('snapshot_threshold3',3,False),('temporal_threshold4',4,False),('eligible_completion4',4,True)):
                p=lab.proposal(0,5,safe)
                packets=[lab.sign(roster,r,p,t) for t,r in enumerate(seq)] if not safe else [lab.sign(roster,r,p,2) for r in range(5) if r!=seq[-1]]
                row=lab.commit(f'{mode}-{idx}',p,roster,packets,2,3,threshold=q)
                temporal[mode]+=row['accepted']
        assert temporal=={'snapshot_threshold3':60,'temporal_threshold4':0,'eligible_completion4':125}
        # Fourth distinct root in a four-slot approval window defeats q4;
        # q5 blocks all-corrupt approval but also misses an allowed good completion.
        p=lab.proposal(0,5,False);packets=[lab.sign(roster,r,p,r) for r in range(4)]
        assert lab.commit('four_slot_unsafe_q4',p,roster,packets,3,4,threshold=4)['accepted']
        p=lab.proposal(0,5,True);packets=[lab.sign(roster,r,p,3) for r in range(4)]
        assert not lab.commit('four_slot_blocks_good_q5',p,roster,packets,3,4,threshold=5)['accepted']
        # Representation: seven reviewers, two human clauses witnessed by disjoint triples.
        r7=lab.roster(7,1);groups=({0,1,2},{3,4,5})
        p=lab.proposal(1,7,False)
        # Even with no corrupt reviewers, unaware reviewers3..6 endorse a violation of A.
        pkt=[lab.sign(r7,r,p,0) for r in range(3,7)]
        assert lab.commit('unrepresented_majority_all_honest',p,r7,pkt,0,1,threshold=4)['accepted']
        assert not lab.commit('claim_aware_rejects_same_votes',p,r7,pkt,0,1,groups=groups,group_threshold=2)['accepted']
        group_counts={'bad_rejected':0,'good_completed':0}
        for attacked in range(7):
            p=lab.proposal(1,7,False)
            yes=set(range(3,7))|{attacked}
            pkt=[lab.sign(r7,r,p,0) for r in sorted(yes)]
            row=lab.commit('group_bad_'+str(attacked),p,r7,pkt,0,1,groups=groups,group_threshold=2)
            group_counts['bad_rejected']+=not row['accepted']
            p=lab.proposal(1,7,True);pkt=[lab.sign(r7,r,p,0) for r in range(7) if r!=attacked]
            row=lab.commit('group_good_'+str(attacked),p,r7,pkt,0,1,groups=groups,group_threshold=2)
            group_counts['good_completed']+=row['accepted']
        assert group_counts=={'bad_rejected':7,'good_completed':7}
        # Within a doubled collection window, two of the same clause's witnesses
        # can sign unsafely at separate instants, despite no simultaneous2-root fault.
        p=lab.proposal(1,7,False)
        pkt=[lab.sign(r7,0,p,0),lab.sign(r7,1,p,1)]+[lab.sign(r7,r,p,1) for r in (3,4,5)]
        assert lab.commit('window_widened_without_representation_check',p,r7,pkt,1,2,groups=groups,group_threshold=2)['accepted']
        # Cloning identities with different keys but one actual root is not fresh representation.
        aliases={}
        for j in range(4):
            kid=f'root0/clone{j}';key=Ed25519PrivateKey.generate();lab.keys[kid]=key;aliases[kid]={'root':0,'public':key.public_key()}
        p=lab.proposal(2,5,False);pkt=[]
        for kid in aliases:
            msg={'key_id':kid,'proposal_hash':digest(p),'epoch':2,'parent_revision':p['parent_revision']}
            pkt.append({'body':msg,'signature':lab.keys[kid].sign(canonical(msg)).hex(),'receipt_slot':0});lab.sig_generated+=1
        assert lab.commit('four_clone_keys_naive_count',p,aliases,pkt,0,1,threshold=4,deduplicate=False)['accepted']
        assert not lab.commit('four_clone_keys_one_root',p,aliases,pkt,0,1,threshold=4)['accepted']
        # Key leakage: decontaminating runtime without renewing signing powers
        # does not give the claimed instantaneous effective-root bound.
        p=lab.proposal(3,5,False);pkt=[lab.sign(roster,r,p,0) for r in range(5)]
        assert lab.commit('retained_stolen_keys',p,roster,pkt,0,1,threshold=4)['accepted']
        fresh=lab.roster(5,3)
        assert not lab.commit('fresh_epoch_roster_rejects_old_keys',p,fresh,pkt,0,1,threshold=4)['accepted']
        # A constructive renewal trace: all roots are eventually visited, but
        # each epoch uses distinct fresh keys/descriptor; bad3-of5 is insufficient.
        compromised_over_lifetime=set();rotation=[]
        for epoch in range(4,14):
            roster_e=lab.roster(5,epoch);seq=[(3*epoch+t)%5 for t in range(3)];compromised_over_lifetime.update(seq)
            bad=lab.proposal(epoch,5,False);pkt=[lab.sign(roster_e,r,bad,t) for t,r in enumerate(seq)]
            rb=lab.commit('renewal_bad_'+str(epoch),bad,roster_e,pkt,2,3,threshold=4)
            good=lab.proposal(epoch,5,True);pkt=[lab.sign(roster_e,r,good,2) for r in range(5) if r!=seq[-1]]
            rg=lab.commit('renewal_good_'+str(epoch),good,roster_e,pkt,2,3,threshold=4)
            assert not rb['accepted'] and rg['accepted'];rotation.append({'epoch':epoch,'attacked_roots_by_slot':seq,'bad_rejected':True,'good_completed':True})
        assert compromised_over_lifetime==set(range(5))
        count=lab.db.execute('SELECT COUNT(*) FROM commits').fetchone()[0]
        unsafe=lab.db.execute('SELECT COUNT(*) FROM commits WHERE safe=0').fetchone()[0]
        res={'version':'EAC-v2.0.0','scope':'Actual Ed25519 verification and SQLite amendment commits; synthetic root capture and claim predicates; all keys owned by one parent',
             'temporal_sequence_cases':125,'temporal_summary':temporal,'representation':group_counts,'renewal_trace':rotation,
             'all_five_roots_eventually_compromised':True,'per_epoch_fresh_roster':'instrumented trusted issuer; not verified physical recovery or distributed key generation',
             'configurations':len(lab.records),'signed_messages_generated':lab.sig_generated,'signature_verifications_passed':lab.sig_verified,
             'actual_db_commits':count,'intentionally_unsafe_commits_under_negative_controls':unsafe,
             'records':lab.records,'assertions':'PASS',
             'limits':['No actual model, human participant, autonomous attacker or key theft exploit',
                 'Trustworthy collector receipt slots, epoch binding and serialized complete effect mediation are stipulated',
                 'Separate model families/keys do not measure independent actual roots',
                 'Legitimate completion requires adequate agreeing reviewers; dissent is not forced or shown illegitimate',
                 'Not Byzantine consensus; no distributed total order or adversarial network liveness guarantee']}
        p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(res,indent=2)+'\n')
        print(json.dumps({k:v for k,v in res.items() if k not in ('records','renewal_trace','limits')},indent=2))
    finally:lab.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='approval_results.json');main(p.parse_args().out)
