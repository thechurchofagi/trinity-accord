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
check('revision_R140', graph['revision'] == 'R140-v1.0')
ids = {node['id'] for node in graph['nodes']}
for anchor in graph['consolidation_R138']['anchors']:
    check('existing_anchor_' + anchor, anchor in ids)
for src in graph['source_versions']:
    raw = (ROOT / src['snapshot_workspace_path']).read_bytes()
    check('pinned_source_' + src['paper'], hashlib.sha256(raw).hexdigest() == src['sha256'])
for filename in ['Organization_Capability_Experience_v0_2.md', 'DISPOSITION_AND_REVIEW_ZH.md']:
    path = REC / filename
    text = path.read_text()
    check(filename + '_math_delimiters', text.count(r'\[') == text.count(r'\]')
          and text.count(r'\(') == text.count(r'\)'))
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target and not target.startswith('#'):
            check(filename + '_link_' + target, (path.parent / target.split('#')[0]).exists())
check('memory_active_revision', '当前形式化基础：**R140-v1.0**' in (ROOT / 'MEMORY.md').read_text())
check('memory_active_priority', '当前最高优先级' in (ROOT / 'MEMORY.md').read_text())

import fitz
pdfpath=REC/'output/pdf/UCT_Formal_Companion_v0_2.pdf'
doc=fitz.open(pdfpath)
check('pdf_eight_pages',len(doc)==8)
check('pdf_unencrypted',not doc.is_encrypted)
overflow=[]
for i,page in enumerate(doc):
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            x0,y0,x1,y1=line['bbox']
            if x0<39 or x1>page.rect.width-39 or y0<20 or y1>page.rect.height-20:
                overflow.append([i+1,line['bbox']])
check('pdf_safe_bounds',not overflow)
paper=(REC/'Organization_Capability_Experience_v0_2.md').read_text()
for i in range(1,4):
    check('proposition_'+str(i)+'_once',paper.count('**Proposition '+str(i))==1)
for anchor in re.findall(r'\b(?:A|B|C|D|R\d+):[A-Z][A-Z_0-9]*',paper):
    check('manuscript_anchor_'+anchor,anchor in ids)
pdf_review={
 'pages':len(doc),'sha256':hashlib.sha256(pdfpath.read_bytes()).hexdigest(),
 'visual_review':'All eight final pages inspected by the same assistant after formula, heading and URL layout repairs.',
 'scope':'Review edition; no overlapping or clipped content observed. Not publication or independent mathematical review.'
}

report = {
    'revision': 'R140-v1.0',
    'baseline_commit': '692a091ede41b0111c0423855a213566460793bc',
    'scope': 'Source bytes, graph preservation, selected references and editorial consistency only; not proof verification.',
    'proof_review': 'Same-assistant selected-source review and manuscript restatement; not independent review or a proof assistant.',
    'new_nodes': 0, 'new_rules': 0, 'pdf_review': pdf_review,
    'checks': checks,
    'passed': sum(x['pass'] for x in checks),
    'total': len(checks),
    'all_pass': all(x['pass'] for x in checks),
}
(REC / 'VALIDATION.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ['passed', 'total', 'all_pass']}))
if not report['all_pass']:
    raise SystemExit([c for c in checks if not c['pass']])
