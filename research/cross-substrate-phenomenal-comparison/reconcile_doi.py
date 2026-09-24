#!/usr/bin/env python3
"""Read-only public DOI check; update only this paper's local status on success.
Never creates, edits, or republishes a Zenodo record.
"""
import datetime,json,urllib.request,urllib.parse,urllib.error
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[1]
RID=22934654
DOI='10.5281/zenodo.22934654'
def run():
 p=ROOT/'publication-record.json';receipt=json.loads(p.read_text())
 if (receipt.get('record_id'),receipt.get('doi'),receipt.get('version'))!=(RID,DOI,'1.0'):
  raise RuntimeError('Paper identity mismatch')
 if receipt.get('public_file_readback_pass') is not True or receipt.get('file_count')!=10:
  raise RuntimeError('Published complete-file readback is not established')
 if receipt.get('doi_resolution_pass') is True:
  print('DOI already verified; no action');return
 now=datetime.datetime.now(datetime.timezone.utc)
 if now.date()>datetime.date(2026,10,1):
  print('Automatic reconciliation window ended; receipt retains unresolved state');return
 try:
  req=urllib.request.Request('https://doi.org/'+DOI,headers={'User-Agent':'TrinityAccord-TA15-PublicDOIReconciliation/1.0'})
  with urllib.request.urlopen(req,timeout=25) as r:
   u=urllib.parse.urlsplit(r.url)
   ok=(r.status==200 and u.scheme=='https' and u.hostname=='zenodo.org' and not u.username and not u.password and u.port in (None,443) and not u.query and not u.fragment and u.path.rstrip('/') in (f'/records/{RID}',f'/record/{RID}'))
   if not ok: raise RuntimeError('DOI resolver returned a different target')
   resolver={'state':'RESOLVER_PASS','http_status':r.status,'final_url':r.url,'matches_record':True,'checked_at':now.isoformat(),'authenticated':False}
 except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as e:
  print('DOI resolution still pending:',type(e).__name__,getattr(e,'code',None));return
 receipt['state']='PUBLISHED_AND_PUBLIC_READBACK_PASS';receipt['doi_resolution_pass']=True;receipt['doi_resolver']=resolver
 p.write_text(json.dumps(receipt,indent=2)+'\n')
 a=ROOT/'publication-attempt.json';attempt=json.loads(a.read_text());attempt.update({'state':receipt['state'],'phase':'public_doi_reconciled','doi_reconciled_at':now.isoformat(),'zenodo_record_mutated':False});a.write_text(json.dumps(attempt,indent=2)+'\n')
 index=REPO/'research/index.md';s=index.read_text();old='DOI registration is assigned; resolver confirmation is still pending. The contribution is a comparison framework'
 s=s.replace(old,'The DOI resolves to the public record. The contribution is a comparison framework');index.write_text(s)
 print('DOI and complete publication now verified; only local receipt/index status updated')
if __name__=='__main__':run()
