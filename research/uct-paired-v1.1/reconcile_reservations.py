#!/usr/bin/env python3
"""Read/reconcile only the two UCT version families; resume once-only reservations.
No blind repeat of a new-version POST after an unresolved intent.
"""
import json, os, urllib.parse
import reserve as r

def valid_successor(d,oldid,concept):
    return (isinstance(d,dict) and d.get('id') not in (None,oldid)
            and str(d.get('conceptrecid',''))==concept and not d.get('submitted'))

def candidates(z,old,concept):
    found={}
    for name in ('latest_draft','latest','self'):
        link=old.get('links',{}).get(name)
        if not link:continue
        p=urllib.parse.urlsplit(link)
        if p.scheme!='https' or p.hostname!='zenodo.org' or not p.path.startswith('/api/deposit/depositions/'):continue
        d=z.request(link)
        if valid_successor(d,old['id'],concept):found[d['id']]=d
    # The API may return the new draft itself from newversion. Locate it by
    # concept identity rather than depending on one response-link convention.
    for page in range(1,11):
        rows=z.request('/deposit/depositions?'+urllib.parse.urlencode({'size':100,'page':page,'sort':'mostrecent'}))
        if not isinstance(rows,list):raise RuntimeError('Unexpected deposition-list schema')
        for d in rows:
            if valid_successor(d,old['id'],concept):found[d['id']]=d
        if len(rows)<100:break
    return list(found.values())

def main():
    z=r.client()
    for key,cfg in r.PAPERS.items():
        oldid=cfg['old_id'];old=z.request(f'/deposit/depositions/{oldid}')
        public=z.request(f'/records/{oldid}',authenticated=False)
        if old.get('id')!=oldid or not old.get('submitted') or str(old['metadata'].get('version'))!='1.0':
            raise RuntimeError('Prior identity mismatch')
        if public.get('doi')!=f'10.5281/zenodo.{oldid}' or not any(c.get('name')=='Liu, Hongju' for c in old['metadata'].get('creators',[])):
            raise RuntimeError('Prior author/DOI mismatch')
        concept=str(public['conceptrecid']);baseline=f'prior-public-{key}.json'
        if not (r.ROOT/baseline).exists():r.save(baseline,public);r.persist()
        name=f'deposit-{key}.json';intent=f'newversion-intent-{key}.json'
        if (r.ROOT/name).exists():
            ident=r.load(name);draft=z.request(f'/deposit/depositions/{int(ident["record_id"])}')
        else:
            matches=candidates(z,old,concept)
            r.save(f'reconciliation-{key}.json',{'old_id':oldid,'conceptrecid':concept,
                 'matching_unpublished_ids':[d['id'] for d in matches],
                 'old_link_ids':{k:urllib.parse.urlsplit(v).path for k,v in old.get('links',{}).items() if k in ('self','latest','latest_draft')}})
            r.persist()
            if len(matches)>1:raise RuntimeError('More than one matching successor; stop')
            if matches:
                if not (r.ROOT/intent).exists():raise RuntimeError('Unowned prior draft: no release intent')
                draft=matches[0]
            else:
                if (r.ROOT/intent).exists():raise RuntimeError('Prior POST unresolved; no repeat permitted')
                latest=public.get('links',{}).get('latest','')
                lid=urllib.parse.urlsplit(latest).path.rstrip('/').split('/')[-1]
                if lid.isdigit() and int(lid)!=oldid:raise RuntimeError('Newer edition exists')
                r.save(intent,{'state':'NEWVERSION_ONCE_INTENT','old_record_id':oldid,'version':'1.1','run_id':os.environ.get('GITHUB_RUN_ID'),'authorization':'Explicit user request to complete revisions through DOI publication, 2026-09-29.'});r.persist()
                response=z.request(f'/deposit/depositions/{oldid}/actions/newversion','POST')
                # Persist safe identity information immediately after the POST.
                r.save(f'newversion-response-{key}.json',{'id':response.get('id'),'submitted':response.get('submitted'),'conceptrecid':response.get('conceptrecid'),'links':{k:v for k,v in response.get('links',{}).items() if k in ('self','latest_draft','latest')}});r.persist()
                if valid_successor(response,oldid,concept):draft=response
                else:
                    refreshed=z.request(f'/deposit/depositions/{oldid}');matches=candidates(z,refreshed,concept)
                    if len(matches)!=1:raise RuntimeError('Cannot identify exact new successor; checkpoint retained')
                    draft=matches[0]
        if not valid_successor(draft,oldid,concept):raise RuntimeError('Only an unpublished same-family successor may be updated')
        if str(draft.get('metadata',{}).get('version','')) not in ('','1.0','1.1'):raise RuntimeError('Unexpected pending version')
        newid=int(draft['id'])
        # Record the ID before changing any draft metadata.
        r.save(name,{'state':'DRAFT_IDENTIFIED_NOT_PUBLISHED','record_id':newid,'doi':f'10.5281/zenodo.{newid}','conceptrecid':concept,'prior_record_id':oldid,'report_number':cfg['report'],'title':cfg['title'],'version':'1.1','submitted':False});r.persist()
        md={'upload_type':'publication','publication_type':'preprint','title':cfg['title'],
            'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
            'description':'<p>'+cfg['report']+' v1.1. Revised Unified Consciousness Theory preprint; not peer reviewed. Preserves the published v1.0 edition. Distinguishes ontic structure, scientific views, formal deductions, and empirical bridges. Finite-model checks are not empirical confirmation of experience.</p><p>Human author and responsible depositor: Hongju Liu. Substantial ChatGPT assistance, including GPT-6 Astra Pro for this revision. Adjacent non-amending research, not an amendment or independent corroboration of the Trinity Accord or its Bitcoin Originals.</p>',
            'publication_date':'2026-09-29','version':'1.1','access_right':'open','license':'cc-by-4.0','language':'eng',
            'keywords':['consciousness','structural identity','process ontology','causal organization','theory unification'],
            'related_identifiers':[{'identifier':f'10.5281/zenodo.{oldid}','relation':'isNewVersionOf','scheme':'doi'}], 'prereserve_doi':True}
        draft=z.request(f'/deposit/depositions/{newid}','PUT',{'metadata':md})
        doi=draft.get('metadata',{}).get('prereserve_doi',{}).get('doi') or draft.get('doi')
        if doi!=f'10.5281/zenodo.{newid}':raise RuntimeError('Reserved DOI mismatch')
        r.save(name,{'state':'RESERVED_NOT_PUBLISHED','record_id':newid,'doi':doi,'conceptrecid':concept,'prior_record_id':oldid,'report_number':cfg['report'],'title':cfg['title'],'version':'1.1','submitted':False,'old_published_files_modified':False,'run_id':os.environ.get('GITHUB_RUN_ID')});r.persist()
        print(key,doi,'RESERVED_NOT_PUBLISHED',flush=True)
if __name__=='__main__':
    try:main()
    finally:r.persist()
