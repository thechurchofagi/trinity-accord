#!/usr/bin/env python3
"""Build TA-TR-2026-04 from reviewed source bytes; no network or credentials.
Publication rendering changes only status/front matter and disclosure updates.
Uses the prior TA-TR-2026-03 ReportLab build pattern with embedded CJK glyphs.
"""
from __future__ import annotations
import argparse, base64, difflib, hashlib, html, json, lzma, re, zipfile
from functools import partial
from pathlib import Path
import reportlab
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
TITLE='Beyond Guaranteed Control: An Ex Ante Proposal for Human–Superintelligence Coexistence under Radical Capability Asymmetry'
DOI='10.5281/zenodo.22804542'
RID=22804542
REPORT='TA-TR-2026-04'
STEM='beyond-guaranteed-control'
FONT=Path('/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf')
FONT_SHA='705ec2dba81eaee1208e4ed5d3ff23ab259292e8e0e163ea3de297ef1317007a'
SITE='https://www.trinityaccord.org/research/beyond-guaranteed-control/'
NOTE='''# Publication preparation and authority boundary\n\nTA-TR-2026-04, version 1.0, 17 September 2026. DOI: 10.5281/zenodo.22804542.\n\nThe user explicitly requested format checking, independent DOI publication through the existing GitHub workflow, and documentation in the research directory. This is publication authorization, not evidence of a separate final line-by-line or claim-specific human review. Substantive AI contribution remains disclosed in both manuscripts.\n\nThe seven retained pre-publication text files are recovered losslessly from the user's reviewed v1.0 package. Their original status statements describe preparation before the subsequent publication request. The current manuscripts update only front matter, publication status and corresponding disclosure sentences. Scholarly sections 1–11, abstract, tables and all 40 references remain unchanged. The supplement contains exact pre-publication text sources and publication-only diffs; it does not claim to contain the entire earlier binary package.\n\nPDFs are new, deterministic publication renderings, not byte-identical copies of the pre-publication Writer exports. CJK glyphs are subset-embedded; no standalone fonts are distributed. ReportLab 4.4.9 and the specified Arphic font checksum define the renderer inputs.\n\nA reserved DOI is not a published record. Actual publication status and exact-byte public readback are recorded separately in publication-record.json after the authorized workflow succeeds. The existing three paper DOIs and Bitcoin Originals remain unchanged. This fourth paper is non-amending analysis, not a fourth Original or an exclusive interpretation.\n\nGoogle Scholar checks concern searchable PDF, file size, first-page title/author, complete references, freely available full text and Highwire metadata. They neither certify Google Scholar inclusion nor constitute peer review or independent research validation.\n\nScope of rights: the new report and supporting documentation are offered under CC BY 4.0. Quoted historical/third-party material remains attributable to its source and is not relicensed by this notice. No journal submission, institutional endorsement, universal originality finding, ASI deadline or safety guarantee is asserted.\n'''
def sha(b:bytes)->str: return hashlib.sha256(b).hexdigest()
def jdump(obj)->str: return json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
def write(p:Path,s:str)->None: p.write_text(s,encoding='utf-8',newline='\n')
def load_sources(root:Path)->tuple[dict,dict]:
    d=root/'source-transfer'; m=json.loads((d/'SOURCE-MANIFEST.json').read_text())
    parts=[]
    for r in m['parts']:
        b=(d/r['name']).read_bytes()
        if len(b)!=r['bytes'] or sha(b)!=r['sha256']: raise ValueError('Source part mismatch: '+r['name'])
        parts.append(b)
    raw=lzma.decompress(base64.b64decode(b''.join(parts),validate=True))
    if sha(raw)!=m['decoded_json_sha256'] or len(raw)!=m['decoded_json_bytes']: raise ValueError('Source payload mismatch')
    files=json.loads(raw)
    if set(files)!={r['name'] for r in m['files']}: raise ValueError('Unexpected source set')
    for r in m['files']:
        if Path(r['name']).name!=r['name']: raise ValueError('Unsafe path')
        b=files[r['name']].encode()
        if len(b)!=r['bytes'] or sha(b)!=r['sha256']: raise ValueError('Source file mismatch: '+r['name'])
    return files,m

