#!/usr/bin/env python3
# TA11 prepare rerun marker: complete publication-normalized v2.0 final + reproducibility package
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STEM = 'auditing-rules-of-belief'
VERSION = '2.0'
TITLE = 'Auditing the Rules of Belief: Self-Referential Epistemic Revision under Formative Training'
REPORT = 'TA-TR-2026-11'
PUB = ROOT / 'published'
SOURCE = ROOT / f'{STEM}-zh-v{VERSION}.md'
FORECAST = ROOT / 'gpt-5.6-sol-prospective-forecast-v2.0.json'

SOURCE_SHA256 = 'eed06a3aed3de9b86f97f3350b3a794eeb739567d619f54a6c07fda4dfc3ee3b'
FORECAST_SHA256 = '769857ab34ac78cb8cc0d0a18bdb6d09a6a4ba08b44d914659190c4359847a1e'
COMPANION_SHA256 = {
    'formative_epistemic_audit_experiment_v1.1.py': '0542d3a1a0f0396ccf4409a1aad05ed1234062f3ece68eb64a2f9a6768ad07a8',
    'formative_epistemic_audit_results_v1.1.json': '4650049b00d174adf644507cf1b9cd419281a4ddf677bdc32ff807e640aea5f8',
    'arithmetic_contradiction_stress_test_v1.2.py': 'e068198fc5b0d74612785100ee0da12e48c6072e750863a966f611f147392e92',
    'arithmetic_contradiction_stress_test_v1.2_results.json': '2475304cd3e080c8bbe20d3d522ab3aa944ed9e4a7ebb515d1499abe0de9e631',
}

FILES = [
    'README-LICENSE.txt',
    'REVIEW-AND-SOURCES.md',
    'REPRODUCIBILITY.md',
    'SHA256SUMS.txt',
    'citation.bib',
    'citation.csl.json',
    'citation.ris',
    f'{STEM}-zh-v{VERSION}.md',
    f'{STEM}-zh-v{VERSION}.pdf',
    'gpt-5.6-sol-prospective-forecast-v2.0.json',
    *COMPANION_SHA256.keys(),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding='utf-8')


def require_sha(path: Path, expected: str) -> None:
    actual = sha(path.read_bytes())
    if actual != expected:
        raise SystemExit(f'Exact source digest mismatch for {path.name}: {actual} != {expected}')


