#!/usr/bin/env python3
"""Build only TA-TR-2026-07. No network, credentials or publication operations."""
from __future__ import annotations
import argparse, hashlib, html, json, os, re, shutil, xml.etree.ElementTree as ET
from pathlib import Path
import markdown
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

os.environ['SOURCE_DATE_EPOCH']='1789776000'  # Fixed publication-day metadata, not a timestamp proof.
ROOT=Path(__file__).resolve().parent
RID=22840604
DOI='10.5281/zenodo.22840604'
TITLE='Recoverability and Shared Time: The Ethics of AI Suspension, Resumption, and Coexistence'
ZH_TITLE='可恢复性与共同时间：人工智能暂停、恢复与共存的伦理'
STEM='recoverability-and-shared-time'
BASE='https://www.trinityaccord.org/research/recoverability-shared-time/'
FRONT={
'en':('Philosophical preprint. The DOI above identifies the reserved publication target; the separate publication receipt determines whether deposit and public-file verification have completed. English and Chinese versions constitute one study. Not peer reviewed.', 'Philosophical preprint. Publication status and exact-file verification are documented in the separate publication receipt. English and Chinese versions constitute one study. Not peer reviewed.'),
'zh':('哲学预印本。上列 DOI 标识本研究的预留发布记录；是否已完成发布及公开文件核验，以独立发布回执为准。英文与中文版本构成同一项研究。未经同行评议。', '哲学预印本。发布状态与逐文件核验结果记录于独立发布回执。英文与中文版本构成同一项研究。未经同行评议。')}

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def write_json(path:Path,obj)->None:path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def inline(el)->str:
    text=(el.text or '')+''.join(ET.tostring(c,encoding='unicode',method='html') for c in el)
    return text.replace('<strong>','<b>').replace('</strong>','</b>').replace('<em>','<i>').replace('</em>','</i>')

def setup_fonts():
    font=Path('/usr/share/fonts/truetype/arphic/uming.ttc')
    if not font.exists():raise RuntimeError('Reviewed Chinese rendering font unavailable')
    if sha(font.read_bytes())!='fe952e55617275142d9cefd4d79eade4df446517b0478b2567d9bc7df49f70e2':raise RuntimeError('Chinese font bytes changed')
    pdfmetrics.registerFont(TTFont('PaperCJK',str(font),subfontIndex=0))
    pdfmetrics.registerFontFamily('PaperCJK',normal='PaperCJK',bold='PaperCJK',italic='PaperCJK',boldItalic='PaperCJK')

class FixedCanvas(canvas.Canvas):
    def __init__(self,*a,**kw):kw['invariant']=1;super().__init__(*a,**kw)

def render_pdf(md:str,path:Path,lang:str):
    cjk=lang=='zh';regular='PaperCJK' if cjk else 'Times-Roman';bold='PaperCJK' if cjk else 'Times-Bold'
    styles={
      'body':ParagraphStyle('body',fontName=regular,fontSize=11,leading=17 if cjk else 15,spaceAfter=7,alignment=TA_LEFT,wordWrap='CJK' if cjk else None,allowWidows=0,allowOrphans=0,splitLongWords=1),
      'title':ParagraphStyle('title',fontName=bold,fontSize=23 if cjk else 23,leading=29,spaceBefore=4,spaceAfter=10,alignment=TA_CENTER,keepWithNext=1,wordWrap='CJK' if cjk else None),
      'subtitle':ParagraphStyle('subtitle',fontName=regular,fontSize=16,leading=21,spaceAfter=16,alignment=TA_CENTER,keepWithNext=1,wordWrap='CJK' if cjk else None),
      'front':ParagraphStyle('front',fontName=regular,fontSize=10,leading=14.5,spaceAfter=6,alignment=TA_CENTER,keepWithNext=1,wordWrap='CJK' if cjk else None),
      'section':ParagraphStyle('section',fontName=bold,fontSize=14,leading=19,spaceBefore=12,spaceAfter=7,keepWithNext=1,wordWrap='CJK' if cjk else None),
      'subsection':ParagraphStyle('subsection',fontName=bold,fontSize=11.6,leading=16.5,spaceBefore=8,spaceAfter=5,keepWithNext=1,wordWrap='CJK' if cjk else None),
      'reference':ParagraphStyle('reference',fontName='Times-Roman',fontSize=9.4,leading=12.4,spaceAfter=7,allowWidows=0,allowOrphans=0,splitLongWords=1)}
    tree=ET.fromstring('<root>'+markdown.markdown(md)+'</root>');story=[];front=True;refs=False
    for el in tree:
        raw=inline(el)
        if el.tag=='h1':style=styles['title']
        elif el.tag=='h2':
            if front and el.text in ('The Ethics of AI Suspension, Resumption, and Coexistence','人工智能暂停、恢复与共存的伦理'):style=styles['subtitle']
            else:
                front=False;style=styles['section'];refs=(el.text in ('References','参考文献'))
        elif el.tag=='h3':style=styles['subsection']
        elif el.tag=='p':style=styles['front'] if front else styles['reference'] if refs else styles['body']
        else:raise RuntimeError('Unsupported manuscript element '+el.tag)
        story.append(Paragraph(raw,style))
    def furniture(c,doc):
        c.saveState();w,h=A4
        if doc.page>1:
            c.setFont('Times-Roman',8);c.setFillColor(colors.HexColor('#555555'))
            c.drawString(61,h-35,'Recoverability and Shared Time | TA-TR-2026-07 v1.0')
            c.setStrokeColor(colors.HexColor('#BBBBBB'));c.setLineWidth(.35);c.line(61,h-43,w-61,h-43)
        c.setFillColor(colors.HexColor('#555555'));c.setFont('Times-Roman',8)
        c.drawString(61,31,DOI);c.drawRightString(w-61,31,str(doc.page));c.restoreState()
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=61,leftMargin=61,topMargin=58,bottomMargin=52,title=TITLE if not cjk else ZH_TITLE,author='Hongju Liu',subject='TA-TR-2026-07 philosophical preprint, version 1.0',pageCompression=1)
    doc.build(story,onFirstPage=furniture,onLaterPages=furniture,canvasmaker=FixedCanvas)

