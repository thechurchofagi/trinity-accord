#!/usr/bin/env python3
"""Read-only draft inventory before the guarded publication worker."""
import json
import reserve as r
import publish
z=r.client()
try:
    for key,rid in [('a',23030207),('b',23030320)]:
        dep=z.request(f'/deposit/depositions/{rid}')
        rows=z.request(f'/deposit/depositions/{rid}/files')
        r.save(f'draft-inventory-{key}.json',{'record_id':rid,'submitted':dep.get('submitted'),
          'listing_type':type(rows).__name__,'files':rows,
          'deposition_file_summary':dep.get('files',[])})
    r.persist()
    publish.main()
finally:r.persist()
