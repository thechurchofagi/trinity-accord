"""Check editorial consolidation integrity; this does not verify mathematical proofs."""
from pathlib import Path
import hashlib
import json
import re

REC = Path(__file__).resolve().parent
ROOT = REC.parent.parent
graph = json.loads((ROOT / 'UCT_FORMAL_GRAPH.json').read_text())
checks = []

def check(name, condition):
    checks.append({'name': name, 'pass': bool(condition)})

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':')).encode()).hexdigest()

expected = {
    'nodes': '56e0d3bc680b5d131d43687c5d86980249ade6e842bead741ca6fa36247d68e5',
    'rules': '7b0ea4705f318beaa90c03ffbef4d59a7b745d93c9e47659edf5cc6eb035fe06',
    'source_versions': 'f8a9ee08995e3e8f4b50ffcbc61bbb4abb9ff499e391f5a8329ab2ddd5e13403',
}
for key, value in expected.items():
    check(key + '_identical_to_R137', digest(graph[key]) == value)
check('counts_328_157', len(graph['nodes']) == 328 and len(graph['rules']) == 157)
check('revision_R138', graph['revision'] == 'R138-v1.0')
ids = {node['id'] for node in graph['nodes']}
for anchor in graph['consolidation_R138']['anchors']:
    check('existing_anchor_' + anchor, anchor in ids)
for src in graph['source_versions']:
    raw = (ROOT / src['snapshot_workspace_path']).read_bytes()
    check('pinned_source_' + src['paper'], hashlib.sha256(raw).hexdigest() == src['sha256'])
for filename in ['DEFINITION_CONTRACT_AND_PAPER_SPINE.md', 'PROOF_SPINE.md', 'REVIEW_ZH.md']:
    path = REC / filename
    text = path.read_text()
    check(filename + '_math_delimiters', text.count(r'\[') == text.count(r'\]')
          and text.count(r'\(') == text.count(r'\)'))
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target and not target.startswith('#'):
            check(filename + '_link_' + target, (path.parent / target.split('#')[0]).exists())
check('memory_active_revision', '当前形式化基础：**R138-v1.0**' in (ROOT / 'MEMORY.md').read_text())
check('memory_active_priority', '当前最高优先级' in (ROOT / 'MEMORY.md').read_text())
report = {
    'revision': 'R138-v1.0',
    'baseline_commit': 'd4d9e72b0bd02d53ac257855419b995cc0a69ad6',
    'scope': 'Source bytes, graph preservation, selected references and editorial consistency only; not proof verification.',
    'proof_review': 'Same-assistant manual review of selected existing proofs, not independent review or a proof assistant.',
    'new_nodes': 0, 'new_rules': 0,
    'checks': checks,
    'passed': sum(x['pass'] for x in checks),
    'total': len(checks),
    'all_pass': all(x['pass'] for x in checks),
}
(REC / 'VALIDATION.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['passed', 'total', 'all_pass']}))
if not report['all_pass']:
    raise SystemExit([c for c in checks if not c['pass']])
