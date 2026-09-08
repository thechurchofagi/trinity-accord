"""Finish the reviewed curatorial presentation without changing source records."""
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1];D=P/'dist'
p=D/'museum.js';s=p.read_text()
statement="import {createDocumentPanel} from './document-panel.js';"
if statement not in s:s=statement+'\n'+s
needle='function documentTexture(e){'
replacement=needle+"\n if(e.id.startsWith('canon-')||e.id==='authority-boundary')return createDocumentPanel(e,lang);"
if replacement not in s:
 assert s.count(needle)==1
 s=s.replace(needle,replacement)
p.write_text(s)
p=P/'scripts/check_presentation.py'
if p.exists():
 s=p.read_text().replace('#flaw-content','#flaw-view')
 p.write_text(s)
# Leave the original model/evidence/audio untouched. The following is a
# production record for later curatorial speech, not an interpretation rule.
g=json.loads((D/'data/guide-audio.json').read_text())
english=[t for key in ['tracks','inspectionTracks'] for t in g[key] if t['language']=='en']
assert len(english)==11
assert all(t.get('captionAudit',{}).get('accepted') for t in english)
for t in english:
 assert 'Chatterbox' in t.get('provenance',{}).get('model','')
print('REVIEWED_DOCUMENT_PANELS_CONNECTED; 11 English curatorial recordings accepted',flush=True)
