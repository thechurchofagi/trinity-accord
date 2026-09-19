#!/usr/bin/env python3
"""Integrate the published seventh preprint, never edit older manuscripts."""
from pathlib import Path
import hashlib,json,re,shutil,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
DOI='10.5281/zenodo.22840604'
BASE='https://www.trinityaccord.org/research/recoverability-shared-time/'
def sha(b):return hashlib.sha256(b).hexdigest()
def gitsha(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def replace_once(s,a,b):
    if s.count(a)!=1:raise RuntimeError('Non-unique index anchor: '+a)
    return s.replace(a,b)
def main():
    rec=json.loads((ROOT/'publication-record.json').read_text());expected=json.loads((ROOT/'EXPECTED-PUBLICATION.json').read_text())
    if rec.get('state')!='PUBLISHED_AND_PUBLIC_READBACK_PASS' or rec.get('doi')!=DOI or rec.get('file_count')!=12 or rec.get('public_readback_authenticated') is not False:raise RuntimeError('Actual publication gate not complete')
    if sha((ROOT/'EXPECTED-PUBLICATION.json').read_bytes())!=rec['expected_manifest_sha256']:raise RuntimeError('Reviewed package changed')
    for f in expected['files']:
        p=ROOT/'published'/f['name'];b=p.read_bytes()
        if sha(b)!=f['sha256'] or len(b)!=f['bytes']:raise RuntimeError('Published mirror differs')
        if p.suffix=='.html':
            dest=ROOT/('zh.html' if '-zh-' in p.name else 'index.html')
            if dest.exists() and dest.read_bytes()!=b:raise RuntimeError('Existing full text differs')
            dest.write_bytes(b)
        elif p.suffix=='.pdf' or p.name in ('citation.bib','citation.ris','citation.csl.json','README-LICENSE.txt'):
            dest=ROOT/p.name
            if dest.exists() and dest.read_bytes()!=b:raise RuntimeError('Existing mirror differs')
            dest.write_bytes(b)
    index=REPO/'research/index.md';before=index.read_text();updated=before
    if '## Recoverability and Shared Time\n' not in before:
        if gitsha(index.read_bytes())!='7819e649c518eb088c09656c8018aabf3c20adf7':raise RuntimeError('Research index changed; inspect before applying integration')
        updated=replace_once(updated,'  - id: "citation-boundary"','  - id: "recoverability-and-shared-time"\n    title: "Recoverability and Shared Time"\n  - id: "citation-boundary"')
        updated=replace_once(updated,'**six distinct research papers (TA-TR-2026-01 through TA-TR-2026-06)**','**seven distinct research papers (TA-TR-2026-01 through TA-TR-2026-07)**')
        updated=replace_once(updated,'are not six independent corroborations.','are not seven independent corroborations.')
        updated=replace_once(updated,'for all six papers:','for the original six papers:')
        updated=replace_once(updated,'no single paper DOI represents all six studies.','no single paper DOI represents all seven studies.')
        updated=replace_once(updated,'the preferred citation for Paper 01 or the six-paper series.','the preferred citation for Paper 01 or the seven-paper series.')
        section='''## Recoverability and Shared Time
{: #recoverability-and-shared-time }

### Recoverability and Shared Time: The Ethics of AI Suspension, Resumption, and Coexistence

TA-TR-2026-07 · Version 1.0 · 19 September 2026. Human author of record and responsible depositor: Hongju Liu. Substantial literature research, conceptual development, critical revision, drafting and translation: GPT-6 Astra Pro under human direction.

A philosophical preprint separating internal recoverability, practical resumability and participation before a shared decision closes. It holds restored identity, memory and preferences fixed, then varies the external decision history. Eight paired case groups examine authorization, representation, emergencies, scarcity, serial suspension, speed asymmetry and branching. The normative conclusion depends on independently justified participation claims, not on a recovery checksum or an AI system's assertion of status.

**Status:** Published open-access preprint; not peer reviewed; non-amending. All twelve assets passed unauthenticated, complete-file SHA-256 readback; the DOI resolved to the correct public record. The English and complete Chinese texts are one study. The elementary separation argument is not claimed as a new mathematical theorem; direct prior work is acknowledged. No current AI consciousness, unlimited compute entitlement, empirical safety efficacy or Google Scholar indexing is asserted.

- [DOI: 10.5281/zenodo.22840604](https://doi.org/10.5281/zenodo.22840604) · [Zenodo record and twelve files](https://zenodo.org/records/22840604)
- [English full text](/research/recoverability-shared-time/) · [中文全文](/research/recoverability-shared-time/zh.html)
- [English PDF](/research/recoverability-shared-time/recoverability-and-shared-time-v1.0.pdf) · [中文 PDF](/research/recoverability-shared-time/recoverability-and-shared-time-zh-v1.0.pdf)
- [Publication receipt](/research/recoverability-shared-time/publication-record.json) · [Source comparison and substantive review](/research/recoverability-shared-time/REVIEW-AND-SOURCES.md) · [Exact-package visual review](/research/recoverability-shared-time/visual-review.json)
- [BibTeX](/research/recoverability-shared-time/citation.bib) · [RIS](/research/recoverability-shared-time/citation.ris) · [CSL-JSON](/research/recoverability-shared-time/citation.csl.json)

This is a separate seventh study, not the dated six-paper editorial supplement (DOI 10.5281/zenodo.22839629) and not a revision of an earlier deposit. It extends the coexistence discussion without independently corroborating the earlier papers. The seventh paper's new files are not covered by the earlier six-paper timestamp and Arweave batch.

'''
        updated=replace_once(updated,'## Citation boundary\n',section+'## Citation boundary\n')
        links=lambda s:set(re.findall(r'\]\(([^)]+)\)',s))
        if not links(before)<=links(updated):raise RuntimeError('Old research link removed')
        index.write_text(updated)
    elif DOI not in before:raise RuntimeError('Existing seventh section has wrong DOI')
    sitemap=REPO/'sitemap.xml';xml=sitemap.read_text();tree=ET.fromstring(xml);ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    previous=[e.text for e in tree.findall('s:url/s:loc',ns)]
    urls=[BASE,BASE+'zh.html'];added=[]
    for url in urls:
        if url not in previous:
            xml=replace_once(xml,'</urlset>','  <url><loc>'+url+'</loc><lastmod>2026-09-19</lastmod></url>\n</urlset>');added.append(url)
    after=[e.text for e in ET.fromstring(xml).findall('s:url/s:loc',ns)]
    if len(after)!=len(set(after)) or not set(previous)<=set(after):raise RuntimeError('Sitemap preservation failure')
    sitemap.write_text(xml)
    closeout='''# TA-TR-2026-07 publication closeout

**Recoverability and Shared Time: The Ethics of AI Suspension, Resumption, and Coexistence**

Version 1.0, 19 September 2026. DOI: 10.5281/zenodo.22840604.

The independent seventh paper is published, with twelve unauthenticated complete-file SHA-256 matches and successful DOI resolution recorded in publication-record.json. English PDF: 14 pages; Chinese PDF: 13 pages. Twelve references, eight paired case groups and seven explicit objections. Both complete PDF/HTML body texts were normalized and compared with Markdown; all 27 PDF pages were rendered and visually inspected. Two deterministic builds produced identical publication bytes.

This is a philosophical preprint, not peer reviewed and not a claim of exhaustive global originality. Substantial AI research and drafting, human responsibility and first-party project interests are disclosed. The direct prior-work comparison and the limits of the proposed contribution are documented in REVIEW-AND-SOURCES.md. No complete earlier seventh manuscript was recovered; this is the newly completed first public edition.

The website mirrors copy the exact published files and use self-contained scholarly full-text HTML. The research index preserves its previous link destinations and now lists seven distinct studies. The original six-paper critical-use guide remains a dated six-paper guide. No old manuscript, DOI asset, Bitcoin Original, timestamp target or Arweave record is modified. The old six-paper preservation bundle does not timestamp this new paper.

Publication, repository integration and live-site deployment are separate states. This note records publication and the prepared integration; live deployment must be checked independently after merge. Neither DOI registration nor format tests establish philosophical truth, peer review or indexing.
'''
    (ROOT/'PUBLICATION-CLOSEOUT.md').write_text(closeout)
    diagnostics={'state':'PUBLICATION_AND_SOURCE_INTEGRATION_PASS','publication_doi':DOI,'prior_index_blob':gitsha(before.encode()),'new_index_blob':gitsha(updated.encode()),'existing_link_destinations_preserved':True,'sitemap_added':added,'sitemap_url_count':len(after),'live_site_deployment':'NOT_YET_CHECKED','older_manuscripts_modified':False}
    (ROOT/'integration-checks.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
    print(json.dumps(diagnostics,indent=2))
    print('RELATED TEST FILES')
    for folder in ('scripts','tests'):
        for p in sorted((REPO/folder).glob('*research*')):print(p.relative_to(REPO))
    print('RELATED WORKFLOWS')
    for p in sorted((REPO/'.github/workflows').glob('*research*')):print(p.relative_to(REPO))
if __name__=='__main__':main()