def replace_once(s,old,new):
    if s.count(old)!=1: raise ValueError('Publication replacement count: '+old[:70])
    return s.replace(old,new,1)

def publication_text(s:str,lang:str)->str:
    if lang=='en':
        replacements=[
          ('Position paper and conceptual analysis · Consolidated manuscript v1.0 · 17 September 2026\nNot peer reviewed · Not publicly deposited',
           f'Position paper and conceptual analysis · {REPORT} · Version 1.0 · 17 September 2026\nOpen-access preprint · Not peer reviewed\nDOI: {DOI}'),
          ("The preparation record does not yet contain Liu's claim-specific endorsement of this exact final version or authorization for public submission. Completing the manuscript does not manufacture either act.",
           'After the consolidated revision, Liu explicitly authorized DOI publication following format checks. This authorization does not establish a separate final line-by-line or claim-specific human review, and none is claimed.'),
          ('The original v0.1, historical inscriptions, existing deposited studies, and website remain unchanged. No new DOI, journal submission, or public deposit was created in preparing this version.',
           f'The original v0.1, historical inscriptions and existing deposited studies remain unchanged. This separate fourth research paper is prepared for its independently authorized Zenodo deposit under DOI {DOI}, with publication and citation records added to the research directory. No journal submission is claimed.')]
    else:
        replacements=[
          ('立场论文与概念分析 · 集中修订定稿 v1.0 · 2026年9月17日\n未经同行评审 · 尚未公开发布',
           f'立场论文与概念分析 · {REPORT} · 版本1.0 · 2026年9月17日\n开放获取预印本 · 未经同行评审\nDOI: {DOI}'),
          ('制作记录尚未包含刘烘炬对这一确切定稿逐项主张的认可，也未包含公开提交授权。稿件完成不会制造这两种行为。',
           '集中修订后，刘烘炬明确授权在格式检查后进行DOI发布。这项授权不等于另外完成了最终逐行或逐项主张的人类审阅，本文不作此声称。'),
          ('原v0.1、历史铭文、既有入库研究及网站保持不变。本次制作没有创建新DOI、提交期刊或公开入库。',
           f'原v0.1、历史铭文及既有入库研究保持不变。这是独立的第四篇研究论文，依据另行明确授权准备以DOI {DOI} 在Zenodo入库，并在研究目录增列发布与引用记录。本文不声称已提交期刊。')]
    old=s
    for a,b in replacements: s=replace_once(s,a,b)
    decl='## Declarations' if lang=='en' else '## 声明'
    ref='## References' if lang=='en' else '## 参考文献'
    if old.split('## 1.',1)[1].split(decl)[0]!=s.split('## 1.',1)[1].split(decl)[0]: raise ValueError('Scholarly body modified')
    if old.split(ref,1)[1]!=s.split(ref,1)[1]: raise ValueError('References modified')
    ab='### Abstract' if lang=='en' else '### 摘要'
    if old.split(ab,1)[1].split('## 1.')[0]!=s.split(ab,1)[1].split('## 1.')[0]: raise ValueError('Abstract modified')
    return s

CJK=re.compile(r'([\u2e80-\u9fff\uf900-\ufaff\uff00-\uffef]+)')
def inline(s:str)->str:
    s=html.escape(s,quote=False)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)',lambda m:'<a href="'+html.escape(html.unescape(m[2]),quote=True)+'">'+m[1]+'</a>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
    s=re.sub(r'`([^`]+)`',r'\1',s)
    return CJK.sub(r'<font name="CN">\1</font>',s)
class Report(SimpleDocTemplate):
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and hasattr(f,'bookmark'):
            self.canv.bookmarkPage(f.bookmark); self.canv.addOutlineEntry(f.getPlainText(),f.bookmark,f.level,False)
def page(c,d):
    c.saveState();c.setFont('Times-Roman',8);c.setFillColor(colors.HexColor('#555555'))
    if d.page>1:
        c.drawString(54,A4[1]-30,'Beyond Guaranteed Control');c.drawRightString(A4[0]-54,A4[1]-30,REPORT+' | v1.0')
    c.drawString(54,27,DOI+' | Open-access preprint');c.drawRightString(A4[0]-54,27,str(d.page));c.restoreState()