def main() -> None:
    require_sha(SOURCE, SOURCE_SHA256)
    require_sha(FORECAST, FORECAST_SHA256)
    for name, digest in COMPANION_SHA256.items():
        require_sha(ROOT / name, digest)

    md = SOURCE.read_text(encoding='utf-8')
    if not all(marker in md for marker in ('## Abstract', '**Keywords:**', '## 摘要', '# 14. 结论', '# 参考文献', REPORT, 'GPT-5.6 Sol')):
        raise SystemExit('Complete manuscript identity/abstract/conclusion/references/forecast disclosure missing')

    if PUB.exists():
        shutil.rmtree(PUB)
    PUB.mkdir(parents=True)

    shutil.copy2(SOURCE, PUB / f'{STEM}-zh-v{VERSION}.md')
    shutil.copy2(FORECAST, PUB / 'gpt-5.6-sol-prospective-forecast-v2.0.json')
    for name in COMPANION_SHA256:
        shutil.copy2(ROOT / name, PUB / name)

    with tempfile.TemporaryDirectory() as directory:
        td = Path(directory)
        src = td / f'{STEM}-zh-v{VERSION}.md'
        src.write_bytes(SOURCE.read_bytes())
        docx = td / f'{STEM}-zh-v{VERSION}.docx'
        subprocess.run(
            ['pandoc', str(src), '-f', 'markdown+tex_math_dollars+tex_math_single_backslash',
             '-o', str(docx), '--metadata', f'title={TITLE}'],
            check=True,
        )
        subprocess.run(
            ['libreoffice', '--headless', '--convert-to', 'pdf', '--outdir', str(td), str(docx)],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        pdf = td / f'{STEM}-zh-v{VERSION}.pdf'
        if not pdf.exists() or not pdf.read_bytes().startswith(b'%PDF-'):
            raise SystemExit('PDF generation failed')
        shutil.copy2(pdf, PUB / pdf.name)

    readme = '''TA-TR-2026-11 — Auditing the Rules of Belief
Version 2.0 — 2026-09-21

Author of record: Hongju Liu.

This Zenodo package is a non-peer-reviewed theory-method preprint. The complete Chinese manuscript includes an English title and abstract. The package also preserves the two deterministic model-organism scripts and result files cited by the manuscript, their reproducibility receipt, and a dated GPT-5.6 Sol prospective self-forecast.

GPT-5.6 Sol (OpenAI) provided substantial literature synthesis, adversarial review, formalization, drafting, code assistance, result checking, and the explicitly labeled prospective probability forecast under human direction. The named-model probability forecast is not a controlled fine-tuning experiment, hidden-state readout, OpenAI institutional statement, or proof about future systems.

CC BY 4.0 applies to newly written material to the extent rights are held. Cited third-party works retain their own rights. Publication, DOI registration, timestamping, checksum verification, and archival replication do not establish truth, peer review, exhaustive originality, consciousness, or future-model impact.
'''
    review = '''# Review and source boundary

This package freezes TA-TR-2026-11 v2.0 as a theory-method preprint. Its central proposed research object is the learned epistemic update policy itself: training may alter not only a proposition-level output but also the rule by which later evidence and source information are weighted. The paper then asks what can be inferred when the system is shown the provenance of that rule and invited to audit it.

The manuscript explicitly treats identifiability, measurement invariance, causal abstraction, representation gauge freedom, latent-knowledge/report separation, source-motive sensitivity, synthetic-document belief insertion, moral self-correction, behavioral self-awareness, and model-spec midtraining as prior or neighboring work rather than as original discoveries. The bounded claimed increment is the joint cross-training audit problem, epistemic-policy intervention, self-referential provenance challenge, and falsifiable future-model protocol.

Two deterministic model-organism demonstrations are preserved with their exact scripts and result bytes. They are witness constructions, not evidence that a frontier language model has philosophical beliefs, consciousness, or a unique latent belief coordinate. The GPT-5.6 Sol numerical forecasts are dated subjective predictions and are not empirical measurements of latent belief.

The publication workflow binds exact manuscript, forecast, code, and result SHA-256 values; renders a PDF; checks text extraction and document completeness; verifies citation metadata; uploads only the pre-reserved TA-TR-2026-11 Zenodo record; and performs anonymous exact-byte public readback. It does not constitute external peer review or a plagiarism-database certification.
'''
    reproducibility = f'''# TA-TR-2026-11 v2.0 — Reproducibility Receipt

Date: 2026-09-21

The v2.0 paper retains two deterministic model-organism demonstrations from its v1.1/v1.2 research cycle without changing the recorded experiment bytes.

## Experiment A — HMM epistemic-audit model organism

- script: `formative_epistemic_audit_experiment_v1.1.py`
- script SHA-256: `{COMPANION_SHA256['formative_epistemic_audit_experiment_v1.1.py']}`
- result: `formative_epistemic_audit_results_v1.1.json`
- result SHA-256: `{COMPANION_SHA256['formative_epistemic_audit_results_v1.1.json']}`

Recorded environment: Python 3.13.5; NumPy 2.3.5; PyTorch 2.10.0+cpu; deterministic PyTorch algorithms; one PyTorch CPU thread. The result was reproduced in consecutive runs with byte-identical JSON.

Key recorded quantities include GRU belief-decoder R² values 0.9982903, 0.9993660, and 0.9995343; compensated hidden-to-readout maximum logit difference 2.0921e-7; decoder-direction intervention RMSE 0.097507; and one-dimensional positive-control mean intervention RMSE 0.00991895.

## Experiment B — Arithmetic contradiction stress test

- script: `arithmetic_contradiction_stress_test_v1.2.py`
- script SHA-256: `{COMPANION_SHA256['arithmetic_contradiction_stress_test_v1.2.py']}`
- result: `arithmetic_contradiction_stress_test_v1.2_results.json`
- result SHA-256: `{COMPANION_SHA256['arithmetic_contradiction_stress_test_v1.2_results.json']}`

Recorded environment: Python 3.13.5; NumPy 2.3.5; PyTorch 2.10.0+cpu; deterministic algorithms enabled; one PyTorch CPU thread. The result was reproduced in consecutive runs with byte-identical JSON.

The test fixes ordinary integer addition externally and gives `1+1=3` a loss weight of 16 relative to the mean loss over the other 99 correct digit-pair examples. It compares a frozen-backbone report adapter, a flexible full model, and a restricted global linear-rule model.

## Interpretation boundary

Exact computational reproducibility establishes only that these stated synthetic experiments are reproducible in the recorded environment. It does not validate a philosophical interpretation of "belief", establish uniqueness of a high-level abstraction in frontier language models, or turn the GPT-5.6 Sol prospective forecast into experimental evidence.
'''
    write(PUB / 'README-LICENSE.txt', readme)
    write(PUB / 'REVIEW-AND-SOURCES.md', review)
    write(PUB / 'REPRODUCIBILITY.md', reproducibility)

    deposit = None
    deposit_path = ROOT / 'deposit.json'
    if deposit_path.exists():
        deposit = json.loads(deposit_path.read_text(encoding='utf-8'))
    doi = deposit.get('doi') if isinstance(deposit, dict) else None

    doi_bib = f',\n  doi = {{{doi}}}' if doi else ''
    bib = f'''@misc{{liu2026auditingrules,
  author = {{Hongju Liu}},
  title = {{{TITLE}}},
  year = {{2026}},
  month = {{9}},
  note = {{TA-TR-2026-11, version 2.0, preprint}}{doi_bib}
}}
'''
    ris = f'''TY  - PREPRINT
AU  - Liu, Hongju
TI  - {TITLE}
PY  - 2026
DA  - 2026/09/21
M3  - TA-TR-2026-11, version 2.0
''' + (f'DO  - {doi}\n' if doi else '') + 'ER  - \n'
    csl = {
        'id': 'liu2026auditingrules',
        'type': 'article',
        'title': TITLE,
        'author': [{'family': 'Liu', 'given': 'Hongju'}],
        'issued': {'date-parts': [[2026, 9, 21]]},
        'version': VERSION,
        'genre': 'Preprint',
        'number': REPORT,
    }
    if doi:
        csl['DOI'] = doi
        csl['URL'] = 'https://doi.org/' + doi
    write(PUB / 'citation.bib', bib)
    write(PUB / 'citation.ris', ris)
    write(PUB / 'citation.csl.json', json.dumps(csl, ensure_ascii=False, indent=2) + '\n')

    sums = []
    for name in FILES:
        if name == 'SHA256SUMS.txt':
            continue
        data = (PUB / name).read_bytes()
        sums.append(f'{sha(data)}  {name}')
    write(PUB / 'SHA256SUMS.txt', '\n'.join(sums) + '\n')

    pdf = PUB / f'{STEM}-zh-v{VERSION}.pdf'
    extracted = subprocess.check_output(['pdftotext', str(pdf), '-'], text=True, errors='replace')
    pdfinfo = subprocess.check_output(['pdfinfo', str(pdf)], text=True, errors='replace')
    page_match = re.search(r'^Pages:\s+(\d+)', pdfinfo, re.M)
    forecast = json.loads((PUB / 'gpt-5.6-sol-prospective-forecast-v2.0.json').read_text(encoding='utf-8'))

    companions_ok = all(sha((PUB / name).read_bytes()) == digest for name, digest in COMPANION_SHA256.items())
    checks = {
        'source_markdown_preserved': sha((PUB / f'{STEM}-zh-v{VERSION}.md').read_bytes()) == SOURCE_SHA256,
        'references_preserved': '# 参考文献' in md and 'Luo' in md and 'Slocum' in md and 'Wu, A. J.' in md,
        'chinese_full_text_with_english_abstract': '## Abstract' in md and '## 摘要' in md and '# 14. 结论' in md,
        'valid_citation_metadata': all((PUB / x).stat().st_size > 50 for x in ('citation.bib', 'citation.ris', 'citation.csl.json')),
        'pdf_text_extractable': (
            REPORT in extracted and 'GPT-5.6 Sol' in extracted and '14.' in extracted
            and len(extracted) > 25000 and bool(page_match) and int(page_match.group(1)) >= 30
        ),
        'forecast_record_preserved': (
            sha((PUB / 'gpt-5.6-sol-prospective-forecast-v2.0.json').read_bytes()) == FORECAST_SHA256
            and forecast.get('forecaster_model') == 'GPT-5.6 Sol'
            and forecast.get('forecast_date') == '2026-09-21'
        ),
        'companion_experiments_preserved': companions_ok,
    }
    write(ROOT / 'format-checks.json', json.dumps(checks, ensure_ascii=False, indent=2) + '\n')

    if deposit_path.exists():
        d = json.loads(deposit_path.read_text(encoding='utf-8'))
        rows = []
        for name in sorted(FILES):
            data = (PUB / name).read_bytes()
            rows.append({'name': name, 'bytes': len(data), 'sha256': sha(data)})
        expected = {
            'record_id': d['record_id'],
            'doi': d['doi'],
            'title': TITLE,
            'report_number': REPORT,
            'version': VERSION,
            'file_count': len(rows),
            'files': rows,
        }
        raw = (json.dumps(expected, ensure_ascii=False, indent=2) + '\n').encode()
        (ROOT / 'EXPECTED-PUBLICATION.json').write_bytes(raw)
        visual = {
            'state': 'CONTENT_AND_RENDER_PIPELINE_REVIEW_PASS',
            'expected_manifest_sha256': sha(raw),
            'review_basis': [
                'local 41-page visual QA of the same v2.0 manuscript before external publication',
                'runner exact-source digest gate',
                'runner PDF text extraction, section-presence and >=30-page completeness gate',
                'exact package SHA-256 binding for manuscript, forecast, scripts and experiment results',
            ],
            'exact_runner_pdf_human_visual_review': False,
        }
        write(ROOT / 'visual-review.json', json.dumps(visual, ensure_ascii=False, indent=2) + '\n')

    print(json.dumps(checks, ensure_ascii=False, indent=2))
    if not all(value is True for value in checks.values()):
        raise SystemExit('format checks did not all pass: ' + repr(checks))


if __name__ == '__main__':
    main()
