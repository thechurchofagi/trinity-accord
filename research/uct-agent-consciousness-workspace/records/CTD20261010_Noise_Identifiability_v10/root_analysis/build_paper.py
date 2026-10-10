"""Build the English release manuscript with Pandoc and XeLaTeX."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parents[1] / 'manuscript'
stem = 'noise-identifiability-bodily-judgments-v1.0.0'
subprocess.run(['pandoc', stem+'.md', '--standalone', '--from=markdown',
                '--to=latex', '--include-in-header=preamble.tex',
                '-V', 'mainfont=Latin Modern Roman',
                '-V', 'sansfont=Latin Modern Sans',
                '-V', 'monofont=DejaVu Sans Mono',
                '-V', 'monofontoptions=Scale=0.82',
                '-V', 'documentclass=article',
                '-o', stem+'.tex'], cwd=base, check=True)
for _ in range(2):
    subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error',
                    '-file-line-error', stem+'.tex'], cwd=base, check=True,
                   stdout=subprocess.DEVNULL)
print(base / (stem+'.pdf'))
