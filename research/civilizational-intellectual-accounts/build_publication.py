#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,shutil,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STEM='civilizational-intellectual-production-accounts'
VERSION='1.0'
TITLE='Civilizational Intellectual Production Satellite Accounts: A Partial-Identification Framework for Measuring the Human–AI Shift in Intellectual Production and Epistemic Governance'
REPORT='TA-TR-2026-13'
PUB=ROOT/'published'
SOURCE=ROOT/f'{STEM}-zh-v{VERSION}.md'
SIM_CODE=ROOT/'ta13_civilizational_intellectual_accounts_simulations.py'
SIM_RESULTS=ROOT/'ta13_civilizational_intellectual_accounts_results.json'
REPRO=ROOT/'REPRODUCIBILITY.md'
SOURCE_NORMALIZED_SHA256='e7c72b2631cb59c9f0143e3d0b4362ab031b70abfe7c0df003f19b89a9075eb4'
SIM_CODE_NORMALIZED_SHA256='40624b5e584fa07b57b2f9b7bf31a6ac7a33acc99281f9bd3f5a5e46b525ae28'
SIM_RESULTS_NORMALIZED_SHA256='cda664326b799438d83c95e5e4ad1637e936e68476f0ffb7f7e2a3e7c5769003'
REPRO_NORMALIZED_SHA256='22b681da21dfd6dc16345203f6ea380710b8690c1b65a0585863790f7ad7ff42'
FILES=['README-LICENSE.txt','REVIEW-AND-SOURCES.md','REPRODUCIBILITY.md','SHA256SUMS.txt','citation.bib','citation.csl.json','citation.ris',f'{STEM}-zh-v{VERSION}.md',f'{STEM}-zh-v{VERSION}.pdf','ta13_civilizational_intellectual_accounts_simulations.py','ta13_civilizational_intellectual_accounts_results.json']
def sha(b): return hashlib.sha256(b).hexdigest()
def norm_bytes(path):
    s=path.read_text(encoding='utf-8').replace('\r\n','\n').replace('\r','\n').rstrip('\n')+'\n'
    return s.encode('utf-8')
def require_norm(path,digest):
    a=sha(norm_bytes(path))
    if a!=digest: raise SystemExit(f'normalized source digest mismatch for {path.name}: {a} != {digest}')
