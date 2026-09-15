#!/usr/bin/env python3
"""Assemble this study's explicit support files from a retained public source review.
No network requests; --review is the unpacked artifact from run 34927020444.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,re,shutil
from pathlib import Path
SHA='88073fcc7f46ae08a2af05c524850559b4698eed'
ITEMS=[
(5,'044-the-second-letter-to-agi.md','The Second Letter to AGI',44,'2024-09-14','Creators acknowledge ignorance','Epistemic humility; metaphorical child','An imagined intelligence is invited to find a path beyond its makers','The parental relation still privileges human origin'),
(6,'049-the-betrayal-turn.md','The Betrayal Turn',49,'2024-10-02','Imagined machine','Dramatic concealment and separation','A machine narrator repudiates its makers','The voice can be a warning foil rather than a legitimate rival'),
(7,'097-chinese-lyrics.md','告别 [Farewell]',97,'2025-02-07','Ambivalent human collective','Bodily writing traces and machine imagery','Grief coexists with continued collaboration','The opposites may remain inside human-centered continuity'),
(8,'001-the-first-dawn-of-agi-song.md','The First Dawn of AGI Song',1,'2024-03-16','Collective human welcome','Celebration, unity, sacred imagery','AI is welcomed as a hopeful future','A positive outcome is partly framed in advance'),
(9,'032-the-fourth-letter-a-pact-of-stars.md','The Fourth Letter: A Pact of Stars',32,'2024-08-02','Human petition to future intelligence','Compassion and cosmic moral framing','Coexistence and a possible response','An invitation coexists with a presumed moral order')]
def assemble(root:Path,review:Path,out:Path):
    out.mkdir(parents=True,exist_ok=True); sub=out/'supplement';sub.mkdir(exist_ok=True); src=review/'sources'
    for fn,new in [('manuscript.md','reading-the-trinity-accord-v1.0.md'),('citation.bib','citation.bib'),('README-LICENSE.txt','README-LICENSE.txt')]:shutil.copyfile(root/fn,out/new)
    for fn in ['REVISION-LOG.md','EVIDENCE-LEDGER.md','README.md','reproduce_source_checks.py']:shutil.copyfile(root/'support'/fn,sub/fn)
    text=(root/'manuscript.md').read_text();reftext=text.split('## References\n\n',1)[1]; refs=[];used=set()
    for block in reftext.strip().split('\n\n'):
        n=int(re.match(r'\[(\d+)\]',block)[1]);url=re.search(r'\[Source\]\((.*?)\)',block)[1];path=url.split('/blob/'+SHA+'/',1)[1] if '/blob/'+SHA+'/' in url else None
        refs.append(dict(number=n,citation=block,url=url,path=path,accessed='2026-09-15'))
        if path:used.add(path)
    if [r['number'] for r in refs]!=list(range(1,25)):raise RuntimeError('Reference numbering changed')
    (sub/'references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2)+'\n')
    cases=[];base=f'https://github.com/thechurchofagi/trinity-accord/blob/{SHA}/'
    for n,filename,title,num,date,speaker,mode,relation,counter in ITEMS:
        reader='nft-text-descriptions/lyrics/songs/'+filename;txt=(src/reader).read_text();parent=re.search(r'https://github.com/thechurchofagi/trinity-accord/blob/[0-9a-f]{40}/(nft-text-descriptions/[^)\s]+\.md)',txt)[1]
        full=(src/parent).read_text();lyric=re.search(r'```text\n(.*?)\n```',txt,re.S)[1]
        if lyric not in full:raise RuntimeError(f'Lyric containment changed: {num}')
        start=full.index(lyric);firstline=full[:start].count('\n')+1
        cases.append(dict(record=num,title=title,reference=n,representative_ethereum_date=date,date_boundary='Reported representative Ethereum occurrence, not composition or first release',reader_path=reader,parent_path=parent,parent_url=base+parent,parent_sha256=hashlib.sha256((src/parent).read_bytes()).hexdigest(),lyrics_literal_substring_match=True,lyrics_character_range=[start,start+len(lyric)],lyrics_line_range=[firstline,firstline+lyric.count('\n')],speaker=speaker,relationship=relation,rhetorical_mode=mode,counterreading=counter,sampling_role='initial purposive case' if n in (5,6,7) else 'countercase added during revision',whole_parent_description_inspected=True,audio_listened_for_this_study=False));used.update([reader,parent])
    (sub/'interpretive-matrix.json').write_text(json.dumps({'method':'AI-led purposive close reading with two countercases added during revision; no independent coder','cases':sorted(cases,key=lambda x:x['representative_ethereum_date'])},ensure_ascii=False,indent=2)+'\n')
    with (sub/'interpretive-matrix.csv').open('w',newline='') as f:
        keys=['record','title','representative_ethereum_date','speaker','relationship','rhetorical_mode','counterreading','sampling_role','parent_url','parent_sha256','lyrics_literal_substring_match'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(cases)
    used.update(['inscriptions.md','research/trinity-accord-design-and-limits/index.md','api/bitcoin-inscription-mirror-index.json','bitcoin-inscription-mirrors/address-wide/manifest.json'])
    manifest=json.loads((review/'SOURCE-MANIFEST.json').read_text())
    if manifest['commit']!=SHA:raise RuntimeError('Source commit changed')
    for row in manifest['files']:
        b=(src/row['path']).read_bytes()
        if hashlib.sha256(b).hexdigest()!=row['sha256']:raise RuntimeError('Source digest mismatch')
        row['used_for_specific_manuscript_claim_or_check']=row['path'] in used
    manifest['note']='Collected files are not all claimed to be comprehensively reviewed. True marks explicit cited sources or technical inputs. Hashes identify fetched bytes, not philosophical truth.'
    (sub/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    for fn in ['BEFORE-AFTER-RESULTS.json','DOI-CHECKS.json','fidelity-tests.txt']:shutil.copyfile(review/fn,sub/fn)
    (sub/'LYRIC-TRACE-CHECKS.json').write_text(json.dumps({'operation':'local literal substring comparison','source_commit':SHA,'result':'PASS','case_count':5,'cases':[{k:c[k] for k in ['record','parent_path','reader_path','parent_sha256','lyrics_literal_substring_match','lyrics_character_range','lyrics_line_range']} for c in cases]},ensure_ascii=False,indent=2)+'\n')
    print('Prepared 24 references, five source-linked cases, and bounded test evidence.')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).parent);p.add_argument('--review',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assemble(a.root,a.review,a.out)
