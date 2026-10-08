"""Finite interpreted transducers; no modeled/observed qualia variables."""
from itertools import product, permutations
from fractions import Fraction as F
from pathlib import Path
import json
schedules={'baseline':{'B':(F(1),F(11,10),F(12,10)),'C':(F(2),F(21,10),F(22,10))},'delayed':{'B':(F(1),F(25,10),F(3)),'C':(F(2),F(21,10),F(22,10))}}
checks={};cases=[]
for cB,cC,mode,schedule in product([0,1],[0,1],['identity','compensated','uncompensated'],schedules):
 decoded={};payload={};provenance={}
 for source,c in [('B',cB),('C',cC)]:
  # Only B is transformed: permits checking prediction/feedback match changes.
  flip=source=='B' and mode!='identity'
  z=1-c if flip else c
  value=1-z if source=='B' and mode=='compensated' else z
  payload[source]=z;decoded[source]=value;provenance[source]=source
  t=schedules[schedule][source];assert t[0]<t[1]<t[2]
 cases.append({'source_features':[cB,cC],'mode':mode,'schedule':schedule,'provenance':provenance,'payload':payload,'decoded':decoded,'match':decoded['B']==decoded['C'],'B_used_before_C':schedules[schedule]['B'][2]<schedules[schedule]['C'][2]})
lookup={(tuple(x['source_features']),x['mode'],x['schedule']):x for x in cases}
checks['24_explicit_executions']=len(cases)==24
checks['all_inputs_compensated_decode']=all(x['decoded']=={'B':x['source_features'][0],'C':x['source_features'][1]} for x in cases if x['mode']=='compensated')
checks['uncompensated_same_source_changed_feature']=all(x['provenance']['B']=='B' and x['decoded']['B']!=x['source_features'][0] for x in cases if x['mode']=='uncompensated')
checks['source_cross_feature']=set((s,x['decoded'][s]) for x in cases for s in ['B','C'])==set(product(['B','C'],[0,1]))
checks['distinct_sources_equal_features']=any(x['decoded']['B']==x['decoded']['C'] and x['provenance']['B']!=x['provenance']['C'] for x in cases)
checks['retiming_preserves_selected_binding']=all(lookup[(cs,m,'baseline')]['decoded']==lookup[(cs,m,'delayed')]['decoded'] and lookup[(cs,m,'baseline')]['provenance']==lookup[(cs,m,'delayed')]['provenance'] for cs in product([0,1],repeat=2) for m in ['identity','compensated','uncompensated'])
checks['retiming_reverses_use_order']=all(lookup[(cs,m,'baseline')]['B_used_before_C'] and not lookup[(cs,m,'delayed')]['B_used_before_C'] for cs in product([0,1],repeat=2) for m in ['identity','compensated','uncompensated'])
checks['compensated_preserves_match']=all(lookup[(cs,'identity',s)]['match']==lookup[(cs,'compensated',s)]['match'] for cs in product([0,1],repeat=2) for s in schedules)
checks['uncompensated_reverses_match']=all(lookup[(cs,'identity',s)]['match']!=lookup[(cs,'uncompensated',s)]['match'] for cs in product([0,1],repeat=2) for s in schedules)
# Independent general finite-map check: every permutation of a 3-code alphabet.
checks['three_code_all_permutations']=all(all(p.index(p[c])==c for c in range(3)) for p in permutations(range(3)))
# Failure when bijectivity is dropped: constant transmission cannot recover both inputs.
checks['noninjective_failure']=all(not all(d[0]==c for c in [0,1]) for d in product([0,1],repeat=2))
# Boundary: a decoder that reads clock state need not commute with retiming.
checks['stateful_timing_boundary']=(int(schedules['baseline']['B'][2]>2)!=int(schedules['delayed']['B'][2]>2))
results={'status':'FINITE_MODEL_CHECKS_ONLY','checks':checks,'passed':all(checks.values()),'cases':cases,'scope':'Causal event schedules and executed interpretation equations; no actual neural or phenomenal observations.'}
Path(__file__).with_name('MODEL_RESULTS.json').write_text(json.dumps(results,indent=2)+'\n')
assert results['passed'];print(json.dumps({'checks':len(checks),'executions':len(cases),'passed':True}))
