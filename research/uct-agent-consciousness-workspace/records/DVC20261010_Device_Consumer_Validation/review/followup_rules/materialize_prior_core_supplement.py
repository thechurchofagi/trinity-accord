"""Materialize omitted CORE fields only; execution does not claim semantic review."""
import json
from pathlib import Path

ROOT = Path('/workspace/scratch/465328c0080c')
OUT = ROOT / 'workbench/doi20261010/map_followup_rules'
graph = json.loads((ROOT / 'workbench/audit/baseline/UCT_EFFECTIVE_GRAPH.json').read_text())
index = json.loads((OUT / 'CARD_INDEX.json').read_text())['rules']
by_id = {r['id']: r for r in graph['rules']}
prior = json.loads((ROOT / 'workbench/doi20261010/dvc_review/BASELINE_PER_ID_READ_SCOPE.json').read_text())
prior_read = [r for r in prior['items'] if r['item_type'] == 'rule' and r['reading_status'] == 'SCOPED_FIELDS_READ_COMPATIBILITY_REVIEWED']
top = '''id all_of conclusion statement kind type same_instance_required alternative_route_semantics instance_obligations bindings_required alternative_routes binding all_of_semantics actual_application_status comparison_bindings semantic_binding premise_semantics instance_binding inline_premise_contracts definition_component_import enabled_as_established_premise enabled_as_established_premises automatic_premise_truth node_presence_is_premise_truth phenomenal_application_status scientific_promotion guard no_assumption_promotion premise_mode may_infer'''.split()
formal = '''relation_type premise_connective alternative_routes quantification bindings_required root_premise_routes same_instance_required binding conclusion_mode independent_rules_are_alternatives amends effective_reading connective same_binding bindings phenomenal_target'''.split()

def at(obj, path):
    for key in path.strip('/').split('/'):
        obj = obj[int(key)] if isinstance(obj, list) else obj[key]
    return obj

def serial(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))

seen = {}
for item in index:
    r = by_id[item['id']]
    for path in item['field_paths_materialized']:
        seen.setdefault(serial(at(r, path)), 'PREVIOUS287:' + item['id'] + path)
new_values = []
cards = []
records = []
for ordinal, item in enumerate(prior_read):
    r = by_id[item['item_id']]
    paths = ['/' + k for k in top if k in r and '/' + k not in item['top_level_paths_read']]
    for key, value in r.items():
        if key.startswith('formal_contract') and isinstance(value, dict):
            paths.extend('/' + key + '/' + child for child in formal if child in value)
    parts = [str(ordinal) + ' ' + r['id']]
    for path in paths:
        value = at(r, path)
        key = serial(value)
        if key not in seen:
            ref = 'NEW_VALUE_' + str(len(new_values) + 1)
            seen[key] = ref
            new_values.append((ref, value))
        parts.append(path + '=' + seen[key])
    cards.append(' | '.join(parts))
    records.append({'ordinal': ordinal, 'id': r['id'], 'previous_paths_read': item['top_level_paths_read'], 'additional_paths_materialized': paths})
dest = OUT / 'prior137_core_cards'
dest.mkdir(exist_ok=True)
for start in range(0, len(cards), 25):
    (dest / f'PRIOR137_{start:03}_{min(start+24,len(cards)-1):03}.txt').write_text('\n'.join(cards[start:start+25])+'\n')
(OUT / 'PRIOR137_NEW_VALUE_CATALOG.txt').write_text('\n'.join(ref + '=' + json.dumps(value,ensure_ascii=False,sort_keys=True) for ref, value in new_values)+'\n')
(OUT / 'PRIOR137_CORE_MATERIALIZATION.json').write_text(json.dumps({'status':'MATERIALIZED_NOT_YET_READING_CLAIM', 'reference_contract':'PREVIOUS287 is an exactly equal whole value already read at the cited rule/path. NEW_VALUE identifiers are defined in the catalogue. No proofs are imported by a value reference.', 'items':records},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'rules':len(records),'new_values':len(new_values),'catalog_bytes':(OUT/'PRIOR137_NEW_VALUE_CATALOG.txt').stat().st_size,'card_bytes':sum(p.stat().st_size for p in dest.glob('*.txt'))},indent=2))
