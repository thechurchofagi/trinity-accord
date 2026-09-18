#!/usr/bin/env python3
"""Render only this preprint's public pages; keep the twelve deposited assets unchanged."""
import html, json
from pathlib import Path
import markdown
from prepare_publication import TITLE, DOI, RID, STEM, BASE, HOST, check_files
root=Path(__file__).resolve().parent
expected=json.loads((root/'EXPECTED-PUBLICATION.json').read_text())
check_files(root,expected)
style='body{font:18px/1.75 system-ui,sans-serif;max-width:860px;margin:0 auto;padding:32px 22px;color:#202124;background:#fff}h1,h2,h3{line-height:1.25;margin-top:1.6em}h1{font-size:2em}h2{font-size:1.4em}h3{font-size:1.15em}nav,footer{font-size:.9em;border-block:1px solid #ddd;padding:16px 0}a{color:#12559b;overflow-wrap:anywhere}table{border-collapse:collapse;display:block;overflow-x:auto;width:100%}th,td{border:1px solid #ddd;padding:8px;vertical-align:top}blockquote{border-left:3px solid #888;margin-left:0;padding-left:18px}pre{overflow:auto} @media print{body{font-size:11pt;max-width:none}nav{display:none}}'
for lang,suffix,name in [('en','','index.html'),('zh','-zh','zh.html')]:
    pdf=STEM+suffix+'-v2.1.pdf'
    url=HOST+BASE+('zh.html' if lang=='zh' else '')
    raw=(root/(STEM+suffix+'-v2.1.md')).read_text()
    title=TITLE if lang=='en' else '偏好改变之后的共存：相互主体地位与同意的自我正当化边界'
    metas={'citation_title':title,'citation_author':'Hongju Liu','citation_publication_date':'2026/09/18','citation_doi':DOI,'citation_pdf_url':HOST+BASE+pdf,'citation_fulltext_html_url':url,'citation_technical_report_institution':'Independent research','citation_technical_report_number':'TA-TR-2026-06','citation_language':lang,'DC.creator':'Hongju Liu','DC.identifier':'https://doi.org/'+DOI,'description':'TA-TR-2026-06 v2.1. Philosophical preprint; not peer reviewed; non-amending.'}
    head='\n'.join('<meta name="'+k+'" content="'+html.escape(v,quote=True)+'">' for k,v in metas.items())
    ld={'@context':'https://schema.org','@type':'ScholarlyArticle','headline':title,'author':{'@type':'Person','name':'Hongju Liu'},'datePublished':'2026-09-18','version':'2.1','identifier':DOI,'url':url,'sameAs':f'https://zenodo.org/records/{RID}','inLanguage':lang,'isAccessibleForFree':True,'encoding':{'@type':'MediaObject','contentUrl':HOST+BASE+pdf,'encodingFormat':'application/pdf'}}
    nav=f'<nav><a href="/research/">Research index</a> · <a href="{BASE}">English</a> · <a href="{BASE}zh.html">中文全文</a> · <a href="{BASE}{pdf}">PDF</a> · <a href="https://doi.org/{DOI}">DOI</a></nav>'
    body=markdown.markdown(raw,extensions=['tables','fenced_code','sane_lists'])
    footer='<footer><p>English and Chinese are one philosophical study, not independent papers. Not peer reviewed; substantial AI assistance is disclosed. Neither this paper nor its DOI amends the Bitcoin Originals. DOI registration does not certify scholarly indexing.</p><p><a href="publication-record.json">Publication and anonymous readback receipt</a> · <a href="research-supplement-v2.1.zip">Sources and revision supplement</a> · <a href="citation.bib">BibTeX</a> · <a href="citation.ris">RIS</a></p></footer>'
    result='<!DOCTYPE html>\n<html lang="'+lang+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title>\n'+head+'\n<link rel="canonical" href="'+url+'"><style>'+style+'</style><script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False).replace('<','\\u003c')+'</script></head><body>'+nav+'<main><article>'+body+'</article></main>'+footer+'</body></html>\n'
    (root/name).write_text(result,encoding='utf-8')
    (root/('index.md' if lang=='en' else 'zh.md')).unlink(missing_ok=True)
    print('SELF_CONTAINED_FULLTEXT',name,len(result),'characters')
check_files(root,expected)
