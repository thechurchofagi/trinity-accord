#!/usr/bin/env python3
"""Reproduce retained LP candidates from the completed actual-wall search."""
from pathlib import Path
import gzip,json
from verify_paired_odd_k5_obstruction import exact_joint_lp

def main():
    here=Path(__file__).parent
    wall=json.loads(gzip.decompress((here/'paired_odd_k5_actual_wall_pressure.json.gz').read_bytes()))
    seed=wall['actual_exactness_gaps'][1]
    assert seed['weights']==[10480038,3358564,4427690,18199924,7393112,7711178,15108776,968084,2436896,16335859]
    raw=(json.dumps(seed,indent=2)+'\n').encode()
    (here/'paired_actual_joint_gap_seed_certificate.json.gz').write_bytes(gzip.compress(raw,mtime=0))
    limit=[(u,v,c-int((u,v)==(508,511))) for u,v,c in seed['half_edges']]
    joint=exact_joint_lp(limit,seed['all_objects'])
    assert joint['value']==[28,1]
    (here/'paired_actual_joint_gap_limit_certificate.json').write_text(json.dumps({'edges':limit,'joint':joint},indent=2)+'\n')
    print(json.dumps({'status':'EXACT_RATIONAL_CANDIDATES_PREPARED','seed_packing':seed['packing_value'],'limit_packing':joint['value']}))

if __name__=='__main__':main()
