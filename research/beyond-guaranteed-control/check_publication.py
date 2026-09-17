#!/usr/bin/env python3
"""Bounded format checks; never reports Google Scholar indexing or peer review."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from pathlib import Path
from html.parser import HTMLParser
import yaml
from prepare_publication import DOI, RID, TITLE, REPORT, STEM, SITE, jdump
class Tags(HTMLParser):
    def __init__(self): super().__init__();self.meta={};self.text=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta' and 'name' in a: self.meta[a['name']]=a.get('content','')
    def handle_data(self,s): self.text.append(s)
def run(*args): return subprocess.check_output(args,text=True)
def compact(s): return re.sub(r'\s+','',s)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--files',type=Path,required=True);ap.add_argument('--expected',type=Path,required=True);ap.add_argument('--site-dir',type=Path);ap.add_argument('--report',type=Path,required=True);a=ap.parse_args()
    expected=json.loads(a.expected.read_text());actual=json.loads((a.files/'EXPECTED-PUBLICATION.json').read_text())
    if expected!=actual: raise RuntimeError('Build differs from locally reviewed expectations')
    for e in expected['files']:
        b=(a.files/e['name']).read_bytes()
        if len(b)!=e['bytes'] or hashlib.sha256(b).hexdigest()!=e['sha256']: raise RuntimeError('Publication byte mismatch: '+e['name'])
    checks=[]
    for lang in ('en','zh'):
        base=STEM+('' if lang=='en' else '-zh')+'-v1.0';pdf=a.files/(base+'.pdf');page=a.files/('index.md' if lang=='en' else 'zh.md')
        first=run('pdftotext','-f','1','-l','1',str(pdf),'-');text=run('pdftotext',str(pdf),'-');fonts=run('pdffonts',str(pdf))
        if pdf.stat().st_size>=5_000_000 or len(text)<20000: raise RuntimeError('PDF size/text extraction failure')
        if 'Hongju Liu' not in first or DOI not in first: raise RuntimeError('First-page author/DOI missing')
        title=TITLE if lang=='en' else '超越控制保证：极端能力不对等条件下的人类—超级智能共存提议'
        if compact(title.replace(': ','' ).replace('：','')) not in compact(first):
            # Main title and subtitle are displayed on separate lines without a colon.
            raise RuntimeError('Full first-page title missing')
        if '[40]' not in text or ('References' if lang=='en' else '参考文献') not in text: raise RuntimeError('Reference section missing')
        if not any('Bousung' in l and re.search(r'yes\s+yes\s+yes',l) for l in fonts.splitlines()): raise RuntimeError('CJK glyphs not subset-embedded with Unicode mapping')
        md=page.read_text();front=yaml.safe_load(md.split('---',2)[1])
        for k,v in {'citation_title':title,'citation_author':'Hongju Liu','citation_doi':DOI,'citation_publication_date':'2026/09/17','citation_pdf_url':SITE+base+'.pdf','citation_technical_report_number':REPORT,'citation_language':lang}.items():
            if front.get(k)!=v: raise RuntimeError('Source scholarly metadata mismatch: '+k)
        if len(front.get('article_abstract',''))<250 or '{% include_relative '+base+'.md %}' not in md: raise RuntimeError('Complete abstract/full text not exposed')
        if a.site_dir:
            p=a.site_dir/'research/beyond-guaranteed-control'/('index.html' if lang=='en' else 'zh.html');h=p.read_text();parser=Tags();parser.feed(h)
            for k in ('citation_title','citation_author','citation_doi','citation_publication_date','citation_pdf_url','citation_technical_report_number','citation_language'):
                if parser.meta.get(k)!=front[k]: raise RuntimeError('Rendered scholarly metadata mismatch: '+k)
            if compact(front['article_abstract']) not in compact(' '.join(parser.text)): raise RuntimeError('Complete abstract missing from rendered HTML')
            b=(p.parent/(base+'.pdf')).read_bytes()
            if b!=pdf.read_bytes(): raise RuntimeError('Rendered-site PDF mirror mismatch')
        checks.append({'language':lang,'searchable_full_text':True,'first_page_title_author_doi':True,'reference_count_in_source':40,'pdf_bytes':pdf.stat().st_size,'cjk_subset_embedded':True,'highwire_source_metadata':True,'rendered_site_checked':bool(a.site_dir)})
    result={'status':'FORMAT_AND_BYTE_CHECKS_PASS','record_id':RID,'doi':DOI,'checks':checks,'google_scholar_indexing':'NOT_ASSERTED','peer_reviewed':False,'limitations':'Technical format/source checks only. No external indexing, peer-review, novelty or safety certification.'}
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(jdump(result));print(jdump(result))
if __name__=='__main__': main()
