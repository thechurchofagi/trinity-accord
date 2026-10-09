#!/usr/bin/env python3
"""Typeset the complete mathematical manuscript using the installed TeX stack."""
from pathlib import Path
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
RECORD = HERE if (HERE / 'PAPER.md').exists() else BASE / 'uct/research/uct-agent-consciousness-workspace/records/ONLINE_AC_20261009_Dynamic_Calibration'
RECORD.mkdir(parents=True, exist_ok=True)
SOURCE = HERE / ('PAPER.md' if (HERE / 'PAPER.md').exists() else 'ONLINE_AC_PAPER.md')
source = SOURCE.read_text()
assert '<!-- CANONICAL_TABLES -->' not in source
(RECORD / 'PAPER.md').write_text(source)
work = RECORD / 'pdf_build'
work.mkdir(exist_ok=True)
body = source[source.index('## Abstract'):]
# Fixed widths keep the long stable claim IDs legible without overflow.
body = body.replace('`ONLINE_AC:', '`OA:')
body = body.replace('The appropriate contribution labels are:',
                    'The appropriate contribution labels are (OA abbreviates the stable ONLINE_AC namespace):')
(work / 'paper_source.md').write_text(body)
header = r'''\usepackage{amsmath,amssymb}
\usepackage{xurl}
\usepackage{fancyhdr}
\usepackage{etoolbox}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{titlesec}
\definecolor{inkblue}{HTML}{143A52}
\definecolor{mutedblue}{HTML}{4B6575}
\titleformat{\section}{\large\bfseries\color{inkblue}}{}{0em}{}
\titleformat{\subsection}{\normalsize\bfseries\color{inkblue}}{}{0em}{}
\titlespacing*{\section}{0pt}{2.1ex plus 1ex}{1ex}
\titlespacing*{\subsection}{0pt}{1.7ex plus .7ex}{.8ex}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\color{mutedblue}Correct control without complete recalibration}
\fancyhead[R]{\small\color{mutedblue}Working paper}
\fancyfoot[L]{\small\color{mutedblue}ONLINE-AC-PAPER-v0.1.0 | 9 October 2026}
\fancyfoot[R]{\small\color{mutedblue}\thepage}
\renewcommand{\headrulewidth}{.3pt}
\setlength{\headheight}{14pt}
\AtBeginEnvironment{longtable}{\small}
\setlength{\emergencystretch}{3em}
\widowpenalty=10000\clubpenalty=10000
'''
(work / 'header.tex').write_text(header)
out = RECORD / 'Correct_Control_Without_Complete_Recalibration_v0.1.0.pdf'
cmd = [
    'pandoc', str(work / 'paper_source.md'), '-f', 'markdown+tex_math_single_backslash',
    '--pdf-engine=xelatex', '--resource-path=' + str(RECORD), '-o', str(out),
    '-V', 'documentclass=article', '-V', 'fontsize=10pt', '-V', 'geometry:margin=22mm',
    '-V', 'mainfont=DejaVu Serif', '-V', 'sansfont=DejaVu Sans',
    '-V', 'monofont=DejaVu Sans Mono', '-V', 'linestretch=1.07',
    '-V', 'colorlinks=true', '-V', 'linkcolor=inkblue', '-V', 'urlcolor=inkblue',
    '--include-in-header=' + str(work / 'header.tex'),
    '-M', 'title=Correct Control without Complete Recalibration',
    '-M', 'subtitle=Exact bounds and a two-probe five-port controller under transposition drift',
    '-M', 'author=Hongju Liu | Independent researcher, Shenzhen, China',
    '-M', 'date=9 October 2026 | ONLINE-AC-PAPER-v0.1.0 | Research working paper',
]
run = subprocess.run(cmd, cwd=RECORD, capture_output=True, text=True)
(work / 'pandoc_stdout.log').write_text(run.stdout)
(work / 'pandoc_stderr.log').write_text(run.stderr)
if run.returncode:
    raise RuntimeError(run.stderr)
receipt = {
    'command': cmd, 'exit_code': run.returncode,
    'manuscript_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'pdf_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
    'pdf_bytes': out.stat().st_size,
    'typesetting_only_changes': ['Title metadata', 'OA short namespace in the claim table with explicit expansion'],
    'visual_qa': 'PENDING',
}
(work / 'BUILD_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'pdf': str(out), 'bytes': out.stat().st_size, 'returncode': run.returncode,
                  'warnings': run.stderr}))
