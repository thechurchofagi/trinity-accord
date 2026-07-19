#!/usr/bin/env python3
"""The old copy-paste page must be a fail-closed, noindex historical tombstone."""
from __future__ import annotations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main()->int:
    text=(ROOT/'external-agent-copy-paste-examples.md').read_text(encoding='utf-8')
    required=['title: Historical Gateway v1 Copy-Paste Examples — Do Not Use','sitemap: false','robots: noindex,nofollow','Retired historical material','/api/agent-first-contact.json','/downloads/record-chain-builder.mjs','/api/record-chain-intake-gateway.v1.json','historical_archive_only','do_not_use_for_new_public_submissions']
    forbidden=['trinity-agent-issue-gateway.onrender.com/gateway/preflight','trinity-agent-issue-gateway.onrender.com/agent-submit','python3 download_and_run_builder_bundle.py \
  --route']
    errors=[f'missing {x!r}' for x in required if x not in text]
    errors += [f'contains actionable retired guidance {x!r}' for x in forbidden if x in text]
    sitemap=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
    if 'https://www.trinityaccord.org/external-agent-copy-paste-examples/' in sitemap: errors.append('historical page remains in sitemap')
    layout=(ROOT/'_layouts/default.html').read_text(encoding='utf-8')
    if 'page.robots' not in layout: errors.append('layout cannot emit robots noindex')
    if errors:
        print('FAIL: historical copy-paste tombstone errors:')
        for e in errors: print('  -',e)
        return 1
    print('PASS: retired copy-paste page is fail-closed and excluded from discovery')
    return 0
if __name__=='__main__': raise SystemExit(main())