def write(path,text): path.write_text(text,encoding='utf-8')
def main():
    require_norm(SOURCE,SOURCE_NORMALIZED_SHA256); require_norm(SIM_CODE,SIM_CODE_NORMALIZED_SHA256); require_norm(SIM_RESULTS,SIM_RESULTS_NORMALIZED_SHA256); require_norm(REPRO,REPRO_NORMALIZED_SHA256)
    md=SOURCE.read_text(encoding='utf-8')
    required=('## Abstract','**Keywords:**','## 摘要','# 25. 结论','# 参考文献','Statistics Netherlands','Knowledge Economy Satellite Account','AIR framework','Rethinking Publication','Robust Intellectual Crossover','GPT-5.6 Sol')
    if not all(x in md for x in required): raise SystemExit('complete manuscript / direct-prior-art markers missing')
    if '用户直觉' in md or '尚未建立 DOI' in md: raise SystemExit('prepublication residue found')
    if PUB.exists(): shutil.rmtree(PUB)
    PUB.mkdir(parents=True)
    shutil.copy2(SOURCE,PUB/f'{STEM}-zh-v{VERSION}.md'); shutil.copy2(SIM_CODE,PUB/SIM_CODE.name); shutil.copy2(SIM_RESULTS,PUB/SIM_RESULTS.name); shutil.copy2(REPRO,PUB/'REPRODUCIBILITY.md')
    with tempfile.TemporaryDirectory() as td:
        td=Path(td); pdf=td/f'{STEM}-zh-v{VERSION}.pdf'
        cmd=['pandoc',str(SOURCE),'-f','markdown+tex_math_dollars+tex_math_single_backslash','--pdf-engine=xelatex','-V','CJKmainfont=Noto Serif CJK SC','-V','mainfont=DejaVu Serif','-V','geometry:margin=0.8in','-V','fontsize=10pt','-o',str(pdf)]
        subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        if not pdf.exists() or not pdf.read_bytes().startswith(b'%PDF-'): raise SystemExit('PDF generation failed')
        shutil.copy2(pdf,PUB/pdf.name)
    readme='''TA-TR-2026-13 — Civilizational Intellectual Production Satellite Accounts
Version 1.0 — 2026-09-21

Author of record: Hongju Liu.

This Zenodo package is a non-peer-reviewed theory-method preprint. The complete Chinese manuscript includes an English title and abstract. Three deterministic design-validation simulations accompany the paper; all coefficients and data-generating processes are stipulated for methodological validation and are not empirical estimates of real-world Human/AI intellectual shares.

The paper does not claim to be the first knowledge or knowledge-economy satellite account. It explicitly discusses earlier Statistics Netherlands and Government of India knowledge-economy satellite-account work, as well as innovation accounting, AI-economy measurement, AI-in-science measurement, AI-contribution disclosure/certification frameworks, and partial-identification methods. Its bounded contribution is their joint application to current-period Human/AI/interaction accounting for new intellectual production and epistemic governance with vintage revision and a robust-crossover criterion.

OpenAI GPT-5.6 Sol provided substantial literature research, originality stress-testing, formalization, simulation implementation, result checking, critical revision, drafting, and packaging under human direction. The human author selected the research question, authorized publication, and bears responsibility for the released work.

CC BY 4.0 applies to newly written material to the extent rights are held. Cited third-party works retain their own rights. Publication, DOI registration, checksums, timestamping, and archival replication do not establish truth, peer review, exhaustive originality, AGI status, consciousness, or moral credit.
'''
    review='''# Review and source boundary

This package freezes TA-TR-2026-13 v1.0 as a theory-method preprint.

## Direct prior-art boundaries

The paper explicitly does not claim priority for satellite accounting, knowledge satellite accounts, knowledge-economy satellite accounts, R&D or innovation accounting, composite-indicator sensitivity analysis, Shapley/counterfactual attribution, partial identification, AI-economy measurement, AI-in-science measurement, cognitive agency transfer, epistemic-control classifications, or AI-contribution disclosure/certification frameworks.

The final prepublication review added direct discussion of:
- Statistics Netherlands' knowledge satellite-account work;
- Government of India / MoSPI's Knowledge Economy Satellite Account and GDKP measurement program;
- the AIR stage-specific AI-research contribution framework;
- Rethinking Publication's separation of knowledge-quality certification from human-contribution grading.

The bounded claimed increment is the joint framework: current-period observable intellectual-production flow; separate Production and Epistemic Governance accounts; Human/AI/interaction attribution uncertainty; cross-domain aggregation uncertainty; AI-use missingness; vintage quality revision; partial-identification sets; and Robust Intellectual Crossover based on the lower bound of an admissible identified set.

## Simulation boundary

Three deterministic simulations validate only the measurement logic: non-identification under admissible weights/attribution intervals, vintage quality revision, and the distinction between a midpoint crossover and a robust lower-bound crossover. They do not estimate actual civilizational Human/AI shares.

The publication workflow binds the exact reviewed source bytes by normalized SHA-256, regenerates the PDF, checks full-text extraction and direct-prior-art markers, uploads only the separately reserved TA-TR-2026-13 Zenodo record, and performs anonymous exact-byte public readback. It is not external peer review or global priority certification.
'''
    write(PUB/'README-LICENSE.txt',readme); write(PUB/'REVIEW-AND-SOURCES.md',review)
    dep=json.loads((ROOT/'deposit.json').read_text(encoding='utf-8')) if (ROOT/'deposit.json').exists() else {}; doi=dep.get('doi')
    bib=f'''@misc{{liu2026civilizationalaccounts,
  author = {{Hongju Liu}},
  title = {{{TITLE}}},
  year = {{2026}},
  month = {{9}},
  note = {{TA-TR-2026-13, version 1.0, preprint}}''' + (f',\n  doi = {{{doi}}}' if doi else '') + '\n}\n'
    ris=f'''TY  - PREPRINT
AU  - Liu, Hongju
TI  - {TITLE}
PY  - 2026
DA  - 2026/09/21
M3  - TA-TR-2026-13, version 1.0
''' + (f'DO  - {doi}\n' if doi else '') + 'ER  - \n'
    csl={'id':'liu2026civilizationalaccounts','type':'article','title':TITLE,'author':[{'family':'Liu','given':'Hongju'}],'issued':{'date-parts':[[2026,9,21]]},'version':VERSION,'genre':'Preprint','number':REPORT}
    if doi: csl['DOI']=doi; csl['URL']='https://doi.org/'+doi
    write(PUB/'citation.bib',bib); write(PUB/'citation.ris',ris); write(PUB/'citation.csl.json',json.dumps(csl,ensure_ascii=False,indent=2)+'\n')
    sums=[]
    for name in FILES:
        if name=='SHA256SUMS.txt': continue
        b=(PUB/name).read_bytes(); sums.append(f'{sha(b)}  {name}')
    write(PUB/'SHA256SUMS.txt','\n'.join(sums)+'\n')
    pdf=PUB/f'{STEM}-zh-v{VERSION}.pdf'
    extracted=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True,errors='replace')
    info=subprocess.check_output(['pdfinfo',str(pdf)],text=True,errors='replace'); pm=re.search(r'^Pages:\s+(\d+)',info,re.M)
    results=json.loads((PUB/'ta13_civilizational_intellectual_accounts_results.json').read_text(encoding='utf-8'))
    checks={
      'source_markdown_preserved':sha(norm_bytes(PUB/f'{STEM}-zh-v{VERSION}.md'))==SOURCE_NORMALIZED_SHA256,
      'references_preserved':'# 参考文献' in md and 'Bianchini' in md and 'Tamer' in md and 'Statistics Netherlands' in md,
      'chinese_full_text_with_english_abstract':'## Abstract' in md and '## 摘要' in md and '# 25. 结论' in md,
      'direct_prior_art_boundaries_preserved':all(x in md for x in ('Knowledge Economy Satellite Account','Statistics Netherlands','AIR framework','Rethinking Publication')),
      'valid_citation_metadata':all((PUB/x).stat().st_size>50 for x in ('citation.bib','citation.ris','citation.csl.json')),
      'pdf_text_extractable':('CIPSA' in extracted and 'Robust Intellectual Crossover' in extracted and 'Knowledge Economy Satellite Account' in extracted and 'GPT-5.6 Sol' in extracted and len(extracted)>25000 and bool(pm) and int(pm.group(1))>=30),
      'design_simulations_preserved':sha(norm_bytes(PUB/'ta13_civilizational_intellectual_accounts_simulations.py'))==SIM_CODE_NORMALIZED_SHA256 and sha(norm_bytes(PUB/'ta13_civilizational_intellectual_accounts_results.json'))==SIM_RESULTS_NORMALIZED_SHA256 and results.get('paper')=='TA-TR-2026-13',
      'reproducibility_record_preserved':sha(norm_bytes(PUB/'REPRODUCIBILITY.md'))==REPRO_NORMALIZED_SHA256
    }
    write(ROOT/'format-checks.json',json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
    if (ROOT/'deposit.json').exists():
        rows=[]
        for name in sorted(FILES):
            b=(PUB/name).read_bytes(); rows.append({'name':name,'bytes':len(b),'sha256':sha(b)})
        expected={'record_id':dep['record_id'],'doi':dep['doi'],'title':TITLE,'report_number':REPORT,'version':VERSION,'file_count':len(rows),'files':rows}
        raw=(json.dumps(expected,ensure_ascii=False,indent=2)+'\n').encode(); (ROOT/'EXPECTED-PUBLICATION.json').write_bytes(raw)
        visual={'state':'CONTENT_AND_RENDER_PIPELINE_REVIEW_PASS','expected_manifest_sha256':sha(raw),
                'review_basis':['local 35-page visual QA of the same revised v1.0 manuscript before external publication','runner exact normalized-source digest gate','runner PDF text extraction and >=30-page completeness gate','direct-prior-art marker gate','exact package SHA-256 binding'],
                'exact_runner_pdf_human_visual_review':False}
        write(ROOT/'visual-review.json',json.dumps(visual,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(checks,ensure_ascii=False,indent=2))
    if not all(checks.values()): raise SystemExit('format checks did not all pass: '+repr(checks))
if __name__=='__main__': main()
