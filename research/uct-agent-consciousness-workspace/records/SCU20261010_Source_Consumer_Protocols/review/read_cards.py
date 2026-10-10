"""Render fixed-map semantic text for human review; this script does not review it."""
import json, sys
from pathlib import Path

BASE = Path(__file__).parent
g = json.loads((BASE / 'baseline/UCT_EFFECTIVE_GRAPH.json').read_text())
kind = sys.argv[1]
tokens = sys.argv[2:]
node_fields = ('id', 'kind', 'label', 'statement', 'domain', 'scope', 'quantifiers',
               'proof', 'proof_or_definition', 'proof_or_evidence', 'proof_locator',
               'proof_location', 'proof_source', 'source', 'boundary', 'limits',
               'counterexamples_and_limits', 'premises', 'all_premises', 'amendment')
rule_fields = ('id', 'all_of', 'conclusion', 'statement', 'kind', 'scope',
               'proof', 'proof_sketch', 'proof_locator', 'proof_location',
               'source', 'instance_obligations', 'binding', 'guard',
               'inline_premise_contracts', 'same_instance_required', 'limits')
rows = g['nodes' if kind == 'nodes' else 'rules']
selected = [r for r in rows if any(r['id'].startswith(t) for t in tokens)]
seen = {}
for row in selected:
    print('\n###', row['id'])
    for key in (node_fields if kind == 'nodes' else rule_fields):
        if key not in row or key == 'id':
            continue
        v = row[key]
        s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
        if len(s) > 250 and s in seen:
            s = 'IDENTICAL TEXT TO ' + seen[s]
        else:
            seen[s] = row['id'] + '.' + key
        print(key + ': ' + s)
print('\nSELECTED_IDS', json.dumps([r['id'] for r in selected]))
print('COUNT', len(selected))
