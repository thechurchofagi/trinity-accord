#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, shutil, subprocess
from publication_common import ROOT,TITLE,REPORT,VERSION,DATE,STEM,ALLOWED_FILES,sha,load
PUB=ROOT/'published'; PUB.mkdir(parents=True,exist_ok=True)
dep=load('deposit.json'); doi=dep['doi']; rid=dep['record_id']
src=(ROOT/'source'/f'{STEM}-v{VERSION}.md').read_text(encoding='utf-8')
if 'DOI: ' not in src:
    marker=f'{REPORT} · Working Paper v{VERSION} · 21 September 2026'
    src=src.replace(marker,marker+'\n\nDOI: '+doi,1)
(PUB/f'{STEM}-v{VERSION}.md').write_text(src,encoding='utf-8')
for n in ('build_paper.py','generate_assets.py'):
    shutil.copy2(ROOT/n,PUB/n)
for n in ('figure1_output_wage.png','figure2_claim_gap.png','illustrative_series.csv'):
    shutil.copy2(ROOT/n,PUB/n)
license_txt=f"""The Claim Architecture Transition
{REPORT} · Version {VERSION} · {DATE}
DOI: {doi}

Human author of record and responsible depositor: Hongju Liu.
Substantial assistance from OpenAI ChatGPT (GPT-5.6 Sol) for literature search, mathematical checking, numerical illustration, drafting, document preparation, and publication QA is disclosed in the manuscript.

Status: open-access working paper / preprint; not peer reviewed.
License: CC BY 4.0 for newly written material to the extent rights are held. Cited third-party works retain their own rights.

DOI registration, checksums, code, public byte readback, and repository publication do not establish truth, peer review, exhaustive originality, policy superiority, or future forecasting accuracy.
"""
(PUB/'README-LICENSE.txt').write_text(license_txt,encoding='utf-8')
review=f"""# Review and source boundary

This release is {REPORT}, version {VERSION}, first public DOI edition.

The broad premises are not claimed as original: automation can reduce labor's income share; aggregate abundance need not imply household access; AI-capital ownership matters; scarce inputs can dominate purchasing power; and market clearing does not guarantee inclusion.

Closest identified prior work includes Båge and Wilson (2026) on wages, scarce inputs, subsistence purchasing power and rent-funded transfers; Restrepo (2025/2026) on work and labor share in the AGI limit; Mookherjee and Ray (2022) on labor share and real wages; Sen (1981) on entitlement; Lagarda, Marin and Verastegui (2026) on AI ownership; Hazari and Mohan (2024) on asset exclusion; and Korinek and Lockwood (2026) on public finance under TAI.

The narrower contribution advanced here is the unified claim-architecture formalization, the joint CES real-claim phase condition involving substitution, scarce-factor share and basic-bundle price dynamics, the power-law claim-closure condition across multiple nonnegative claim channels, and the abundance-exclusion diagnostic within one framework.

Targeted search and internal adversarial review do not certify global priority. A direct prior paper deriving the same joint formal result would narrow or defeat the novelty claim.
"""
(PUB/'REVIEW-AND-SOURCES.md').write_text(review,encoding='utf-8')
repro=f"""# Reproducibility

## Environment
Ubuntu 22.04 runner; Python 3; pandoc; LibreOffice; python-docx; lxml; numpy; matplotlib.

## Build
1. python3 generate_assets.py
2. python3 build_paper.py
3. libreoffice --headless --convert-to pdf --outdir published published/{STEM}-v{VERSION}.docx
4. python3 finalize_package.py

The illustrative series is deterministic. Parameters: Z=R=L=K=1, beta=0.35, B=0.40, q=0.70, A on a 500-point logarithmic grid from 0.1 to 1000.

The figures are comparative-statics illustrations, not empirical forecasts or calibration results.
"""
(PUB/'REPRODUCIBILITY.md').write_text(repro,encoding='utf-8')
bib=f"""@misc{{liu2026claimarchitecture,
  author = {{Liu, Hongju}},
  title = {{{TITLE}}},
  year = {{2026}},
  month = {{sep}},
  note = {{{REPORT}, Version {VERSION}, working paper}},
  doi = {{{doi}}},
  url = {{https://doi.org/{doi}}}
}}
"""
(PUB/'citation.bib').write_text(bib,encoding='utf-8')
ris=f"""TY  - GEN
AU  - Liu, Hongju
TI  - {TITLE}
PY  - 2026
DA  - 2026/09/21
M3  - Working paper / preprint
ET  - Version {VERSION}
DO  - {doi}
UR  - https://doi.org/{doi}
N1  - {REPORT}
ER  -
"""
(PUB/'citation.ris').write_text(ris,encoding='utf-8')
csl={'id':f'https://doi.org/{doi}','type':'article','title':TITLE,'author':[{'family':'Liu','given':'Hongju'}],
     'issued':{'date-parts':[[2026,9,21]]},'version':VERSION,'DOI':doi,'URL':f'https://doi.org/{doi}',
     'genre':'Working paper / preprint','note':REPORT}
(PUB/'citation.csl.json').write_text(json.dumps(csl,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# First make checksums for all package files except the checksum file itself.
targets=sorted(n for n in ALLOWED_FILES if n!='SHA256SUMS.txt')
lines=[]
for n in targets:
    b=(PUB/n).read_bytes(); lines.append(f'{sha(b)}  {n}')
(PUB/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n',encoding='utf-8')
# Basic machine gates.
pdf=PUB/f'{STEM}-v{VERSION}.pdf'; docx=PUB/f'{STEM}-v{VERSION}.docx'
txt=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True,errors='replace')
checks={'docx_generated':docx.exists() and docx.stat().st_size>10000,'pdf_generated':pdf.exists() and pdf.stat().st_size>10000,
'pdf_text_extractable':len(txt)>20000,'source_markdown_preserved':(PUB/f'{STEM}-v{VERSION}.md').exists(),
'equation_source_preserved':('[\\chi_' in src or '$$' in src or '\\[' in src),'figures_preserved':all((PUB/x).exists() for x in ('figure1_output_wage.png','figure2_claim_gap.png')),
'replication_series_preserved':(PUB/'illustrative_series.csv').exists(),'citation_metadata_valid':all((PUB/x).exists() for x in ('citation.bib','citation.ris','citation.csl.json')),
'references_preserved':'# References' in src,'ai_assistance_disclosed':'AI-assistance statement' in src,'not_peer_reviewed_disclosed':'not peer reviewed' in src.lower()}
(ROOT/'format-checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
if not all(checks.values()): raise SystemExit('format gate failed: '+repr(checks))
files=[]
for n in sorted(ALLOWED_FILES):
    b=(PUB/n).read_bytes(); files.append({'name':n,'bytes':len(b),'sha256':sha(b)})
manifest={'record_id':rid,'doi':doi,'title':TITLE,'report_number':REPORT,'version':VERSION,'file_count':len(files),'files':files}
(ROOT/'EXPECTED-PUBLICATION.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'doi':doi,'file_count':len(files),'manifest_sha256':sha((ROOT/'EXPECTED-PUBLICATION.json').read_bytes())},indent=2))
