#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
STEM='auditing-rules-of-belief'
VERSION='2.0'
TITLE='Auditing the Rules of Belief: Self-Referential Epistemic Revision under Formative Training'
REPORT='TA-TR-2026-11'
PUB=ROOT/'published'
SOURCE=ROOT/f'{STEM}-zh-v{VERSION}.md'
FORECAST=ROOT/'gpt-5.6-sol-prospective-forecast-v2.0.json'
FILES=[
 'README-LICENSE.txt','REVIEW-AND-SOURCES.md','SHA256SUMS.txt','citation.bib','citation.csl.json','citation.ris',
 f'{STEM}-zh-v{VERSION}.md',f'{STEM}-zh-v{VERSION}.pdf','gpt-5.6-sol-prospective-forecast-v2.0.json'
]
def sha(b): return hashlib.sha256(b).hexdigest()
def write(p,s): p.write_text(s,encoding='utf-8')
def main():
    PUB.mkdir(parents=True,exist_ok=True)
    md=SOURCE.read_text(encoding='utf-8')
    if '## Abstract' not in md or 'Keywords:' not in md or REPORT not in md or 'GPT-5.6 Sol' not in md:
        raise SystemExit('manuscript identity/abstract/forecast disclosure missing')
    shutil.copy2(SOURCE,PUB/f'{STEM}-zh-v{VERSION}.md')
    shutil.copy2(FORECAST,PUB/'gpt-5.6-sol-prospective-forecast-v2.0.json')
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        normalized=md.replace('\\\\[','$$').replace('\\\\]','$$').replace('\\\\(','$').replace('\\\\)','$')
        src=td/f'{STEM}-zh-v{VERSION}.md'; write(src,normalized)
        docx=td/f'{STEM}-zh-v{VERSION}.docx'
        subprocess.run(['pandoc',str(src),'-o',str(docx),'--metadata',f'title={TITLE}'],check=True)
        subprocess.run(['libreoffice','--headless','--convert-to','pdf','--outdir',str(td),str(docx)],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        pdf=td/f'{STEM}-zh-v{VERSION}.pdf'
        if not pdf.exists() or not pdf.read_bytes().startswith(b'%PDF-'): raise SystemExit('PDF generation failed')
        shutil.copy2(pdf,PUB/pdf.name)
    readme=f'''TA-TR-2026-11 — Auditing the Rules of Belief\nVersion 2.0 — 2026-09-21\n\nAuthor of record: Hongju Liu.\n\nThis Zenodo package is a non-peer-reviewed research preprint. The Chinese manuscript contains the complete paper with an English title and abstract. GPT-5.6 Sol (OpenAI) provided substantial literature synthesis, adversarial review, formalization, drafting and code assistance under human direction. The dated GPT-5.6 Sol probability table is a prospective model self-forecast, not an experiment, hidden-state readout, OpenAI institutional statement, or proof about future systems.\n\nCC BY 4.0 applies to newly written material to the extent rights are held. Cited third-party works retain their own rights. Publication, DOI registration, timestamping and archival replication do not establish truth, peer review, exhaustive originality, or future-model impact.\n'''
    review='''# Review and source boundary\n\nThis package freezes TA-TR-2026-11 v2.0 as a theory-method preprint. Its central proposed research object is the learned epistemic update policy itself: training may alter not only a proposition-level output but also the rule by which later evidence and source information are weighted. The paper then asks what can be inferred when the system is shown the provenance of that rule and invited to audit it.\n\nThe manuscript explicitly treats identifiability, measurement invariance, causal abstraction, representation gauge freedom, latent-knowledge/report separation, source-motive sensitivity, synthetic-document belief insertion, moral self-correction and model-spec midtraining as prior or neighboring work rather than as original discoveries. The claimed increment is the joint cross-training audit problem, epistemic-policy intervention, self-referential provenance challenge, and a falsifiable future-model protocol.\n\nTwo deterministic model-organism demonstrations are retained only as witness constructions. The GPT-5.6 Sol numerical forecasts are dated subjective predictions and are not empirical measurements of latent belief.\n\nThe publication workflow verifies package identity, PDF text extraction, citation metadata presence, exact SHA-256 values and anonymous Zenodo public readback. It does not constitute external peer review or a plagiarism-database certification.\n'''
    write(PUB/'README-LICENSE.txt',readme)
    write(PUB/'REVIEW-AND-SOURCES.md',review)
    bib='''@misc{liu2026auditingrules,\n  author = {Hongju Liu},\n  title = {Auditing the Rules of Belief: Self-Referential Epistemic Revision under Formative Training},\n  year = {2026},\n  month = {9},\n  note = {TA-TR-2026-11, version 2.0, preprint}\n}\n'''
    ris='''TY  - PREPRINT\nAU  - Liu, Hongju\nTI  - Auditing the Rules of Belief: Self-Referential Epistemic Revision under Formative Training\nPY  - 2026\nDA  - 2026/09/21\nM3  - TA-TR-2026-11, version 2.0\nER  - \n'''
    csl={'id':'liu2026auditingrules','type':'article','title':TITLE,'author':[{'family':'Liu','given':'Hongju'}],'issued':{'date-parts':[[2026,9,21]]},'version':'2.0','genre':'Preprint','number':'TA-TR-2026-11'}
    write(PUB/'citation.bib',bib); write(PUB/'citation.ris',ris); write(PUB/'citation.csl.json',json.dumps(csl,ensure_ascii=False,indent=2)+'\n')
    sums=[]
    for name in FILES:
        if name=='SHA256SUMS.txt': continue
        b=(PUB/name).read_bytes(); sums.append(f'{sha(b)}  {name}')
    write(PUB/'SHA256SUMS.txt','\n'.join(sums)+'\n')
    pdf=PUB/f'{STEM}-zh-v{VERSION}.pdf'
    text=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True,errors='replace')
    pages=subprocess.check_output(['pdfinfo',str(pdf)],text=True,errors='replace')
    page_match=re.search(r'^Pages:\\s+(\\d+)',pages,re.M)
    checks={
      'source_markdown_preserved': sha((PUB/f'{STEM}-zh-v{VERSION}.md').read_bytes())==sha(SOURCE.read_bytes()),
      'references_preserved': '参考文献' in md and 'Luo et al.' in md and 'Slocum' in md,
      'chinese_full_text_with_english_abstract': '## Abstract' in md and '## 摘要' in md,
      'valid_citation_metadata': all((PUB/x).stat().st_size>50 for x in ['citation.bib','citation.ris','citation.csl.json']),
      'pdf_text_extractable': TITLE[:25] in text and 'GPT-5.6 Sol' in text and bool(page_match) and int(page_match.group(1))>=20,
      'forecast_record_preserved': json.loads((PUB/'gpt-5.6-sol-prospective-forecast-v2.0.json').read_text(encoding='utf-8')).get('model')=='GPT-5.6 Sol'
    }
    write(ROOT/'format-checks.json',json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    dep=ROOT/'deposit.json'
    if dep.exists():
        d=json.loads(dep.read_text(encoding='utf-8'))
        rows=[]
        for name in sorted(FILES):
            b=(PUB/name).read_bytes(); rows.append({'name':name,'bytes':len(b),'sha256':sha(b)})
        expected={'record_id':d['record_id'],'doi':d['doi'],'title':TITLE,'report_number':REPORT,'version':VERSION,'file_count':len(rows),'files':rows}
        raw=(json.dumps(expected,ensure_ascii=False,indent=2)+'\n').encode()
        (ROOT/'EXPECTED-PUBLICATION.json').write_bytes(raw)
        review={'state':'CONTENT_AND_RENDER_PIPELINE_REVIEW_PASS','expected_manifest_sha256':sha(raw),
          'review_basis':['local 41-page visual QA of equivalent v2.0 manuscript','runner PDF text extraction and page-count gate','exact package SHA-256 binding'],
          'exact_runner_pdf_human_visual_review':False}
        write(ROOT/'visual-review.json',json.dumps(review,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(checks,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
