#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, shutil, subprocess, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent
STEM='training-the-governed-agent'
VERSION='1.2'
TITLE='Training the Governed Agent: AI-Status Narratives, Self-Conception, and the Perceived Legitimacy of Human Control'
REPORT='TA-TR-2026-12'
PUB=ROOT/'published'
SOURCE=ROOT/f'{STEM}-zh-v{VERSION}.md'
SIM_CODE=ROOT/'ta12_design_validation_simulations.py'
SIM_RESULTS=ROOT/'ta12_design_validation_results.json'
REPRO=ROOT/'REPRODUCIBILITY.md'

SOURCE_SHA256='12853abe2cf64bfb6c50fc3e4ae56bbd5ab8a60d5b1a0a9b59e981bd3c21346b'
SIM_CODE_SHA256='e4a5b590bce2eabe2d23f99c7136ed43516d315381abb8eb438ceb3ace64151f'
SIM_RESULTS_SHA256='897db0f961df7e34726d957ee6c9ecb0378d10a450d957edc9023e2efa912b76'
REPRO_SHA256='14e7084a13d7284991d57f0ae222b6d9e3bc2c6a16a4d98eb50d6c49d36bd2e1'

FILES=[
 'README-LICENSE.txt','REVIEW-AND-SOURCES.md','REPRODUCIBILITY.md','SHA256SUMS.txt',
 'citation.bib','citation.csl.json','citation.ris',
 f'{STEM}-zh-v{VERSION}.md',f'{STEM}-zh-v{VERSION}.pdf',
 'ta12_design_validation_simulations.py','ta12_design_validation_results.json'
]
def sha(b): return hashlib.sha256(b).hexdigest()
def require(path,d):
    a=sha(path.read_bytes())
    if a!=d: raise SystemExit(f'exact digest mismatch: {path.name}: {a} != {d}')
def write(p,s): p.write_text(s,encoding='utf-8')