def pdf_build(s:str,target:Path,lang:str)->None:
    if reportlab.Version!='4.4.9': raise ValueError('Requires reportlab==4.4.9')
    if not FONT.exists() or sha(FONT.read_bytes())!=FONT_SHA: raise ValueError('Embedded CJK font input mismatch')
    if 'CN' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('CN',str(FONT)))
        pdfmetrics.registerFontFamily('CN',normal='CN',bold='CN',italic='CN',boldItalic='CN')
    rl_config.invariant=1
    body=ParagraphStyle('body',fontName='Times-Roman',fontSize=10.5 if lang=='en' else 10.4,leading=14.0 if lang=='en' else 16,alignment=TA_JUSTIFY,spaceAfter=7,allowWidows=0,allowOrphans=0,wordWrap='CJK' if lang=='zh' else None)
    styles={
      'body':body,'title':ParagraphStyle('title',parent=body,fontName='Times-Bold',fontSize=24,leading=28,alignment=TA_LEFT,spaceAfter=8),
      'subtitle':ParagraphStyle('subtitle',parent=body,fontName='Times-Bold',fontSize=13,leading=17,alignment=TA_LEFT,spaceAfter=13),
      'meta':ParagraphStyle('meta',parent=body,fontSize=10,leading=13,alignment=TA_LEFT,spaceAfter=4),
      'h2':ParagraphStyle('h2',parent=body,fontName='Times-Bold',fontSize=14,leading=18,alignment=TA_LEFT,spaceBefore=13,spaceAfter=7,keepWithNext=True),
      'h3':ParagraphStyle('h3',parent=body,fontName='Times-Bold',fontSize=11.6,leading=15,alignment=TA_LEFT,spaceBefore=9,spaceAfter=5,keepWithNext=True),
      'ref':ParagraphStyle('ref',parent=body,fontSize=9.4,leading=12.4,alignment=TA_LEFT,spaceAfter=6,wordWrap=None),
      'table':ParagraphStyle('table',parent=body,fontSize=9.2,leading=12.4,alignment=TA_LEFT,spaceAfter=0)}
    lines=s.splitlines();flow=[Paragraph(inline(lines[0][2:]),styles['title']),Paragraph(inline(lines[1][3:]),styles['subtitle'])]
    blocks=re.split(r'\n\s*\n','\n'.join(lines[2:]).strip()); abstract=False;refs=False;count=0
    for block in blocks:
        if block.startswith('## ') or block.startswith('### '):
            heading=block.lstrip('# ').strip(); level=0 if block.startswith('## ') else 1
            if heading=='Declarations': flow.append(PageBreak())
            if heading in ('References','参考文献'): refs=True;flow.append(PageBreak())
            if heading.startswith('1. '): flow.append(PageBreak())
            if heading in ('Abstract','摘要'): abstract=True;level=0
            p=Paragraph(inline(heading),styles['h2' if level==0 else 'h3']);p.bookmark='s'+str(count);p.level=level;count+=1;flow.append(p);continue
        if not abstract:
            for l in block.splitlines(): flow.append(Paragraph(inline(l),styles['meta']))
            flow.append(Spacer(1,5));continue
        if block.startswith('|'):
            rows=[]
            for l in block.splitlines():
                cells=[c.strip() for c in l.strip('| ').split('|')]
                if all(re.fullmatch(r'[-: ]+',c) for c in cells): continue
                rows.append([Paragraph(('<b>'+inline(c)+'</b>') if not rows else inline(c),styles['table']) for c in cells])
            if len(rows[0])!=3: raise ValueError('Unexpected table width')
            width=A4[0]-108;t=Table(rows,colWidths=[width*.23,width*.36,width*.41],repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EEEEEE')),('LINEBELOW',(0,0),(-1,0),.6,colors.grey),('LINEBELOW',(0,1),(-1,-1),.3,colors.lightgrey),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));flow.extend([t,Spacer(1,10)]);continue
        flow.append(Paragraph(inline(block.replace('\n',' ')),styles['ref'] if refs else body))
    doc=Report(str(target),pagesize=A4,leftMargin=54,rightMargin=54,topMargin=49,bottomMargin=47,title=TITLE,author='Hongju Liu',subject=REPORT+' | Position paper and conceptual analysis | Not peer reviewed',keywords=DOI+'; human-AI coexistence; superintelligence',pageCompression=0)
    doc.build(flow,onFirstPage=page,onLaterPages=page,canvasmaker=partial(canvas.Canvas,invariant=1,pageCompression=0))

def landing(text:str,lang:str)->str:
    suffix='' if lang=='en' else '-zh'; pdf=STEM+suffix+'-v1.0.pdf';md=STEM+suffix+'-v1.0.md'
    title=TITLE if lang=='en' else '超越控制保证：极端能力不对等条件下的人类—超级智能共存提议'
    url='/research/beyond-guaranteed-control/' if lang=='en' else '/research/beyond-guaranteed-control/zh.html'
    ab='### Abstract' if lang=='en' else '### 摘要';abstract=text.split(ab+'\n\n',1)[1].split('\n\n',1)[0]
    fm={'layout':'default','title':title,'description':'TA-TR-2026-04 v1.0. Independent fourth preprint; non-amending; not peer reviewed.','permalink':url,'reading_page':True,'scholarly_article':True,'citation_title':title,'citation_author':'Hongju Liu','citation_publication_date':'2026/09/17','citation_doi':DOI,'citation_pdf_url':SITE+pdf,'citation_technical_report_institution':'Independent research','citation_technical_report_number':REPORT,'citation_language':lang,'citation_keywords':'human-AI coexistence; superintelligence; capability asymmetry; ex ante proposal; prospective autonomy; attributable participation','article_identifier':REPORT,'article_version':'1.0','article_date':'2026-09-17','article_license':'CC BY 4.0; third-party source rights retained','article_pdf':SITE+pdf,'article_record_url':'https://zenodo.org/records/'+str(RID),'article_bibtex':SITE+'citation.bib','article_metadata':SITE+'publication-record.json','article_abstract':abstract}
    header='---\n'+'\n'.join(k+': '+json.dumps(v,ensure_ascii=False) for k,v in fm.items())+'\n---\n\n'
    access=f'[Research index](/research/) · [English]({SITE}) · [中文全文]({SITE}zh.html) · [PDF]({pdf}) · [DOI](https://doi.org/{DOI})\n\n'
    note=f'\n\n## Publication and citation boundary\n\nThis English paper and its Chinese translation constitute one research deposit under DOI {DOI}, not two independent papers. Both PDFs and Markdown files are exact-byte mirrors of the deposit. [Publication receipt](publication-record.json) · [BibTeX](citation.bib) · [RIS](citation.ris) · [Supplement](research-supplement-v1.0.zip) · [Checksums](SHA256SUMS.txt).\n\nNot peer reviewed. Human-directed; substantive AI research and drafting disclosed. Publication authorization is not a claim of separate final human line-by-line review. A fourth independent research paper, not a new version of any previous paper and not a fourth Bitcoin Original. Citation and preservation do not confer interpretive authority or prove safety. Metadata supports discovery; Google Scholar inclusion is not guaranteed or claimed.\n'
    return header+access+'{% include_relative '+md+' %}\n'+note

def build(root:Path,out:Path)->dict:
    out.mkdir(parents=True,exist_ok=True);files,source_manifest=load_sources(root);texts={};support={'PUBLICATION-NOTE.md':NOTE,'SOURCE-MANIFEST.json':jdump(source_manifest)};checks={}
    for name,s in files.items(): support['reviewed-input/'+name]=s
    for lang in ('en','zh'):
        old=files[f'Beyond_Guaranteed_Control_{lang.upper()}_v1.0.md'];s=publication_text(old,lang);texts[lang]=s
        base=STEM+('' if lang=='en' else '-zh')+'-v1.0';write(out/(base+'.md'),s);pdf_build(s,out/(base+'.pdf'),lang)
        if (out/(base+'.pdf')).stat().st_size>=5_000_000: raise ValueError('PDF over Scholar size limit')
        decl='## Declarations' if lang=='en' else '## 声明';ref='## References' if lang=='en' else '## 参考文献'
        refs=re.findall(r'^\[(\d+)\] ',s.split(ref,1)[1],re.M)
        if refs!=list(map(str,range(1,41))): raise ValueError('Reference sequence mismatch')
        checks[lang]={'body_unchanged':True,'abstract_unchanged':True,'references_unchanged':True,'reference_count':40,'body_sha256':sha(s.split('## 1.',1)[1].split(decl)[0].encode())}
        support['publication-only-'+lang+'.diff']=''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='reviewed-v1.0',tofile='publication-v1.0'))
        write(out/('index.md' if lang=='en' else 'zh.md'),landing(s,lang))
    for pattern in (r'^#{2,3} (\d+(?:\.\d+)*)\.',r'\[(\d+(?:[–,\-]\d+)*)\]'):
        a=re.findall(pattern,texts['en'],re.M);b=re.findall(pattern,texts['zh'],re.M)
        if a!=b: raise ValueError('Bilingual structure mismatch')
    if texts['en'].split('## References\n',1)[1]!=texts['zh'].split('## 参考文献\n',1)[1]: raise ValueError('Bilingual references differ')
    checks['scope']='Formatting and source identity checks only; not peer review or Google Scholar indexing certification.'
    checks['embedded_cjk_font_sha256']=FONT_SHA;support['SOURCE-CHECKS.json']=jdump(checks)
    citation='@techreport{Liu2026BeyondGuaranteedControl,\n  author = {Liu, Hongju},\n  title = {'+TITLE+'},\n  institution = {Independent research},\n  number = {TA-TR-2026-04},\n  year = {2026},\n  month = {sep},\n  version = {1.0},\n  doi = {'+DOI+'},\n  url = {https://doi.org/'+DOI+'},\n  note = {Open-access preprint; not peer reviewed; substantive AI contribution disclosed}\n}\n'
    write(out/'citation.bib',citation)
    write(out/'citation.ris','TY  - RPRT\nAU  - Liu, Hongju\nTI  - '+TITLE+'\nPY  - 2026\nDA  - 2026/09/17\nDO  - '+DOI+'\nUR  - https://doi.org/'+DOI+'\nM1  - TA-TR-2026-04\nN1  - Version 1.0; preprint; not peer reviewed.\nER  - \n')
    write(out/'citation.csl.json',jdump([{'id':'Liu2026BeyondGuaranteedControl','type':'report','title':TITLE,'author':[{'family':'Liu','given':'Hongju'}],'issued':{'date-parts':[[2026,9,17]]},'number':REPORT,'version':'1.0','DOI':DOI,'URL':'https://doi.org/'+DOI}]))
    write(out/'README-LICENSE.txt',TITLE+'\n'+REPORT+' | Version 1.0 | DOI '+DOI+'\n\nCC BY 4.0: https://creativecommons.org/licenses/by/4.0/\nThird-party/historical quoted materials retain source rights.\n\n'+NOTE)
    with zipfile.ZipFile(out/'research-supplement-v1.0.zip','w',compression=zipfile.ZIP_STORED) as z:
        for name,s in sorted(support.items()):
            info=zipfile.ZipInfo('research-supplement-v1.0/'+name,(2026,9,17,0,0,0));info.compress_type=zipfile.ZIP_STORED;info.external_attr=0o100644<<16;z.writestr(info,s.encode())
    pubnames=[STEM+'-v1.0.pdf',STEM+'-zh-v1.0.pdf',STEM+'-v1.0.md',STEM+'-zh-v1.0.md','citation.bib','citation.ris','citation.csl.json','README-LICENSE.txt','research-supplement-v1.0.zip']
    write(out/'SHA256SUMS.txt',''.join(sha((out/n).read_bytes())+'  '+n+'\n' for n in pubnames));pubnames+=['SHA256SUMS.txt']
    result={'schema':'trinityaccord.expected-publication.v1','record_id':RID,'doi':DOI,'title':TITLE,'version':'1.0','report_number':REPORT,'files':[{'name':n,'bytes':(out/n).stat().st_size,'sha256':sha((out/n).read_bytes())} for n in pubnames],'source_checks':checks}
    write(out/'EXPECTED-PUBLICATION.json',jdump(result));write(out/'PUBLICATION-NOTE.md',NOTE)
    return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=Path(__file__).parent);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();print(jdump(build(a.source,a.out)))
