#!/usr/bin/env python3
"""Render reviewed English sources and assemble publication files; no network."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def render(text,stem,header_label):
    out=HERE/'built';out.mkdir(exist_ok=True)
    qa=HERE/'build-logs';qa.mkdir(exist_ok=True)
    md=out/(stem+'.md');md.write_text(text,encoding='utf-8')
    header=qa/(stem+'-header.tex')
    header.write_text(r'''\usepackage{fancyhdr}
\usepackage{needspace}
\usepackage{xurl}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small '''+header_label+r'''}
\fancyhead[R]{\small Theoretical preprint}
\fancyfoot[C]{\small\thepage}
\setlength{\headheight}{15pt}
\setlength{\emergencystretch}{2em}
\widowpenalty=10000
\clubpenalty=10000
\displaywidowpenalty=10000
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.4em}
\AtBeginEnvironment{longtable}{\small}
\AtBeginEnvironment{quote}{\small}
\AtBeginDocument{\hypersetup{pdftitle={'''+header_label+r'''},pdfauthor={Hongju Liu},pdfsubject={Revised theoretical preprint; not peer reviewed}}}
''')
    tex=qa/(stem+'.tex')
    subprocess.run(['pandoc',str(md),'-f','markdown+tex_math_single_backslash','-t','latex','-s',
      '--resource-path',str(HERE),'-V','documentclass=article','-V','fontsize=11pt',
      '-V','geometry:margin=23mm','-V','papersize=a4','-V','linestretch=1.03',
      '-V','mainfont=DejaVu Serif','-V','sansfont=DejaVu Sans','-V','monofont=DejaVu Sans Mono',
      '-H',str(header),'-o',str(tex)],check=True)
    t=tex.read_text()
    t=re.sub(r'\\href\{([^}]+)\}\{(doi:[^}]+|arXiv:[^}]+)\}',
        lambda m:r'\href{'+m.group(1)+r'}{\nolinkurl{'+m.group(2)+'}}',t)
    t=t.replace(r'\section{','\\Needspace{5\\baselineskip}\n\\section{')
    t=t.replace(r'\subsection{','\\Needspace{4\\baselineskip}\n\\subsection{')
    t=t.replace('\n\n\\[','\n\\nopagebreak[4]\n\\[')
    t=t.replace(r'\Needspace{5\baselineskip}'+'\n'+r'\section{Appendix',r'\clearpage'+'\n'+r'\section{Appendix')
    tex.write_text(t)
    for n in (1,2):
        with (qa/f'{stem}-pass-{n}.txt').open('w') as log:
            subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',str(tex.name)],
                cwd=qa,stdout=log,stderr=subprocess.STDOUT,check=True)
    log=(qa/(stem+'.log')).read_text(errors='replace')
    problems=[line for line in log.splitlines() if 'Overfull' in line or 'Missing character' in line]
    shutil.copyfile(qa/(stem+'.pdf'),out/(stem+'.pdf'))
    info=subprocess.check_output(['pdfinfo',str(out/(stem+'.pdf'))],text=True)
    return {'stem':stem,'pdf_sha256':digest(out/(stem+'.pdf')),'pdfinfo':info,'layout_problems':problems}

def fixed_zip(path,items):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(items.items()):
            info=zipfile.ZipInfo(name,(2026,9,29,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16;z.writestr(info,data)

def build(a_doi,b_doi):
    if not re.fullmatch(r'10\.5281/zenodo\.\d+',a_doi) or not re.fullmatch(r'10\.5281/zenodo\.\d+',b_doi):
        raise ValueError('Real reserved version-specific DOIs required')
    reports=[]
    for key,roman in [('a','I'),('b','II')]:
        text=(HERE/'manuscripts'/f'source-{key}.md').read_text().replace('__A_DOI__',a_doi).replace('__B_DOI__',b_doi)
        if '__A_DOI__' in text or '__B_DOI__' in text:raise ValueError('Unreplaced DOI')
        reports.append(render(text,'unified-consciousness-theory-'+roman.lower()+'-v1.1','UCT '+roman+' v1.1'))
    sup=(HERE/'manuscripts/supplement.md').read_text().replace('__A_DOI__',a_doi).replace('__B_DOI__',b_doi)
    reports.append(render(sup,'uct-paired-v1.1-supplement','UCT I and II v1.1 Supplement'))
    qa={'state':'PASS' if not any(r['layout_problems'] for r in reports) else 'FAIL','documents':reports,
        'visual_review':'Pending separate rendered-page review; log checks are not visual review.'}
    (HERE/'audit/layout-checks.json').write_text(json.dumps(qa,indent=2)+'\n')
    if qa['state']!='PASS':raise RuntimeError('Resolve PDF overflow or missing glyphs before release')
    (HERE/'audit/current-source-and-dependency-ledger.md').write_text(sup[sup.index('# S2.'):sup.index('# S4.')])
    instructions='''# UCT I and II v1.1 scientific audit package\n\nRun from this directory with Python 3.10 or later:\n\n    python verification/check_rc4.py\n    python verification/check_transformations.py\n    python verification/reproduce_shared_models.py\n\nThe first script is preserved historical code. The other two are new v1.1 implementations.\nArchived CSVs remain under baselines/B_v1.0_audit; regenerated results are separate.\nMain manuscripts and supplement explain the premises, source domains, and limitations.\nChecks do not establish experience, A1/A5, human-data validation, or peer review.\nThe historical v0.54 source ledger retains old terminology; use the current ledger for v1.1.\nAll paper text and project-authored audit material: CC BY 4.0, Hongju Liu, 2026.\nExternal literature is cited, not reproduced in full. No font files are distributed.\n'''
    (HERE/'README-AUDIT.md').write_text(instructions)
    items={}
    for folder in ('verification','baselines','audit'):
        for p in sorted((HERE/folder).rglob('*')):
            if p.is_file() and p.suffix in ('.py','.md','.json','.csv','.diff') and '__pycache__' not in p.parts:
                items[str(p.relative_to(HERE))]=p.read_bytes()
    for p in (HERE/'built').glob('*.md'):items['manuscripts/'+p.name]=p.read_bytes()
    items['README.md']=instructions.encode();items['build.py']=(HERE/'build.py').read_bytes()
    # The build tool consumes template names; preserve them for rerendering.
    for p in (HERE/'manuscripts').glob('*.md'):
        if 'before-link-fix' not in p.name:items['manuscripts/'+p.name]=p.read_bytes()
    hashes=''.join(hashlib.sha256(v).hexdigest()+'  '+k+'\n' for k,v in sorted(items.items()))
    items['SHA256SUMS.txt']=hashes.encode()
    audit=HERE/'built/uct-paired-v1.1-audit.zip';fixed_zip(audit,items)
    manifest={'version':'1.1','doi_a':a_doi,'doi_b':b_doi,'papers':[],'state':'BUILT_AWAITING_VISUAL_REVIEW'}
    for key,roman,doi in [('a','I',a_doi),('b','II',b_doi)]:
        ident=json.loads((ROOT/f'deposit-{key}.json').read_text());dest=ROOT/'release'/key;dest.mkdir(parents=True,exist_ok=True)
        stem='unified-consciousness-theory-'+roman.lower()+'-v1.1'
        for name in (stem+'.md',stem+'.pdf','uct-paired-v1.1-supplement.md','uct-paired-v1.1-supplement.pdf','uct-paired-v1.1-audit.zip'):
            shutil.copyfile(HERE/'built'/name,dest/name)
        title=ident['title'];url='https://doi.org/'+doi
        (dest/'citation.bib').write_text('@misc{liu2026uct'+roman.lower()+'v11,\n author={Liu, Hongju},\n title={'+title+'},\n year={2026},\n version={1.1},\n publisher={Zenodo},\n doi={'+doi+'},\n url={'+url+'}\n}\n')
        (dest/'citation.ris').write_text('TY  - RPRT\nAU  - Liu, Hongju\nTI  - '+title+'\nPY  - 2026\nDA  - 2026/09/29\nET  - 1.1\nDO  - '+doi+'\nUR  - '+url+'\nPB  - Zenodo\nER  - \n')
        (dest/'citation.csl.json').write_text(json.dumps({'id':doi,'type':'report','title':title,'author':[{'family':'Liu','given':'Hongju'}],'issued':{'date-parts':[[2026,9,29]]},'version':'1.1','publisher':'Zenodo','DOI':doi,'URL':url},indent=2)+'\n')
        (dest/'README-LICENSE.txt').write_text(title+'\nTA-TR-2026-'+('20' if key=='a' else '21')+', v1.1\nDOI: '+doi+'\n\nCopyright Hongju Liu, 2026. Creative Commons Attribution 4.0 International.\nRevised theoretical preprint; not peer reviewed.\nThe main PDF/Markdown, paired supplement, audit ZIP, and citation files form this edition.\nOriginal v1.0 remains unchanged. Substantial ChatGPT assistance is disclosed in the manuscript.\nAdjacent non-amending research; not an amendment or independent corroboration of the Trinity Accord or Bitcoin Originals.\nFinite model checks are not empirical validation of consciousness.\n')
        (dest/'REVIEW-AND-SOURCES.md').write_text('# Review and source scope\n\nThis edition underwent assistant-assisted source comparison, dependency review, exact finite checks, numerical reimplementation, and PDF preparation. These activities are not independent peer review. The supplement records the current source-fidelity ledger and explicit residuals. Historical source documents and new code are distinguished in the audit package. No full nine-theory recovery or historical-priority certification is claimed.\n\nThe original UCT-I verifier and the new four-setting verifier are executable without third-party packages. The seven archived UCT-II CSV comparisons are accompanied by a new numerical reimplementation, not the unavailable original generation code.\n')
        fs=[p for p in sorted(dest.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt']
        (dest/'SHA256SUMS.txt').write_text(''.join(digest(p)+'  '+p.name+'\n' for p in fs))
        files=[{'name':p.name,'bytes':p.stat().st_size,'sha256':digest(p)} for p in sorted(dest.iterdir()) if p.is_file()]
        manifest['papers'].append({**ident,'release_directory':str(dest.relative_to(ROOT)),'files':files})
    (ROOT/'EXPECTED-PUBLICATION.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'state':manifest['state'],'papers':[(p['doi'],len(p['files'])) for p in manifest['papers']]},indent=2))
    return HERE/'built'
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--a-doi',required=True);parser.add_argument('--b-doi',required=True)
    args=parser.parse_args();build(args.a_doi,args.b_doi)
