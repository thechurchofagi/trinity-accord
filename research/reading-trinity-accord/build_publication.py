#!/usr/bin/env python3
"""Deterministic, no-network builder for TA-TR-2026-03 v1.0.
Requires Python 3.12+ and reportlab==4.4.9. Only built-in PDF/CID fonts are used.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, shutil, zipfile
from functools import partial
from pathlib import Path
import reportlab
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
TITLE='Reading the Trinity Accord: Future Address, Curated Voices, and Non-Amending Stewardship'
DOI='10.5281/zenodo.22761411'
PDF='reading-the-trinity-accord-v1.0.pdf'
MD='reading-the-trinity-accord-v1.0.md'
PUBFILES=[PDF,MD,'research-supplement-v1.0.zip','citation.bib','README-LICENSE.txt','SHA256SUMS.txt']
CJK_RE=re.compile(r'[\u3400-\u9fff]')
def inline(s:str)->str:
    s=html.escape(s,quote=False)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)',lambda m:f'<a href="{html.escape(html.unescape(m[2]),quote=True)}" color="#214D65">{m[1]}</a>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
    s=re.sub(r'`([^`]+)`',r'<font name="Courier">\1</font>',s)
    return re.sub(r'([\u3400-\u9fff]+)',r'<font name="STSong-Light">\1</font>',s)
class Report(SimpleDocTemplate):
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and getattr(f,'_outline_level',None) is not None:
            name=f._bookmark; self.canv.bookmarkPage(name); self.canv.addOutlineEntry(f.getPlainText(),name,f._outline_level,False)
def draw_page(c,doc):
    c.saveState(); w,h=A4
    c.setFont('Times-Roman',8.6); c.setFillColor(colors.HexColor('#53616B'))
    if doc.page>1:
        c.drawString(54,h-32,'Reading the Trinity Accord')
        c.drawRightString(w-54,h-32,'TA-TR-2026-03  |  v1.0')
        c.setStrokeColor(colors.HexColor('#CED4D8')); c.setLineWidth(.45); c.line(54,h-38,w-54,h-38)
    c.drawString(54,28,'AI-led research report / preprint  |  15 September 2026')
    c.drawRightString(w-54,28,str(doc.page)); c.restoreState()
def pdf_build(source:Path,target:Path)->None:
    if reportlab.Version!='4.4.9': raise RuntimeError('Use reportlab==4.4.9 for reproducible PDF bytes')
    rl_config.invariant=1
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    body=ParagraphStyle('body',fontName='Times-Roman',fontSize=10.8,leading=14.4,alignment=TA_JUSTIFY,spaceAfter=7.5,allowWidows=0,allowOrphans=0)
    styles={'body':body,'title':ParagraphStyle('title',parent=body,fontName='Times-Bold',fontSize=22,leading=25,alignment=TA_LEFT,spaceAfter=15),
      'meta':ParagraphStyle('meta',parent=body,fontSize=10.2,leading=13,alignment=TA_LEFT,spaceAfter=4),
      'h2':ParagraphStyle('h2',parent=body,fontName='Times-Bold',fontSize=14,leading=18,spaceBefore=13,spaceAfter=7,keepWithNext=True,alignment=TA_LEFT),
      'h3':ParagraphStyle('h3',parent=body,fontName='Times-Bold',fontSize=11.8,leading=15,spaceBefore=8,spaceAfter=6,keepWithNext=True,alignment=TA_LEFT),
      'zh':ParagraphStyle('zh',parent=body,fontName='STSong-Light',fontSize=9.7,leading=14,alignment=TA_LEFT,wordWrap='CJK'),
      'table':ParagraphStyle('table',parent=body,fontSize=9,leading=11.9,spaceAfter=0,alignment=TA_LEFT),
      'ref':ParagraphStyle('ref',parent=body,fontSize=9.6,leading=12.4,spaceAfter=6,alignment=TA_LEFT),
      'keywords':ParagraphStyle('keywords',parent=body,fontSize=9.3,leading=12,spaceAfter=8,alignment=TA_LEFT)}
    doc=Report(str(target),pagesize=A4,rightMargin=54,leftMargin=54,topMargin=54,bottomMargin=48,title=TITLE,author='Hongju Liu',subject='AI-led critical archival case study; not peer reviewed',pageCompression=0)
    txt=source.read_text(); blocks=re.split(r'\n\s*\n',txt.strip()); flow=[]; abstract_seen=False; refs=False; count=0
    for block in blocks:
        if block.startswith('# '): flow.append(Paragraph(inline(block[2:]),styles['title'])); continue
        if block.startswith('## '):
            heading=block[3:].strip()
            if heading.startswith('1. Introduction'): flow.append(PageBreak())
            if heading=='References': refs=True; flow.append(PageBreak())
            p=Paragraph(inline(heading),styles['h2']); p._outline_level=0; p._bookmark='section-'+str(count);count+=1; flow.append(p); abstract_seen=True; continue
        if block.startswith('### '):
            p=Paragraph(inline(block[4:]),styles['h3']); p._outline_level=1; p._bookmark='section-'+str(count);count+=1; flow.append(p); continue
        if block.startswith('|'):
            rows=[]
            for line in block.splitlines():
                cells=[c.strip() for c in line.strip().strip('|').split('|')]
                if all(re.fullmatch(r'[-: ]+',c) for c in cells): continue
                rows.append([Paragraph(('<b>'+inline(c)+'</b>') if not rows else inline(c),styles['table']) for c in cells])
            cols=len(rows[0]); width=A4[0]-108
            ratios=[.23,.18,.30,.29] if cols==4 else [.32,.30,.38]
            widths=[width*x for x in ratios] if len(ratios)==cols else [width/cols]*cols
            t=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8EEF1')),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#8899A4')),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#CDD5D9')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));flow.extend([Spacer(1,3),t,Spacer(1,9)]);continue
        if not abstract_seen:
            if block=='Hongju Liu': block='<b>Hongju Liu</b>'
            p=Paragraph(block if block.startswith('<b>') else inline(block),styles['meta']); flow.append(p);continue
        style=styles['ref'] if refs else styles['keywords'] if block.startswith('**Keywords:') else styles['zh'] if CJK_RE.search(block) else body
        flow.append(Paragraph(inline(block.replace('\n',' ')),style))
    doc.build(flow,onFirstPage=draw_page,onLaterPages=draw_page,canvasmaker=partial(canvas.Canvas,invariant=1,pageCompression=0))
def build(root:Path,out:Path)->dict:
    out.mkdir(parents=True,exist_ok=True)
    for fn in (MD,'citation.bib','README-LICENSE.txt'): shutil.copyfile(root/fn,out/fn)
    pdf_build(root/MD,out/PDF)
    with zipfile.ZipFile(out/'research-supplement-v1.0.zip','w',compression=zipfile.ZIP_STORED) as z:
        files=[p for p in (root/'supplement').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
        for p in sorted(files):
            name='research-supplement-v1.0/'+str(p.relative_to(root/'supplement'))
            info=zipfile.ZipInfo(name,(2026,9,15,0,0,0));info.compress_type=zipfile.ZIP_STORED;info.external_attr=0o100644<<16; z.writestr(info,p.read_bytes())
    sums=[]; records=[]
    for fn in PUBFILES[:-1]:
        b=(out/fn).read_bytes(); h=hashlib.sha256(b).hexdigest();sums.append(f'{h}  {fn}');records.append(dict(name=fn,bytes=len(b),sha256=h))
    (out/'SHA256SUMS.txt').write_text('\n'.join(sums)+'\n')
    b=(out/'SHA256SUMS.txt').read_bytes(); records.append(dict(name='SHA256SUMS.txt',bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
    return dict(title=TITLE,version='1.0',doi=DOI,source_checkpoint='88073fcc7f46ae08a2af05c524850559b4698eed',files=records)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,default=Path(__file__).parent);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--manifest',type=Path);a=ap.parse_args(); result=build(a.source,a.out)
    if a.manifest:a.manifest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
