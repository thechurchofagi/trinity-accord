#!/usr/bin/env python3
"""One bounded, hash-guarded refinement of unpublished TA-TR-2026-07 sources."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent
EXPECTED={'manuscript-en.md':'a8f837978ae6f32afb15641de98c3cdc5afc01e19e9136fbdee755613d013b92','manuscript-zh.md':'9228a434d710d1c7d8bebfbbbfdb403c88be851ee9575d2191d87bfa8a297ef9','REVIEW-AND-SOURCES.md':'de9ca6a6d114ccf550a41177f8ae2519809bf8b4be6a536da47c070ee06bbf28','build_publication.py':'7dfdf777ae6426a2b933d262424383918d490039216c7eb7c814096883fdc766'}
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def once(s,a,b):
    if s.count(a)!=1:raise RuntimeError('Refinement anchor is not unique: '+a[:70])
    return s.replace(a,b)
def main():
    receipt=ROOT/'source-refinement.json'
    if receipt.exists():
        r=json.loads(receipt.read_text())
        for name,v in r['files'].items():
            if digest((ROOT/name).read_text())!=v['after_sha256']:raise RuntimeError('Refined file changed; review explicitly before reapplying')
        print('SOURCE_REFINEMENT_ALREADY_APPLIED');return
    text={n:(ROOT/n).read_text() for n in EXPECTED}
    for n,h in EXPECTED.items():
        if digest(text[n])!=h:raise RuntimeError('Unreviewed starting bytes: '+n)
    en_add="Scanlon's *The Significance of Choice* (1986, Lecture 2, pp. 178-181) distinguishes instrumental, demonstrative and symbolic reasons to value choosing. The participation premise below draws on this established plurality; it does not treat all choice as intrinsically mandatory or all delegation as a loss.\n\nDutta and Kandala (2026, section 2.1) give a related temporal-evidence non-identifiability argument in mental-health AI evaluation. Our two-history construction uses the same elementary information-loss pattern, not a new mathematical result. Our question instead concerns ethically significant decision closure despite successful restoration; their empirical study is not evidence for our normative conclusions.\n\n"
    zh_add='Scanlon 的《选择的意义》（1986，第二讲，第 178—181 页）区分了选择的工具性、展现性与象征性价值。下文的参与前提借鉴这种既有的多元区分，而不是把所有选择都视为内在必需，也不把所有委托都视为损失。\n\nDutta 与 Kandala（2026，第 2.1 节）在心理健康人工智能评估中提出了相关的时间证据不可识别性论证。本文的两段历史构造采用相同的基本信息丢失模式，而不是新的数学结果。本文的问题转向成功恢复之后仍具有伦理意义的决定封闭；对方的实证研究并不是本文规范结论的证据。\n\n'
    text['manuscript-en.md']=once(text['manuscript-en.md'],'Technical work on the off-switch problem examines',en_add+'Technical work on the off-switch problem examines')
    text['manuscript-zh.md']=once(text['manuscript-zh.md'],'有关关闭开关问题的技术研究考察',zh_add+'有关关闭开关问题的技术研究考察')
    refs='\n[11] Dutta, S., and Kandala, R. (2026). Mental Health AI Safety Claims Must Preserve Temporal Evidence. arXiv:2605.08827, version 1. https://doi.org/10.48550/arXiv.2605.08827\n\n[12] Scanlon, T. M., Jr. (1986). The Significance of Choice. Tanner Lectures on Human Values, delivered at Brasenose College, Oxford, 16, 23 and 28 May 1986. Archived revised lecture text, pp. 151-216; cited discussion pp. 178-181. https://tannerlectures.org/wp-content/uploads/2024/07/Scanlon_The-Significance-of-Choice.pdf\n'
    for n in ('manuscript-en.md','manuscript-zh.md'):text[n]=text[n].rstrip()+'\n'+refs
    review_add='11. Srimonti Dutta and Ratna Kandala (2026), arXiv:2605.08827v1. Official abstract and section 2.1 checked. The related information-loss argument is explicitly acknowledged; its empirical findings are not used to validate this paper.\n\n12. T. M. Scanlon, *The Significance of Choice*, lectures delivered May 1986. Official archive and Lecture 2, printed pp. 178-181, checked, including PDF screenshots of pp. 178-180. Cited as a lecture text rather than guessing a journal publication date. The reference acknowledges the established plurality of choice values.\n\n'
    text['REVIEW-AND-SOURCES.md']=once(text['REVIEW-AND-SOURCES.md'],'No third-party full text or standalone font is included',review_add+'No third-party full text or standalone font is included')
    text['REVIEW-AND-SOURCES.md']=once(text['REVIEW-AND-SOURCES.md'],'the same ten references.','the same twelve references.')
    text['REVIEW-AND-SOURCES.md']=once(text['REVIEW-AND-SOURCES.md'],'No priority over all procedural, temporal-autonomy or exclusion literature is asserted.','The final literature pass additionally cites Scanlon on choice and Dutta and Kandala on temporal-evidence non-identifiability. No priority over all procedural, temporal-autonomy or exclusion literature is asserted.')
    text['build_publication.py']=once(text['build_publication.py'],'import argparse, hashlib, html, json, re, shutil, xml.etree.ElementTree as ET','import argparse, hashlib, html, json, os, re, shutil, xml.etree.ElementTree as ET')
    text['build_publication.py']=once(text['build_publication.py'],'ROOT=Path(__file__).resolve().parent',"os.environ['SOURCE_DATE_EPOCH']='1789776000'  # Fixed publication-day metadata, not a timestamp proof.\nROOT=Path(__file__).resolve().parent")
    text['build_publication.py']=once(text['build_publication.py'],"[str(i) for i in range(1,11)]","[str(i) for i in range(1,13)]")
    text['build_publication.py']=once(text['build_publication.py'],"'references':10","'references':12")
    changes={n:{'before_sha256':EXPECTED[n],'after_sha256':digest(s)} for n,s in text.items()}
    for n,s in text.items():(ROOT/n).write_text(s)
    receipt.write_text(json.dumps({'state':'PREPUBLICATION_SOURCE_REFINEMENT_APPLIED','files':changes,'new_references':[11,12],'reason':'Acknowledge additional direct antecedents in both full texts; keep novelty bounded. Set reproducible PDF metadata to the publication day, not ReportLab default year 2000.','published_records_modified':False},indent=2)+'\n')
    print(json.dumps(changes,indent=2))
if __name__=='__main__':main()
