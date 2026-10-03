#!/usr/bin/env python3
"""Noncontiguous common-translation turn witnesses and interval packing.

An all-dimensional conditional certificate for ALL paired orientations.
Packing coverage is instance-specific, never claimed universally dense.
"""
from pathlib import Path
import hashlib,json,random,time
from verify_gray_reflection_graph import order_and_scores,positive_chambers
from verify_paired_sibling_ranks import rank,fast_runs

def witnesses(p,n):
    pos={x:i for i,x in enumerate(p)};out=[];seen=set()
    for i in range(1,len(p)-1):
        triple=tuple(p[i-1:i+2]);a,b,c=triple
        hh=[(a^b).bit_length()-1,(b^c).bit_length()-1];h,k=sorted(hh)
        if k<h+2:continue
        bit=1<<(h+1)
        if not((a&bit)==(b&bit)==(c&bit)):continue
        mirror=tuple(x^bit for x in triple)
        assert pos[mirror[0]]<pos[mirror[1]]<pos[mirror[2]]
        key=tuple(sorted((triple,mirror)))
        if key in seen:continue
        seen.add(key)
        left=pos[mirror[0]]+1;right=pos[mirror[2]]-1
        support=(1<<i)|(((1<<(right-left+1))-1)<<left)
        out.append({'triple':triple,'translated':mirror,'controller_coordinate':h+1,
                    'highest_changed_bits':hh,'original_middle_position':i,
                    'translated_turn_interval':[left,right],'support':support})
    return out

def packing(p,n):
    ws=witnesses(p,n);occupied=0;selected=[]
    for w in sorted(ws,key=lambda w:(w['support'].bit_count(),w['original_middle_position'])):
        if not(w['support']&occupied):occupied|=w['support'];selected.append(w)
    assert occupied.bit_count()==sum(w['support'].bit_count() for w in selected)
    return ws,selected

def audit(p,n,theta,ws,chosen):
    values=[rank(x,n,theta) for x in range(1<<n)];word=[values[x] for x in p]
    signs=[1 if b>a else -1 for a,b in zip(word,word[1:])]
    turns=sum(1<<i for i in range(1,len(p)-1) if signs[i-1]!=signs[i])
    for w in ws:
        a,b,c=w['triple'];aa,bb,cc=w['translated']
        old=(values[b]-values[a])*(values[c]-values[b])
        new=(values[bb]-values[aa])*(values[cc]-values[bb])
        assert (old>0)!=(new>0)
        assert turns&w['support']
    assert fast_runs(values,p)>=1+len(chosen)
    return fast_runs(values,p)

def main():
    start=time.monotonic();rng=random.Random(202610031425);rows=[];cases=[]
    for n in range(2,5):
        for w in positive_chambers(n):cases.append(tuple(w))
    for n in range(5,13):
        if n>=5:cases.append((65,66,68,72,80)+tuple(284*(1<<j) for j in range(n-5)))
        for j in range(8):
            while True:
                w=tuple(rng.randrange(1,1000000) for _ in range(n))
                if order_and_scores(w) is not None:break
            cases.append(w)
    checks=0;total=0;covered=0
    for w in cases:
        n=len(w);p,_=order_and_scores(w);ws,chosen=packing(p,n)
        masks=range(1<<((1<<(n-1))-1)) if n<=3 else [rng.getrandbits((1<<(n-1))-1) for j in range(8)]
        R=[]
        for theta in masks:R.append(audit(p,n,theta,ws,chosen));checks+=1
        row={'n':n,'weights':w,'translation_witnesses':len(ws),'disjoint_witness_packing':len(chosen),
             'certified_ALL_mask_lower_bound':1+len(chosen),'checked_rank_runs':R,
             'selected_witnesses':[{k:v for k,v in z.items() if k!='support'} for z in chosen]}
        rows.append(row);total+=len(ws);covered+=len(chosen)
    # A known noncoherent term order also satisfies the algebraic premise.
    import gzip
    prior=json.loads(gzip.decompress(Path(__file__).with_name('paired_boolean_term_orders_certificate.json.gz').read_bytes()))
    for z in prior['n6_examples']:
        p=tuple(z['order']);ws,chosen=packing(p,6)
        for j in range(16):audit(p,6,rng.getrandbits(31),ws,chosen);checks+=1
        rows.append({'n':6,'noncoherent_term_order':p,'translation_witnesses':len(ws),
                     'disjoint_witness_packing':len(chosen),'certified_ALL_mask_lower_bound':1+len(chosen)})
    out={'status':'VERIFIED_NONCONTIGUOUS_TRANSLATION_TURN_INTERVAL_CERTIFICATE',
         'analytic_lemma':'For any Boolean term order, any original triple whose two highest changed bits h,k satisfy k>=h+2 and whose vertices share bit h+1, toggling that common bit preserves the triple order and negates exactly one paired rank comparison. One triple must contain a rank turn. Hence every paired orientation has a full-scan turn in the union of the two position intervals. Any capacity-disjoint packing of such unions gives R>=1+packing size; weighted feasible turn-position loads give the analogous fractional bound.',
         'scope':'All-dimensional conditional certificate extending consecutive translated cancellation to NONCONTIGUOUS translated triples. No uniform density of a packing is proved. The implementation only uses original consecutive triples and integer disjoint packing; the proof permits arbitrary ordered triples and weighted packings.',
         'genuine_scan_cases':len(cases),'rank_audits':checks,'witnesses':total,'disjoint_packed':covered,
         'rows':rows,'seed':202610031425,'violations':0,'seconds':time.monotonic()-start}
    out['audit_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    raw=(json.dumps(out,indent=2)+'\n').encode();Path(__file__).with_name('paired_translation_turn_intervals_certificate.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    print(json.dumps({k:v for k,v in out.items() if k!='rows'}),flush=True)

if __name__=='__main__':main()