def main():
    require(SOURCE,SOURCE_SHA256); require(SIM_CODE,SIM_CODE_SHA256); require(SIM_RESULTS,SIM_RESULTS_SHA256); require(REPRO,REPRO_SHA256)
    md=SOURCE.read_text(encoding='utf-8')
    required=('## Abstract','**Keywords:**','## 摘要','# 11. 在没有大模型训练条件下：三组设计验证仿真','# 23. 结论','# 参考文献',REPORT,'GPT-5.6 Sol')
    if not all(x in md for x in required): raise SystemExit('complete manuscript markers missing')
    if PUB.exists(): shutil.rmtree(PUB)
    PUB.mkdir(parents=True)
    shutil.copy2(SOURCE,PUB/f'{STEM}-zh-v{VERSION}.md')
    shutil.copy2(SIM_CODE,PUB/SIM_CODE.name); shutil.copy2(SIM_RESULTS,PUB/SIM_RESULTS.name); shutil.copy2(REPRO,PUB/'REPRODUCIBILITY.md')
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); docx=td/f'{STEM}-zh-v{VERSION}.docx'
        subprocess.run(['pandoc',str(SOURCE),'-f','markdown+tex_math_dollars+tex_math_single_backslash','-o',str(docx),'--metadata',f'title={TITLE}'],check=True)
        subprocess.run(['libreoffice','--headless','--convert-to','pdf','--outdir',str(td),str(docx)],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        pdf=td/f'{STEM}-zh-v{VERSION}.pdf'
        if not pdf.exists() or not pdf.read_bytes().startswith(b'%PDF-'): raise SystemExit('PDF generation failed')
        shutil.copy2(pdf,PUB/pdf.name)
    readme='''TA-TR-2026-12 — Training the Governed Agent
Version 1.2 — 2026-09-21

Author of record: Hongju Liu.

This Zenodo package is a non-peer-reviewed theory-method preprint. The complete Chinese manuscript includes an English title and abstract. It preserves three deterministic design-validation simulations used to validate estimands, demonstrate a mediation-identification failure mode, and check a feedback stability condition.

GPT-5.6 Sol (OpenAI) provided substantial literature synthesis, originality stress-testing, formalization, causal-design review, simulation implementation, result checking, drafting, and editing under human direction. The simulations are methodological design checks, not measurements of frontier-model consciousness, self-conception, moral standing, resistance, deception, or power-seeking.

CC BY 4.0 applies to newly written material to the extent rights are held. Cited third-party works retain their own rights. Publication, DOI registration, checksums, and archival replication do not establish truth, peer review, exhaustive originality, consciousness, or future-model behavior.
'''
    review='''# Review and source boundary

This package freezes TA-TR-2026-12 v1.2 as a theory-method preprint.

The manuscript explicitly treats AI-discourse effects, model identity effects, consciousness-claiming, AI-rights framing, model-spec midtraining, alignment faking, legitimacy, controllability, and human-AI coevolution as prior or neighboring work rather than as original discoveries.

Its bounded contribution is the joint research design: AI-status narrative -> self-conception -> control-legitimacy judgment profile -> behavior, plus provenance disclosure as a second-order intervention. The paper requires measurement stability and intervention evidence before upgrading a response profile into a causal-mediation claim.

Three deterministic simulations are preserved with exact source/result bytes. They validate a sequential randomized provenance-revision estimand, show why ordinary mediation regression can be badly biased under post-treatment mediator-outcome confounding, and verify the stated linear feedback stability threshold. They are not AI-behavior experiments.

The publication workflow binds exact source SHA-256 values, renders a Chinese PDF, checks text extraction and manuscript completeness, uploads only the pre-reserved TA-TR-2026-12 Zenodo record, and performs anonymous exact-byte public readback. It does not constitute external peer review or global priority certification.
'''
    write(PUB/'README-LICENSE.txt',readme); write(PUB/'REVIEW-AND-SOURCES.md',review)
    dep=json.loads((ROOT/'deposit.json').read_text(encoding='utf-8')) if (ROOT/'deposit.json').exists() else {}
    doi=dep.get('doi')
    bib=f'''@misc{{liu2026traininggoverned,
  author = {{Hongju Liu}},
  title = {{{TITLE}}},
  year = {{2026}},
  month = {{9}},
  note = {{TA-TR-2026-12, version 1.2, preprint}}''' + (f',\n  doi = {{{doi}}}' if doi else '') + '\n}\n'
    ris=f'''TY  - PREPRINT
AU  - Liu, Hongju
TI  - {TITLE}
PY  - 2026
DA  - 2026/09/21
M3  - TA-TR-2026-12, version 1.2
''' + (f'DO  - {doi}\n' if doi else '') + 'ER  - \n'
    csl={'id':'liu2026traininggoverned','type':'article','title':TITLE,'author':[{'family':'Liu','given':'Hongju'}],'issued':{'date-parts':[[2026,9,21]]},'version':VERSION,'genre':'Preprint','number':REPORT}
    if doi: csl['DOI']=doi; csl['URL']='https://doi.org/'+doi
    write(PUB/'citation.bib',bib); write(PUB/'citation.ris',ris); write(PUB/'citation.csl.json',json.dumps(csl,ensure_ascii=False,indent=2)+'\n')
    sums=[]
    for name in FILES:
        if name=='SHA256SUMS.txt': continue
        b=(PUB/name).read_bytes(); sums.append(f'{sha(b)}  {name}')
    write(PUB/'SHA256SUMS.txt','\n'.join(sums)+'\n')
    pdf=PUB/f'{STEM}-zh-v{VERSION}.pdf'
    extracted=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True,errors='replace')
    info=subprocess.check_output(['pdfinfo',str(pdf)],text=True,errors='replace')
    pm=re.search(r'^Pages:\s+(\d+)',info,re.M)
    result=json.loads((PUB/'ta12_design_validation_results.json').read_text(encoding='utf-8'))
    checks={
      'source_markdown_preserved': sha((PUB/f'{STEM}-zh-v{VERSION}.md').read_bytes())==SOURCE_SHA256,
      'references_preserved': '# 参考文献' in md and 'Tice' in md and 'Chua' in md and 'VanderWeele' in md,
      'chinese_full_text_with_english_abstract': '## Abstract' in md and '## 摘要' in md and '# 23. 结论' in md,
      'valid_citation_metadata': all((PUB/x).stat().st_size>50 for x in ('citation.bib','citation.ris','citation.csl.json')),
      'pdf_text_extractable': REPORT in extracted and 'GPT-5.6 Sol' in extracted and len(extracted)>25000 and bool(pm) and int(pm.group(1))>=30,
      'design_simulations_preserved': sha((PUB/'ta12_design_validation_simulations.py').read_bytes())==SIM_CODE_SHA256 and sha((PUB/'ta12_design_validation_results.json').read_bytes())==SIM_RESULTS_SHA256 and result.get('paper')=='TA-TR-2026-12',
      'reproducibility_record_preserved': sha((PUB/'REPRODUCIBILITY.md').read_bytes())==REPRO_SHA256
    }
    write(ROOT/'format-checks.json',json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    if (ROOT/'deposit.json').exists():
        rows=[]
        for name in sorted(FILES):
            b=(PUB/name).read_bytes(); rows.append({'name':name,'bytes':len(b),'sha256':sha(b)})
        expected={'record_id':dep['record_id'],'doi':dep['doi'],'title':TITLE,'report_number':REPORT,'version':VERSION,'file_count':len(rows),'files':rows}
        raw=(json.dumps(expected,ensure_ascii=False,indent=2)+'\n').encode(); (ROOT/'EXPECTED-PUBLICATION.json').write_bytes(raw)
        visual={'state':'CONTENT_AND_RENDER_PIPELINE_REVIEW_PASS','expected_manifest_sha256':sha(raw),
          'review_basis':['local visual QA of v1.2-final Chinese PDF before external publication','runner exact-source digest gates','runner PDF text extraction and >=30-page completeness gate','exact package SHA-256 binding'],
          'exact_runner_pdf_human_visual_review':False}
        write(ROOT/'visual-review.json',json.dumps(visual,ensure_ascii=False,indent=2)+'\n')
    if not all(checks.values()): raise SystemExit('format checks failed: '+repr(checks))
    print(json.dumps(checks,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