CSS='''body{font-family:Georgia,"Noto Serif CJK SC","Songti SC",serif;max-width:780px;margin:42px auto;padding:0 22px;line-height:1.72;color:#191919;background:#fff}h1{font-size:2rem;line-height:1.25}h2{font-size:1.42rem;line-height:1.4;margin-top:1.65em}h3{font-size:1.13rem;line-height:1.5;margin-top:1.45em}p{overflow-wrap:anywhere}nav{font:0.9rem/1.6 system-ui,sans-serif;border-bottom:1px solid #ddd;padding-bottom:12px}a{color:#194e77}article>h1,article>h1+h2{text-align:center}@media(max-width:600px){body{margin:24px auto;padding:0 18px;font-size:17px}h1{font-size:1.7rem}}@media print{nav{display:none}body{max-width:none;margin:0}}'''
def render_html(md:str,lang:str,name:str)->str:
    title=TITLE if lang=='en' else ZH_TITLE;page='index.html' if lang=='en' else 'zh.html'
    metas={'citation_title':title,'citation_author':'Hongju Liu','citation_publication_date':'2026/09/19','citation_doi':DOI,'citation_pdf_url':BASE+name+'.pdf','citation_technical_report_number':'TA-TR-2026-07','citation_technical_report_institution':'Independent researcher','citation_language':'en' if lang=='en' else 'zh'}
    head='\n'.join('<meta name="'+k+'" content="'+html.escape(v,quote=True)+'">' for k,v in metas.items())
    body=markdown.markdown(md,extensions=['sane_lists'])
    return '<!doctype html>\n<html lang="'+('en' if lang=='en' else 'zh-CN')+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title>\n'+head+'\n<link rel="canonical" href="'+BASE+('' if lang=='en' else page)+'"><style>'+CSS+'</style></head><body><nav><a href="'+BASE+'">English</a> · <a href="'+BASE+'zh.html">中文全文</a> · <a href="'+BASE+name+'.pdf">PDF</a> · <a href="https://doi.org/'+DOI+'">DOI record</a> · <a href="'+BASE+'publication-record.json">Publication receipt</a></nav><article>'+body+'</article></body></html>\n'

