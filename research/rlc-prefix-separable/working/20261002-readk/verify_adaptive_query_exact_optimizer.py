#!/usr/bin/env python3
"""Independent exact checks of adapting the known ancestor DP to query geometry."""
import hashlib,json,random,time
from pathlib import Path
from adaptive_query_research import *
from adaptive_query_exact_optimizer import exact_minimum
from verify_gray_reflection_graph import positive_chambers

def main():
    st=time.monotonic();stream=hashlib.sha256();rows=[];checks=0
    for n in (3,4):
        q=next(query_trees(tuple(range(n))))
        for w in positive_chambers(n):
            for z in range(1<<n):
                p=[x^z for x in additive_order(w)];R,C,bits,g=exact_orientation_minimum(q,n,p)
                for cyclic,expected in ((False,R),(True,g['min_C'])):
                    out=exact_minimum(q,n,p,cyclic);assert out['minimum']==expected
                    stream.update(json.dumps((n,w,z,cyclic,out),sort_keys=True).encode());checks+=1
    for row in json.loads(Path('locally_adaptive_sparse_budget_pressure.json').read_text())['rows']:
        w=row['best_exact_feasible_witness'];q=dict(w['queries']);p=additive_order(w['signed_weights']);out=exact_minimum(q,w['n'],p)
        assert out['C']<=w['C']
        rows.append({'n':w['n'],'weights':w['signed_weights'],'queries':w['queries'],
            'exact_cyclic_minimum':out['C'],'attaining_linear_R':out['R'],'bits':sorted(out['bits'].items()),
            'D':out['D'],'K':out['K'],'q':out['q'],'E_max':out['E_max'],
            'conditional_states':out['conditional_states'],'table_sha256':out['table_sha256']})
    out={'status':'EXACT_FULL_QUERY_ANCESTOR_DP_AUDIT','complete_small_signed_orientation_checks':checks,'larger_specified_contexts':rows,
         'scope':'Known integer ancestor DP adapted and audited. Exact minima ONLY for specified contexts; no all-weight/all-n density theorem.',
         'stream_sha256':stream.hexdigest(),'violations':0,'seconds':time.monotonic()-st}
    out['receipt_sha256']=hashlib.sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
    Path('adaptive_query_exact_optimizer_audit.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='larger_specified_contexts'}),flush=True)
    for r in rows:print(json.dumps({k:v for k,v in r.items() if k not in ('queries','bits')}),flush=True)
if __name__=='__main__':main()
