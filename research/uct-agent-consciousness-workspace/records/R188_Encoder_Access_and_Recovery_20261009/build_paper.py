#!/usr/bin/env python3
"""Render the complete versioned working paper with a precise vector figure."""
from pathlib import Path
import subprocess
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from check_encoder_access import GRAPHS

ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
colors={'bipartite':(0,0,0,1,1,1),'prism':(0,1,0,1,0,1)}
positions={'bipartite':{0:(-1,1),1:(-1,0),2:(-1,-1),3:(1,1),4:(1,0),5:(1,-1)},
           'prism':{0:(-1.6,1),1:(-2.2,-.75),2:(-.9,-.75),3:(1.05,1),4:(.4,-.75),5:(1.7,-.75)}}
fig,axes=plt.subplots(1,2,figsize=(7.1,3.25))
for ax,(name,title) in zip(axes,[('bipartite','A  |  Bipartite contexts'),('prism','B  |  Prism contexts')]):
    pos=positions[name]
    for a,b in GRAPHS[name]:
        bad=colors[name][a]==colors[name][b]
        ax.plot([pos[a][0],pos[b][0]],[pos[a][1],pos[b][1]],
                color='#C65B45' if bad else '#ADBAC8',lw=2.1 if bad else 1.3,
                ls='--' if bad else '-',zorder=1)
    for t,(x,y) in pos.items():
        ax.scatter([x],[y],s=520,c=['#143A52' if colors[name][t]==0 else '#4B8C99'],
                   edgecolors='white',linewidths=1.4,zorder=3)
        ax.text(x,y,str(t),ha='center',va='center',color='white',fontsize=11,fontweight='bold',zorder=4)
    ax.set_title(title,loc='left',fontsize=11,fontweight='bold',color='#143A52',pad=12)
    ax.set_aspect('equal');ax.axis('off');ax.set_ylim(-1.5,1.5)
    ax.set_xlim((-1.8,1.8) if name=='bipartite' else (-2.65,2.15))
    ax.text(.5,-.025,'9 of 9 pairs distinguished  |  success 1' if name=='bipartite'
            else '7 of 9 pairs distinguished  |  success 8/9',transform=ax.transAxes,
            ha='center',fontsize=9,color='#143A52')
fig.subplots_adjust(wspace=.3,left=.04,right=.99,top=.87,bottom=.16)
fig.text(.5,.025,'Colors are one-bit source codes. Dashed pairs remain ambiguous. Edges are candidate contexts, not physical wires.',
         ha='center',fontsize=7.8,color='#4A5660')
fig.savefig(FIG/'matched_architectures.pdf',bbox_inches='tight')
fig.savefig(FIG/'matched_architectures.png',dpi=180,bbox_inches='tight')
plt.close(fig)

source=(ROOT/'RESEARCH_NOTE.md').read_text()
body=source[source.index('## Abstract'):]
body=re.sub(r'https?://[^\s<>]+',lambda m:'<'+m.group(0).rstrip('.')+'>'+('.' if m.group(0).endswith('.') else ''),body)
body=body.replace('### 5.2 Proposition 2: exact one-bit separation',
    '![Matched candidate-context architectures with optimal binary source codes. The prism forces two ambiguous contexts.](figures/matched_architectures.pdf){width=98%}\n\n### 5.2 Proposition 2: exact one-bit separation')
work=ROOT/'pdf_build';work.mkdir(exist_ok=True)
(work/'paper_source.md').write_text(body)
header=r'''\usepackage{amsmath,amssymb}
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
\titlespacing*{\subsection}{0pt}{1.8ex plus .7ex}{.8ex}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\color{mutedblue}Behavioral recovery and organizational change}
\fancyhead[R]{\small\color{mutedblue}Research working paper}
\fancyfoot[L]{\small\color{mutedblue}R188-CER-20261009 | v0.1.0}
\fancyfoot[R]{\small\color{mutedblue}\thepage}
\renewcommand{\headrulewidth}{.3pt}
\setlength{\headheight}{14pt}
\AtBeginEnvironment{longtable}{\small}
\setlength{\emergencystretch}{2em}
\widowpenalty=10000\clubpenalty=10000
'''
(work/'header.tex').write_text(header)
out=ROOT/'When_Behavioral_Recovery_Conceals_Organizational_Change_v0.1.0.pdf'
cmd=['pandoc',str(work/'paper_source.md'),'-f','markdown+tex_math_single_backslash',
     '--pdf-engine=xelatex','--resource-path='+str(ROOT),'-o',str(out),
     '-V','documentclass=article','-V','fontsize=10pt','-V','geometry:margin=22mm',
     '-V','mainfont=DejaVu Serif','-V','sansfont=DejaVu Sans','-V','monofont=DejaVu Sans Mono',
     '-V','linestretch=1.08','-V','colorlinks=true','-V','linkcolor=inkblue','-V','urlcolor=inkblue',
     '--include-in-header='+str(work/'header.tex'),
     '-M','title=When Behavioral Recovery Conceals Organizational Change',
     '-M','subtitle=Intervention contracts, compensation, and the information available to an encoder',
     '-M','author=Hongju Liu | Independent researcher, Shenzhen, China',
     '-M','date=9 October 2026 | CER-RESULT-v0.1.0 | Research working paper']
run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
(work/'pandoc_stdout.log').write_text(run.stdout)
(work/'pandoc_stderr.log').write_text(run.stderr)
if run.returncode:raise RuntimeError(run.stderr)
print(out)
if run.stderr:print(run.stderr)
