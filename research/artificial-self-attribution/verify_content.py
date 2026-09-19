from pathlib import Path
import json, re, sys, unicodedata
from zipfile import ZipFile
from html.parser import HTMLParser
import fitz
from lxml import etree

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from build_documents import read_blocks
from build_publication import manuscript_info, stem

def norm(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s).replace('\u00ad','').replace('\u200b',''))

class Article(HTMLParser):
    def __init__(self):
        super().__init__(); self.inside=False; self.text=[]; self.meta={}
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=='article': self.inside=True
        if tag=='meta' and 'name' in attrs: self.meta[attrs['name']]=attrs.get('content')
    def handle_endtag(self, tag):
        if tag=='article': self.inside=False
    def handle_data(self, text):
        if self.inside: self.text.append(text)

deposit=json.loads((ROOT/'deposit.json').read_text())
report=json.loads((ROOT/'format-checks.json').read_text())
detail=[]
for lang in ['en','zh']:
    base=ROOT/'published'/stem(lang)
    p=lambda ext: Path(str(base)+ext)
    expected='\n'.join(t for _,t in read_blocks(p('.md')))
    with ZipFile(p('.docx')) as z:
        tree=etree.fromstring(z.read('word/document.xml'))
        body=''.join(tree.xpath('//w:body/w:p//w:t/text()',namespaces={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}))
        links=etree.fromstring(z.read('word/_rels/document.xml.rels')).xpath('//*[local-name()="Relationship" and contains(@Type,"hyperlink")]/@Target')
    pdf=fitz.open(p('.pdf')); extracted=[]; bounds=[]
    for i,page in enumerate(pdf):
        for b in page.get_text('blocks'):
            if b[4].strip()==str(i+1) and b[1]>page.rect.height-70: continue
            extracted.append(b[4])
            if b[0]<20 or b[2]>page.rect.width-20 or b[1]<20 or b[3]>page.rect.height-35:
                bounds.append({'page':i+1,'box':b[:4]})
    html=Article(); html.feed(p('.html').read_text())
    values=[norm(x) for x in (expected,body,''.join(extracted),''.join(html.text))]
    record={'language':lang,'pages':len(pdf),'source_docx_equal':values[0]==values[1],
            'source_pdf_equal':values[0]==values[2], 'source_html_equal':values[0]==values[3],
            'normalized_characters':list(map(len,values)),'out_of_bounds':bounds,
            'hyperlink_count':len(links),'doi_link_present':'https://doi.org/'+deposit['doi'] in links}
    for key in ('citation_doi','citation_author','citation_technical_report_number','citation_date'):
        want={'citation_doi':deposit['doi'],'citation_author':'Hongju Liu','citation_technical_report_number':'TA-TR-2026-08','citation_date':'2026/09/19'}[key]
        assert html.meta[key]==want,(lang,key)
    assert html.meta['citation_pdf_url'].endswith(stem(lang)+'.pdf')
    for index in range(1,4):
        if values[0]!=values[index]:
            k=next((j for j,(a,b) in enumerate(zip(values[0],values[index])) if a!=b),min(len(values[0]),len(values[index])))
            record['mismatch_'+str(index)]={'index':k,'expected':values[0][max(0,k-45):k+100],'actual':values[index][max(0,k-45):k+100]}
    detail.append(record)
refs=[manuscript_info(ROOT/f'manuscript-{lang}.md')['references'] for lang in ('en','zh')]
assert refs[0]==refs[1] and len(refs[0])==13
out=ROOT/'published'
csl=json.loads((out/'citation.csl.json').read_text())
assert csl['DOI']==deposit['doi'] and csl['title']==deposit['title'] and csl['number']=='TA-TR-2026-08' and csl['version']=='1.1'
assert csl['author']==[{'family':'Liu','given':'Hongju'}]
assert csl['issued']=={'date-parts':[[2026,9,19]]}
ris=dict(re.findall(r'^(\w{2})  - (.*)$',(out/'citation.ris').read_text(),re.M))
assert (ris['DO'],ris['TI'],ris['M1'],ris['ET'],ris['AU'])==(deposit['doi'],deposit['title'],'TA-TR-2026-08','1.1','Liu, Hongju')
bib=dict(re.findall(r'^  (\w+) = \{(.*)\},?$',(out/'citation.bib').read_text(),re.M))
assert (bib['doi'],bib['title'],bib['number'],bib['version'],bib['author'])==(deposit['doi'],deposit['title'],'TA-TR-2026-08','1.1','Liu, Hongju')
print(json.dumps(detail,ensure_ascii=False,indent=2))
assert all(x['source_docx_equal'] and x['source_pdf_equal'] and x['source_html_equal'] and x['doi_link_present'] and not x['out_of_bounds'] for x in detail)
report.update(source_docx_pdf_text_equal=True,reference_lists_identical=True,valid_citation_metadata=True,pdf_text_extractable=True,source_html_text_equal=True,actual_content_checks=detail)
(ROOT/'format-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