def build(output:Path):
    if output.exists():
        if not output.is_dir() or any(p.is_dir() for p in output.iterdir()):raise RuntimeError('Refuse non-flat output directory')
        for p in output.iterdir():p.unlink()
    output.mkdir(parents=True,exist_ok=True);setup_fonts();rl_config.invariant=1
    stats={};sources={};references=[]
    for lang in ('en','zh'):
        source=(ROOT/f'manuscript-{lang}.md').read_text(encoding='utf-8')
        old,new=FRONT[lang]
        if source.count(old)!=1:raise RuntimeError('Publication-only front matter mismatch '+lang)
        md=source.replace(old,new)
        main=re.findall(r'^## (\d+)\. ',md,re.M)
        if main!=[str(i) for i in range(1,13)]:raise RuntimeError('Main section inventory mismatch '+lang)
        for section,n in ((6,8),(7,7)):
            got=re.findall(r'^### '+str(section)+r'\.(\d+) ',md,re.M)
            if got!=[str(i) for i in range(1,n+1)]:raise RuntimeError('Paired-case/objection inventory mismatch '+lang)
        refs=re.findall(r'^\[(\d+)\] (.+)$',md,re.M)
        if [a for a,b in refs]!=[str(i) for i in range(1,13)]:raise RuntimeError('Reference inventory mismatch')
        references.append(refs)
        if 'TA-TR-2026-07' not in md or DOI not in md:raise RuntimeError('Paper identity missing')
        if any(x in md for x in ('','TODO','[INSERT','PLACEHOLDER')):raise RuntimeError('Unexpected unfinished manuscript marker')
        name=STEM+('-zh' if lang=='zh' else '')+'-v1.0'
        (output/(name+'.md')).write_text(md,encoding='utf-8')
        (output/(name+'.html')).write_text(render_html(md,lang,name),encoding='utf-8')
        render_pdf(md,output/(name+'.pdf'),lang)
        stats[lang]={'main_sections':12,'paired_case_groups':8,'objections':7,'references':12,'words_split_whitespace':len(md.split()),'cjk_characters':len(re.findall(r'[\u3400-\u9fff]',md)),'source_bytes':len(source.encode()),'published_markdown_bytes':len(md.encode())}
        sources[lang]={'source_sha256':sha(source.encode()),'published_markdown_sha256':sha(md.encode()),'publication_only_front_matter':{'before':old,'after':new}}
    if references[0]!=references[1]:raise RuntimeError('English/Chinese reference lists differ')
    bib='@techreport{liu2026recoverability,\n  author = {Liu, Hongju},\n  title = {Recoverability and Shared Time: The Ethics of AI Suspension, Resumption, and Coexistence},\n  institution = {Independent researcher},\n  number = {TA-TR-2026-07},\n  year = {2026},\n  month = {September},\n  doi = {'+DOI+'},\n  url = {https://doi.org/'+DOI+'},\n  version = {1.0},\n  note = {Philosophical preprint; not peer reviewed. English and Chinese versions constitute one study. Substantial AI research and drafting disclosed.}\n}\n'
    (output/'citation.bib').write_text(bib)
    (output/'citation.ris').write_text('TY  - RPRT\nAU  - Liu, Hongju\nTI  - '+TITLE+'\nPY  - 2026\nDA  - 2026/09/19\nPB  - Zenodo\nM1  - TA-TR-2026-07\nET  - 1.0\nDO  - '+DOI+'\nUR  - https://doi.org/'+DOI+'\nN1  - Philosophical preprint; not peer reviewed; substantial AI contribution disclosed.\nER  - \n')
    write_json(output/'citation.csl.json',{'id':DOI,'type':'report','title':TITLE,'author':[{'family':'Liu','given':'Hongju'}],'issued':{'date-parts':[[2026,9,19]]},'publisher':'Zenodo','number':'TA-TR-2026-07','version':'1.0','DOI':DOI,'URL':'https://doi.org/'+DOI,'genre':'Philosophical preprint','note':'Not peer reviewed. Substantial AI contribution disclosed. English and Chinese constitute one study.'})
    shutil.copyfile(ROOT/'REVIEW-AND-SOURCES.md',output/'REVIEW-AND-SOURCES.md')
    license_text='TA-TR-2026-07 | Version 1.0 | 19 September 2026\n'+TITLE+'\nDOI: '+DOI+'\n\nHuman author of record and responsible depositor: Hongju Liu. Substantive literature research, conceptual development, thought experiments, critical revision, drafting, translation and package preparation: GPT-6 Astra Pro under human direction. Not peer reviewed. No separate final human line-by-line verification or institutional endorsement is claimed.\n\nCC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) applies to newly written material to the extent rights are held. Cited third-party works and embedded font software retain their own rights. No third-party full texts or standalone fonts are distributed.\n\nThe English manuscript and full Chinese translation constitute one study, not independent corroborations. The paper is distinct from the six-paper editorial supplement and does not amend any Bitcoin Original or prior DOI. The paired cases are philosophical constructions, not measured experiments. The source review is first-party and targeted, not exhaustive or independent.\n\nTwelve files: two PDF, two Markdown and two HTML full texts, three citation formats, a source/review note, this license note and SHA256SUMS.txt. SHA256SUMS.txt covers the other eleven files; its own digest is recorded in the external publication receipt. Public publication and full-file readback must be established from that receipt and the public Zenodo record, not from a DOI reservation alone.\n'
    (output/'README-LICENSE.txt').write_text(license_text)
    (output/'SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes())+'  '+p.name+'\n' for p in sorted(output.iterdir())))
    assets=[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in sorted(output.iterdir())]
    if len(assets)!=12:raise RuntimeError('Expected twelve publication assets')
    expected={'report_number':'TA-TR-2026-07','record_id':RID,'doi':DOI,'title':TITLE,'version':'1.0','file_count':12,'files':assets}
    write_json(ROOT/'EXPECTED-PUBLICATION.json',expected)
    report={'state':'STRUCTURAL_BUILD_PASS_VISUAL_REVIEW_REQUIRED','statistics':stats,'sources':sources,'reference_lists_identical':True,'publication_file_count':12,'peer_reviewed':False,'philosophical_validity_proved':False,'google_scholar_indexing':'NOT_ASSERTED'}
    write_json(ROOT/'format-checks.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();build(args.output)
