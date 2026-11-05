"""Read only the two owned UCT families and stop on unaccounted published editions."""
import reserve as r

def verify(z):
    concepts={'23005587','23008261'};found=[]
    for page in range(1,11):
        rows=z.request(f'/deposit/depositions?size=100&page={page}&sort=mostrecent')
        if not isinstance(rows,list):raise RuntimeError('Unexpected owned-deposition schema')
        for d in rows:
            if str(d.get('conceptrecid','')) in concepts:
                found.append({'id':d.get('id'),'conceptrecid':str(d.get('conceptrecid')),
                  'submitted':d.get('submitted'),'state':d.get('state'),
                  'version':d.get('metadata',{}).get('version'),'title':d.get('metadata',{}).get('title')})
        if len(rows)<100:break
    else:raise RuntimeError('Owned listing exceeded audit limit; no partial family inference')
    r.save('version-family-check.json',{'families':found,'accounted_record_ids':[23005588,23008262,23030207,23030320]});r.persist()
    extra=[d for d in found if d['submitted'] and d['id'] not in (23005588,23008262,23030207,23030320)]
    if extra:raise RuntimeError('Additional published family edition requires reconciliation: '+str([d['id'] for d in extra]))
