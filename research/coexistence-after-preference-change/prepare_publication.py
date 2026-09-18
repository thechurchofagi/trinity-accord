#!/usr/bin/env python3
"""Rebuild only the reviewed sixth paper, fail closed on every expected byte."""
from pathlib import Path, PurePosixPath
import argparse, base64, hashlib, json, lzma, re, shutil, subprocess, sys
RID=22830239
DOI='10.5281/zenodo.22830239'
TITLE='Coexistence after Preference Change: Reciprocal Standing and the Limits of Self-Validating Assent'
STEM='coexistence-after-preference-change'
BASE='/research/'+STEM+'/'
HOST='https://www.trinityaccord.org'
def digest(data):return hashlib.sha256(data).hexdigest()
def check_files(directory,expected):
    files=expected['files'];names=[f['name'] for f in files]
    if expected['record_id']!=RID or expected['doi']!=DOI or expected['title']!=TITLE or expected['version']!='2.1':raise RuntimeError('Publication identity mismatch')
    if len(names)!=12 or len(set(names))!=12:raise RuntimeError('Expected twelve unique assets')
    for f in files:
        if Path(f['name']).name!=f['name'] or not re.fullmatch('[0-9a-f]{64}',f['sha256']):raise RuntimeError('Invalid asset manifest')
        b=(directory/f['name']).read_bytes()
        if len(b)!=f['bytes'] or digest(b)!=f['sha256']:raise RuntimeError('Reviewed asset mismatch: '+f['name']+' actual='+digest(b))
    return files

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    here=Path(__file__).resolve().parent;repo=here.parents[1];transfer=here/'source-transfer'
    manifest=json.loads((transfer/'SOURCE-MANIFEST.json').read_text());encoded=[]
    for item in manifest['parts']:
        name=item['name']
        if not re.fullmatch(r'part-0[1-9]\.b64',name):raise RuntimeError('Unsafe transfer name')
        b=(transfer/name).read_bytes()
        if digest(b)!=item['sha256']:raise RuntimeError('Transfer part hash mismatch: '+name+' actual='+digest(b))
        encoded.append(b.strip())
    packed=base64.b64decode(b''.join(encoded),validate=True)
    if digest(packed)!=manifest['source_xz_sha256']:raise RuntimeError('Source packet hash mismatch')
    raw=lzma.decompress(packed)
    if len(raw)!=manifest['json_bytes'] or digest(raw)!=manifest['json_sha256']:raise RuntimeError('Source JSON mismatch')
    inputs=json.loads(raw);expected_sources={f['name']:f for f in manifest['files']}
    if set(inputs)!=set(expected_sources):raise RuntimeError('Source inventory mismatch')
    if a.source.exists() or a.output.exists():raise RuntimeError('Fresh source/output directories required')
    for name,content in inputs.items():
        rel=PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or not isinstance(content,str):raise RuntimeError('Unsafe source path/content')
        b=content.encode('utf-8');e=expected_sources[name]
        if len(b)!=e['bytes'] or digest(b)!=e['sha256']:raise RuntimeError('Source file mismatch: '+name)
        dest=a.source/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
    subprocess.run([sys.executable,str(a.source/'tools/build_flat.py'),str(a.output)],check=True)
    expected=json.loads((here/'EXPECTED-PUBLICATION.json').read_text());files=check_files(a.output,expected)
    if {x.name for x in a.output.iterdir()}!={x['name'] for x in files}:raise RuntimeError('Unexpected output assets')
    for f in files:shutil.copyfile(a.output/f['name'],here/f['name'])
    md=json.loads((a.source/'MANUSCRIPT_METADATA.json').read_text())
    en=(a.output/(STEM+'-v2.1.md')).read_text();zh=(a.output/(STEM+'-zh-v2.1.md')).read_text()
    abstract=en.split('### Abstract\n\n',1)[1].split('\n\n**Keywords:',1)[0]
    if abstract!=md['abstract']:raise RuntimeError('Abstract metadata mismatch')
    zhabstract=zh.split('### 摘要\n\n',1)[1].split('\n\n**关键词',1)[0]
    for lang,suffix,page,ab in [('en','','index.md',abstract),('zh','-zh','zh.md',zhabstract)]:
        pdf=STEM+suffix+'-v2.1.pdf';route=BASE+('zh.html' if lang=='zh' else '')
        front={'layout':'default','reading_page':True,'scholarly_article':True,'title':TITLE if lang=='en' else '偏好改变之后的共存：相互主体地位与同意的自我正当化边界','description':'TA-TR-2026-06 v2.1. Philosophical preprint; not peer reviewed; non-amending.','permalink':route,'citation_title':TITLE,'citation_author':'Hongju Liu','citation_publication_date':'2026/09/18','citation_doi':DOI,'citation_pdf_url':HOST+BASE+pdf,'citation_technical_report_institution':'Independent research','citation_technical_report_number':'TA-TR-2026-06','citation_language':lang,'citation_keywords':'human-AI coexistence; preference formation; consent; reciprocal standing; thought experiments','article_identifier':'TA-TR-2026-06','article_version':'2.1','article_date':'2026-09-18','article_license':'CC BY 4.0; third-party rights retained','article_pdf':HOST+BASE+pdf,'article_record_url':f'https://zenodo.org/records/{RID}','article_bibtex':HOST+BASE+'citation.bib','article_metadata':HOST+BASE+'publication-record.json','article_abstract':ab}
        header='---\n'+''.join(k+': '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in front.items())+'---\n\n'
        nav=f'[Research index](/research/) · [English]({BASE}) · [中文全文]({BASE}zh.html) · [PDF]({BASE}{pdf}) · [DOI](https://doi.org/{DOI})\n\n'
        include='{% include_relative '+STEM+suffix+'-v2.1.md %}\n\n'
        boundary='## Publication and citation boundary\n\nEnglish and Chinese are one philosophical study, not independent papers. The text is noncanonical and not peer reviewed. Substantial AI contributions and human publication responsibility are disclosed. The DOI identifies this preprint; it does not certify novelty, safety, peer review or Google Scholar indexing. Earlier DOIs and the Bitcoin Originals are unchanged.\n\n[Publication receipt](publication-record.json) · [Source and revision supplement](research-supplement-v2.1.zip) · [BibTeX](citation.bib) · [RIS](citation.ris) · [CSL-JSON](citation.csl.json)\n'
        (here/page).write_text(header+nav+include+boundary)
    (here/'PUBLICATION-REVIEW-ZH.md').write_bytes((a.source/'documentation/Publication_Review_ZH.md').read_bytes())
    index=repo/'research/index.md';s=index.read_text()
    if '## Coexistence after Preference Change' not in s:
        section=f'''## Coexistence after Preference Change
{{: #coexistence-after-preference-change }}

### {TITLE}

TA-TR-2026-06 · Version 2.1 · 18 September 2026. Hongju Liu, with substantial research, reasoning, drafting and translation by GPT-6 Astra Pro under human direction.

A philosophical preprint using paired thought experiments to distinguish the permissibility of a prior transformation, the standing and choices of the resulting subject, and justification of an ongoing relation. It considers human and possible artificial interests reciprocally; it does not assert present AI consciousness, a superintelligence deadline or demonstrated safety efficacy.

**Status:** Published open-access preprint; not peer reviewed; non-amending. Twelve deposited assets passed unauthenticated full-file SHA-256 readback. The English manuscript and complete Chinese translation are one study. Version 2.1 is its first public edition, not a replacement version of any earlier paper DOI.

- [DOI: {DOI}](https://doi.org/{DOI}) · [Zenodo record](https://zenodo.org/records/{RID})
- [English full text]({BASE}) · [中文全文]({BASE}zh.html)
- [English PDF]({BASE}{STEM}-v2.1.pdf) · [中文 PDF]({BASE}{STEM}-zh-v2.1.pdf)
- [Publication receipt]({BASE}publication-record.json) · [Substantive review]({BASE}PUBLICATION-REVIEW-ZH.md)
- [Sources and revision supplement]({BASE}research-supplement-v2.1.zip) · [BibTeX]({BASE}citation.bib) · [RIS]({BASE}citation.ris)

'''
        if '## Citation boundary' not in s:raise RuntimeError('Research index insertion point unavailable')
        s=s.replace('## Citation boundary',section+'## Citation boundary',1)
        needle='  - id: "citation-boundary"'
        if needle in s:s=s.replace(needle,'  - id: "coexistence-after-preference-change"\n    title: "Coexistence after Preference Change"\n'+needle,1)
        index.write_text(s)
    report={'status':'REVIEWED_BYTES_REPRODUCED','record_id':RID,'doi':DOI,'source_json_sha256':digest(raw),'source_files':len(inputs),'file_count':len(files),'files':files,'pdf_pages':{},'claim':'Byte reproduction and format checks, not independent philosophical validation.'}
    for suffix,pages in [('',16),('-zh',14)]:
        path=here/(STEM+suffix+'-v2.1.pdf');info=subprocess.check_output(['pdfinfo',str(path)],text=True)
        actual=int(re.search(r'^Pages:\s*(\d+)',info,re.M).group(1))
        if actual!=pages:raise RuntimeError('Reviewed PDF pagination changed')
        report['pdf_pages'][path.name]=actual
        text=subprocess.check_output(['pdftotext',str(path),'-'],text=True)
        if DOI not in text or '\ufffd' in text:raise RuntimeError('PDF text check failed')
    (here/'format-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print('SOURCE_AND_TWELVE_REVIEWED_ASSETS_PASS')
if __name__=='__main__':main()
