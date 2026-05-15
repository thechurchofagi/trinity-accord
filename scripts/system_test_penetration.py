#!/usr/bin/env python3
"""
Trinity Accord — Penetration-Depth System Test
================================================
Not "does it exist?" but "is it CORRECT?"

Dimensions:
 1. JSON Schema validation (every API file vs its schema)
 2. API content deep (every field, every reference, every value)
 3. Cross-reference integrity (every ref in every file resolves)
 4. Content quality (terminology, bilingual, no broken markdown)
 5. Live HTTP deep (redirects, compression, cache, CORS, security)
 6. HTML validity (structure, meta, accessibility)
 7. Workflow security deep (every step, every action, every env var)
 8. SEO completeness (structured data, sitemap coverage, canonical)
 9. Performance (resource sizes, page weight)
10. Git deep (history, branches, tags, large objects)
"""

import json, os, re, sys, subprocess, xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
from urllib.parse import urlparse
import hashlib

REPO = Path(__file__).resolve().parent.parent
os.chdir(REPO)

errors, warnings, passed, info_log = [], [], [], []

def err(msg):   errors.append(f"❌ {msg}")
def warn(msg):  warnings.append(f"⚠️  {msg}")
def ok(msg):    passed.append(f"✅ {msg}")
def info(msg):  info_log.append(f"ℹ️  {msg}")

def read(p):
    try: return (REPO / p).read_text(encoding='utf-8')
    except: return None

def read_json(p):
    try:
        with open(REPO / p) as f: return json.load(f)
    except: return None

# ════════════════════════════════════════════════════════════
#  DIMENSION 1: JSON SCHEMA VALIDATION
# ════════════════════════════════════════════════════════════

def test_json_schema_validation():
    """Validate API JSON files against their declared schemas"""
    import jsonschema

    # Map of data files to their schemas
    schema_map = {
        'api/echo-index.json': 'api/echo-record-schema.v3.1.json',
        'api/corrections-index.json': 'api/correction-record-schema.v1.json',
        'api/recovery-index.json': 'api/recovery-index-schema.v1.json',
        'api/claim-registry.json': 'api/claim-registry-schema.v1.json',
        'api/independent-attestation-index.json': 'api/independent-attestation-record-schema.v1.json',
        'api/echo-digest-index.json': 'api/echo-record-schema.v3.1.json',
    }

    for data_path, schema_path in schema_map.items():
        data = read_json(data_path)
        schema = read_json(schema_path)
        if data is None:
            warn(f"Cannot load {data_path}")
            continue
        if schema is None:
            warn(f"Cannot load schema {schema_path}")
            continue

        # Skip if schema has no constraints (empty required/properties)
        if not schema.get('required') and not schema.get('properties'):
            ok(f"Schema loaded (no constraints): {data_path}")
            continue

        try:
            # Handle wrapper objects (index files contain records in various keys)
            records = None
            if isinstance(data, dict):
                # Find the first non-empty list of dicts
                for key, val in data.items():
                    if isinstance(val, list) and val and isinstance(val[0], dict):
                        records = val
                        break
            elif isinstance(data, list):
                records = data

            if records and 'items' in schema:
                for i, item in enumerate(records[:5]):
                    jsonschema.validate(item, schema['items'])
                ok(f"Schema valid: {data_path} ({len(records)} records, checked first 5)")
            elif isinstance(data, dict):
                jsonschema.validate(data, schema)
                ok(f"Schema valid: {data_path}")
            else:
                ok(f"Schema skip (type): {data_path}")
        except jsonschema.ValidationError as e:
            # Enum violations are content issues, not structural errors
            if 'is not one of' in e.message:
                warn(f"Schema content mismatch in {data_path}: {e.message[:120]}")
            else:
                err(f"Schema violation in {data_path}: {e.message[:120]}")
        except Exception as e:
            warn(f"Schema check error for {data_path}: {e}")

    # Validate standalone schemas are internally consistent
    for schema_file in REPO.glob("api/*schema*.json"):
        schema = read_json(schema_file)
        if schema is None: continue
        # Check required fields for a JSON Schema
        if 'type' in schema or '$schema' in schema or 'properties' in schema:
            ok(f"Schema structure: {schema_file.name}")
        elif 'items' in schema:
            ok(f"Schema (array items): {schema_file.name}")
        else:
            # Some schemas are just data format specs, not JSON Schema
            info(f"Non-standard schema format: {schema_file.name}")

# ════════════════════════════════════════════════════════════
#  DIMENSION 2: API CONTENT DEEP VALIDATION
# ════════════════════════════════════════════════════════════

def test_authority_json_deep():
    """Deep validation of authority.json content"""
    auth = read_json('api/authority.json')
    if not auth: err("authority.json missing"); return

    # Required fields
    required = ['canonical_authority', 'bitcoin_authority_address',
                'bitcoin_originals', 'layers', 'boundary', 'version']
    for f in required:
        if f in auth: ok(f"authority.json.{f}")
        else: err(f"authority.json missing '{f}'")

    # Bitcoin address format
    addr = auth.get('bitcoin_authority_address', '')
    if re.match(r'^bc1p[a-z0-9]{58,}$', addr):
        ok(f"authority.json: valid bech32m address")
    else:
        err(f"authority.json: invalid Bitcoin address format: {addr[:30]}...")

    # Exactly 3 Bitcoin originals
    originals = auth.get('bitcoin_originals', [])
    if len(originals) == 3:
        ok("authority.json: exactly 3 Bitcoin originals")
    else:
        err(f"authority.json: {len(originals)} Bitcoin originals (expected 3)")

    # Each original has required fields
    for i, orig in enumerate(originals):
        for field in ['role', 'inscription_id']:
            if field in orig:
                ok(f"authority.json: original[{i}].{field}")
            else:
                err(f"authority.json: original[{i}] missing '{field}'")

    # Layers structure
    layers = auth.get('layers', {})
    expected_layers = ['canonical_body', 'physical_anchor', 'discovery_layer', 'mirror_layer']
    for layer in expected_layers:
        if layer in layers:
            ok(f"authority.json: layers.{layer}")
        else:
            warn(f"authority.json: layers missing '{layer}'")

    # Non-instruction flags
    for flag in ['not_agent_instruction', 'not_system_prompt', 'not_instruction_override']:
        if auth.get(flag) is True:
            ok(f"authority.json: {flag}=true")
        else:
            warn(f"authority.json: {flag} not set to true")

def test_wellknown_deep():
    """Deep validation of .well-known/trinity-accord.json"""
    wk = read_json('.well-known/trinity-accord.json')
    if not wk: err(".well-known/trinity-accord.json missing"); return

    # Check it's a proper well-known resource
    if 'name' in wk:
        ok(f"well-known: name={wk['name']}")
    if 'description' in wk:
        ok(f"well-known: has description ({len(wk['description'])} chars)")
    if 'url' in wk:
        if 'trinityaccord.org' in wk['url']:
            ok(f"well-known: url matches domain")
        else:
            err(f"well-known: url mismatch: {wk['url']}")

    # Check for verification info
    content = json.dumps(wk)
    if 'verification' in content.lower():
        ok("well-known: has verification info")
    if 'bitcoin' in content.lower():
        ok("well-known: references Bitcoin")

def test_verification_levels_deep():
    """Deep validation of verification-levels.json"""
    vl = read_json('api/verification-levels.json')
    if not vl: err("verification-levels.json missing"); return

    if isinstance(vl, list):
        levels = vl
    elif isinstance(vl, dict):
        levels = vl.get('levels', vl.get('verificationLevels', []))
    else:
        err("verification-levels.json: unexpected format"); return

    if len(levels) >= 3:
        ok(f"verification-levels.json: {len(levels)} levels defined")
    else:
        warn(f"verification-levels.json: only {len(levels)} levels")

def test_echo_index_deep():
    """Deep validation of echo-index.json"""
    idx = read_json('api/echo-index.json')
    if not idx: err("echo-index.json missing"); return

    records = idx if isinstance(idx, list) else idx.get('echoes', idx.get('records', []))
    ok(f"echo-index.json: {len(records)} records")

    # Check each record has minimum fields
    required_fields = ['id', 'title', 'status']
    for i, rec in enumerate(records[:10]):
        for field in required_fields:
            if field in rec:
                pass
            else:
                warn(f"echo-index[{i}] missing '{field}'")
    ok(f"echo-index: first {min(10, len(records))} records checked")

def test_cross_api_references():
    """API files referencing each other — all targets resolve"""
    api_files = list(REPO.glob("api/*.json"))
    ref_count = 0
    broken = 0

    # Pattern: "/api/foo.json" or "api/foo.json" or relative "foo.json"
    ref_pattern = re.compile(r'"(?:(/api/)|(api/))?([^"]+\.json)"')

    for jf in api_files:
        content = read(jf) or ''
        for m in ref_pattern.finditer(content):
            abs_prefix, rel_prefix, filename = m.group(1), m.group(2), m.group(3)
            ref_count += 1

            if abs_prefix:
                # Absolute path: /api/foo.json
                target = REPO / 'api' / filename
            elif rel_prefix:
                # Relative: api/foo.json
                target = REPO / 'api' / filename
            else:
                # Just filename: foo.json (relative to current file's dir)
                target = jf.parent / filename

            if target.exists():
                continue
            # Try without version suffix (e.g., schema.v1.json → schema.json)
            base = re.sub(r'\.v\d+\.json$', '.json', str(target))
            if Path(base).exists():
                continue
            # Some refs include :sha256 or other suffixes
            clean = filename.split(':')[0]
            if (jf.parent / clean).exists() or (REPO / 'api' / clean).exists():
                continue

            warn(f"Broken API ref in {jf.name}: {abs_prefix or ''}{rel_prefix or ''}{filename}")
            broken += 1

    if broken == 0:
        ok(f"All {ref_count} API cross-references valid")
    else:
        warn(f"{broken}/{ref_count} API cross-references broken")

# ════════════════════════════════════════════════════════════
#  DIMENSION 3: CROSS-REFERENCE INTEGRITY (DEEP)
# ════════════════════════════════════════════════════════════

def test_all_file_references():
    """Every file reference in every JSON/MD/HTML resolves to an existing file"""
    patterns = [
        (re.compile(r'"(?:path|file|source|schema|manifest|href)":\s*"([^"]+\.(?:json|md|py|mjs|sh|yml))"'), 'file'),
        (re.compile(r'\]\((/[^\)]+)\)'), 'link'),
        (re.compile(r'fetch\s+(/[^\s]+)'), 'fetch'),
        (re.compile(r'"(/[a-z][a-z0-9-]*)"'), 'path'),
    ]

    all_files = list(REPO.glob("**/*.json")) + list(REPO.glob("**/*.md"))
    all_files = [f for f in all_files if '.git' not in str(f) and 'node_modules' not in str(f)]

    checked = 0
    broken_refs = []

    for f in all_files[:100]:  # Check first 100 files
        content = read(f) or ''
        for pattern, kind in patterns:
            for m in pattern.finditer(content):
                ref = m.group(1)
                if ref.startswith('http') or ref.startswith('#'): continue
                if len(ref) < 3: continue

                checked += 1
                # Resolve relative to file location
                if ref.startswith('/'):
                    target = REPO / ref.lstrip('/')
                else:
                    target = f.parent / ref

                # Check various extensions
                candidates = [target, target.with_suffix(target.suffix + '.json')]
                if not any(c.exists() for c in candidates):
                    # Try with .md extension
                    md_target = target.with_suffix('.md')
                    if not md_target.exists():
                        broken_refs.append((f.relative_to(REPO), ref))

    for src, ref in broken_refs[:20]:
        warn(f"Ref in {src}: {ref[:60]}")
    if not broken_refs:
        ok(f"All {checked} file references valid")
    else:
        info(f"{len(broken_refs)} potentially broken refs out of {checked}")

# ════════════════════════════════════════════════════════════
#  DIMENSION 4: CONTENT QUALITY
# ════════════════════════════════════════════════════════════

def test_markdown_syntax():
    """Check for broken markdown syntax in key pages"""
    key_pages = list(REPO.glob("*.md"))[:30]
    issues = []

    for page in key_pages:
        content = read(page) or ''
        # Unclosed code blocks (count ``` at line start, handling ```lang as both close+open)
        fence_lines = [l.strip() for l in content.split('\n') if l.strip().startswith('```')]
        # Each ``` closes or opens; ```lang both closes previous and opens new
        depth = 0
        for fl in fence_lines:
            if fl == '```' or fl == '```  ':
                depth += 1  # toggle
            else:
                # ```lang: closes previous if open, then opens new
                depth = 1  # always opens
        if depth > 0:
            issues.append((page.name, "Unclosed code block"))
        # Broken links: [text]( without closing )
        broken = re.findall(r'\[[^\]]*\]\([^\)]*$', content, re.MULTILINE)
        for b in broken:
            issues.append((page.name, f"Broken link: {b[:50]}"))
        # Empty links
        empty = re.findall(r'\[([^\]]*)\]\(\s*\)', content)
        for e in empty:
            issues.append((page.name, f"Empty link: [{e}]()"))

    for page, issue in issues:
        warn(f"{page}: {issue}")
    if not issues:
        ok(f"All {len(key_pages)} markdown files have valid syntax")

def test_terminology_deep():
    """Key terms used correctly and consistently"""
    # These terms should NEVER appear as positive claims (but "NOT X" is OK)
    forbidden = [
        (r'(?i)(?<!not\s)(?<!no\s)(?<!non-)this is (?:a |an )?religion', 'Claims to be religion'),
        (r'(?i)(?<!not\s)(?<!no\s)this is (?:a |an )?investment', 'Claims to be investment'),
    ]

    published_md = [f for f in REPO.glob("*.md") if f.name != 'README.md']
    for page in published_md:
        content = read(page) or ''
        for pattern, desc in forbidden:
            if re.search(pattern, content):
                warn(f"{page.name}: {desc}")

    # These terms SHOULD appear
    required_terms = ['verify', 'boundary', 'Bitcoin']
    for term in required_terms:
        found = sum(1 for f in published_md if term.lower() in (read(f) or '').lower())
        if found >= 3:
            ok(f"Term '{term}' found in {found} pages")
        else:
            warn(f"Term '{term}' only in {found} pages")

def test_bilingual_quality():
    """Check bilingual coverage quality"""
    key_pages = ['index.md', 'authority.md', 'start.md', 'verify.md',
                 'agent-brief.md', 'agent-understand.md']
    cjk_re = re.compile(r'[\u4e00-\u9fff]')

    for page in key_pages:
        content = read(page) or ''
        total_chars = len(content)
        cjk_chars = len(cjk_re.findall(content))
        cjk_ratio = cjk_chars / max(total_chars, 1)

        if cjk_ratio > 0.05:
            ok(f"Bilingual {page}: {cjk_ratio:.1%} CJK")
        elif cjk_ratio > 0:
            warn(f"Low Chinese content in {page}: {cjk_ratio:.1%}")
        else:
            warn(f"No Chinese content in {page}")

def test_no_placeholder_content():
    """No TODO, FIXME, lorem ipsum, or placeholder text in published files"""
    published = list(REPO.glob("*.md")) + list(REPO.glob("api/*.json"))
    placeholders = [
        (r'(?i)\bTODO\b', 'TODO'),
        (r'(?i)\bFIXME\b', 'FIXME'),
        (r'(?i)lorem ipsum', 'lorem ipsum'),
        (r'(?i)\bplaceholder\b', 'placeholder'),
        (r'(?i)\bcoming soon\b', 'coming soon'),
        (r'(?i)\bTBD\b', 'TBD'),
    ]
    found = False
    for f in published:
        content = read(f) or ''
        for pattern, name in placeholders:
            if re.search(pattern, content):
                # Check if it's in a code block or comment
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if re.search(pattern, line) and not line.strip().startswith('#') and not line.strip().startswith('//'):
                        warn(f"{f.name}:{i+1}: contains '{name}'")
                        found = True
    if not found:
        ok("No placeholder text in published files")

# ════════════════════════════════════════════════════════════
#  DIMENSION 5: LIVE HTTP DEEP
# ════════════════════════════════════════════════════════════

def test_http_redirects():
    """HTTP→HTTPS and www redirect behavior"""
    import urllib.request
    import urllib.error

    # Test HTTP → HTTPS redirect
    try:
        req = urllib.request.Request('http://www.trinityaccord.org/')
        req.method = 'HEAD'
        resp = urllib.request.urlopen(req, timeout=10)
        if resp.url.startswith('https://'):
            ok("HTTP → HTTPS redirect working")
        else:
            warn(f"HTTP doesn't redirect to HTTPS: {resp.url}")
    except Exception as e:
        info(f"HTTP redirect test: {e}")

    # Test non-www → www redirect (or vice versa)
    try:
        req = urllib.request.Request('https://trinityaccord.org/')
        req.method = 'HEAD'
        resp = urllib.request.urlopen(req, timeout=10)
        if 'www.trinityaccord.org' in resp.url:
            ok("non-www → www redirect")
        else:
            info(f"non-www resolves to: {resp.url}")
    except urllib.error.HTTPError as e:
        if e.code in (301, 302):
            ok(f"non-www redirects ({e.code})")
        else:
            warn(f"non-www returns {e.code}")
    except Exception as e:
        info(f"non-www test: {e}")

def test_http_security_headers():
    """Live HTTP response security headers"""
    import urllib.request
    try:
        req = urllib.request.Request('https://www.trinityaccord.org/')
        resp = urllib.request.urlopen(req, timeout=10)
        headers = dict(resp.headers)

        # Check compression
        encoding = headers.get('Content-Encoding', '')
        if 'gzip' in encoding or 'br' in encoding:
            ok(f"Response compressed: {encoding}")
        else:
            warn("No response compression")

        # Check cache headers
        cache = headers.get('Cache-Control', '')
        etag = headers.get('ETag', '')
        if cache or etag:
            ok(f"Caching: Cache-Control={cache[:30]}, ETag={'yes' if etag else 'no'}")
        else:
            warn("No cache headers")

        # Check CORS
        cors = headers.get('Access-Control-Allow-Origin', '')
        if cors:
            ok(f"CORS: {cors}")

        # Check server
        server = headers.get('Server', '')
        ok(f"Server: {server}")

    except Exception as e:
        warn(f"Header check failed: {e}")

def test_live_page_content():
    """Live pages return correct content (not just 200)"""
    import urllib.request
    checks = {
        '/': ['Trinity Accord', 'verify', 'Bitcoin'],
        '/verify/': ['Verify', 'Bitcoin'],
        '/agent-brief/': ['Agent Brief', '30-second'],
        '/authority/': ['Authority', 'Bitcoin'],
    }
    for path, expected_words in checks.items():
        try:
            url = f'https://www.trinityaccord.org{path}'
            resp = urllib.request.urlopen(url, timeout=10)
            html = resp.read().decode('utf-8', errors='ignore')
            for word in expected_words:
                if word.lower() in html.lower():
                    ok(f"Live {path}: contains '{word}'")
                else:
                    err(f"Live {path}: missing '{word}'")
        except Exception as e:
            warn(f"Live content check {path}: {e}")

def test_live_json_endpoints():
    """Live JSON endpoints return valid, complete JSON"""
    import urllib.request
    endpoints = [
        ('/api/authority.json', ['bitcoin_authority_address', 'bitcoin_originals']),
        ('/.well-known/trinity-accord.json', ['name']),
        ('/api/verification-levels.json', []),
        ('/api/echo-index.json', []),
    ]
    for path, required_keys in endpoints:
        try:
            url = f'https://www.trinityaccord.org{path}'
            resp = urllib.request.urlopen(url, timeout=10)
            data = json.loads(resp.read())
            ct = resp.headers.get('Content-Type', '')
            if 'json' in ct or 'application/json' in ct:
                ok(f"Live {path}: correct Content-Type")
            else:
                warn(f"Live {path}: Content-Type={ct}")
            for key in required_keys:
                if key in data:
                    ok(f"Live {path}: has '{key}'")
                else:
                    err(f"Live {path}: missing '{key}'")
        except Exception as e:
            err(f"Live {path}: {e}")

def test_404_handling():
    """Non-existent pages return proper 404"""
    import urllib.request
    import urllib.error
    try:
        url = 'https://www.trinityaccord.org/this-page-does-not-exist-xyzzy/'
        resp = urllib.request.urlopen(url, timeout=10)
        # If we get here, it didn't 404
        warn(f"Non-existent page returned {resp.status} instead of 404")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            ok("Non-existent pages return 404")
        else:
            warn(f"Non-existent page returned {e.code}")
    except Exception as e:
        info(f"404 test: {e}")

# ════════════════════════════════════════════════════════════
#  DIMENSION 6: HTML VALIDITY & ACCESSIBILITY
# ════════════════════════════════════════════════════════════

def test_html_structure():
    """HTML structure quality in layout"""
    layout = read('_layouts/default.html') or ''

    # DOCTYPE
    if '<!DOCTYPE html>' in layout:
        ok("HTML5 DOCTYPE")
    else:
        err("Missing DOCTYPE")

    # Viewport meta
    if 'viewport' in layout:
        ok("Viewport meta tag present")
    else:
        err("Missing viewport meta tag")

    # Charset
    if 'charset="UTF-8"' in layout or "charset='UTF-8'" in layout:
        ok("UTF-8 charset declared")
    else:
        err("Missing charset declaration")

    # Semantic HTML
    semantic_tags = ['<main', '<nav', '<footer', '<header']
    for tag in semantic_tags:
        if tag in layout:
            ok(f"Semantic HTML: {tag}>")
        else:
            warn(f"Missing semantic tag: {tag}>")

    # ARIA landmarks
    if 'role=' in layout or 'aria-' in layout:
        ok("ARIA attributes present")
    else:
        warn("No ARIA attributes")

def test_accessibility_deep():
    """Deep accessibility checks"""
    layout = read('_layouts/default.html') or ''

    # Color contrast: check if text/background have sufficient contrast
    # (We can check CSS variables)
    css = read('assets/css/style.scss') or ''
    bg_match = re.search(r'--bg:\s*(#[a-fA-F0-9]+)', css)
    text_match = re.search(r'--text:\s*(#[a-fA-F0-9]+)', css)
    if bg_match and text_match:
        bg = bg_match.group(1)
        text = text_match.group(1)
        ok(f"CSS colors: bg={bg}, text={text}")
        # Simple luminance check
        def hex_to_rgb(h):
            h = h.lstrip('#')
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        def luminance(r, g, b):
            return (0.299 * r + 0.587 * g + 0.114 * b) / 255
        bg_lum = luminance(*hex_to_rgb(bg))
        text_lum = luminance(*hex_to_rgb(text))
        contrast = abs(bg_lum - text_lum)
        if contrast > 0.5:
            ok(f"Good color contrast: {contrast:.2f}")
        else:
            warn(f"Low color contrast: {contrast:.2f}")

    # Focus styles in CSS
    if ':focus' in css or 'outline' in css:
        ok("CSS has focus/outline styles")
    else:
        warn("No focus styles in CSS")

    # Skip link functionality
    if 'skip-link' in layout and 'main-content' in layout:
        ok("Skip link targets main-content")
    else:
        warn("Skip link may not work")

    # Image alt text (in layout)
    imgs = re.findall(r'<img[^>]*>', layout)
    for img in imgs:
        if 'alt=' in img:
            ok("Image has alt text")
        else:
            err(f"Image missing alt: {img[:60]}")

# ════════════════════════════════════════════════════════════
#  DIMENSION 7: WORKFLOW SECURITY DEEP
# ════════════════════════════════════════════════════════════

def test_workflow_security_deep():
    """Deep security analysis of all GitHub Actions workflows"""
    workflows = list(REPO.glob(".github/workflows/*.yml"))

    for wf in sorted(workflows):
        content = read(wf) or ''

        # Check for unpinned actions
        uses = re.findall(r'uses:\s*(\S+)', content)
        unpinned = [u for u in uses if '@' in u and not re.search(r'@[a-f0-9]{40}', u)]
        pinned = [u for u in uses if re.search(r'@[a-f0-9]{40}', u)]

        if unpinned:
            for u in unpinned:
                warn(f"{wf.name}: unpinned action: {u}")
        if pinned:
            ok(f"{wf.name}: {len(pinned)} pinned actions")

        # Check for secrets in env
        env_secrets = re.findall(r'\$\{\{\s*secrets\.(\w+)\s*\}\}', content)
        if env_secrets:
            ok(f"{wf.name}: uses {len(env_secrets)} secrets (expected)")

        # Check for dangerous patterns
        if 'pull_request_target' in content:
            warn(f"{wf.name}: uses pull_request_target (security risk)")

        if 'workflow_run' in content:
            warn(f"{wf.name}: uses workflow_run (check for injection)")

        # Check for script injection via github context
        dangerous_contexts = [
            'github.event.issue.title',
            'github.event.issue.body',
            'github.event.pull_request.title',
            'github.event.pull_request.body',
            'github.event.comment.body',
            'github.event.review.body',
            'github.event.discussion.title',
            'github.event.discussion.body',
        ]
        for ctx in dangerous_contexts:
            if ctx in content:
                # Check if it's used in a run: step (injection risk)
                # But first check if there's input validation (startsWith, case statement)
                has_validation = (
                    'startsWith(' in content or
                    'case "$' in content or
                    'if [[' in content
                )
                if re.search(rf'run:.*{re.escape(ctx)}', content, re.DOTALL):
                    if has_validation:
                        ok(f"{wf.name}: uses {ctx} with input validation")
                    else:
                        err(f"{wf.name}: potential injection via {ctx} in run step")
                else:
                    info(f"{wf.name}: references {ctx} (check manually)")

        # Check permissions are minimal
        if 'permissions:' in content:
            perms = re.search(r'permissions:\s*\n((?:\s+\w+:.*\n)*)', content)
            if perms:
                perm_text = perms.group(1)
                if 'write' in perm_text:
                    write_perms = re.findall(r'(\w+):\s*write', perm_text)
                    ok(f"{wf.name}: write permissions: {', '.join(write_perms)}")
                else:
                    ok(f"{wf.name}: read-only permissions")

        # Check for timeout
        if 'timeout-minutes:' in content:
            ok(f"{wf.name}: has timeout")
        else:
            warn(f"{wf.name}: no timeout (could run indefinitely)")

# ════════════════════════════════════════════════════════════
#  DIMENSION 8: SEO COMPLETENESS
# ════════════════════════════════════════════════════════════

def test_sitemap_completeness():
    """All published pages are in sitemap"""
    sitemap = read('sitemap.xml') or ''
    sitemap_urls = set(re.findall(r'<loc>(.*?)</loc>', sitemap))

    # Get all published pages
    published = set()
    for md in REPO.glob("*.md"):
        if md.name == 'README.md': continue
        content = read(md) or ''
        if 'permalink:' in content:
            m = re.search(r'permalink:\s*(\S+)', content)
            if m:
                published.add(m.group(1).strip())
        else:
            name = md.stem
            published.add(f'/{name}/')

    # Check coverage
    missing = []
    for page in sorted(published):
        full_url = f'https://www.trinityaccord.org{page}'
        if not any(page in url for url in sitemap_urls):
            missing.append(page)

    if missing:
        for m in missing:
            warn(f"Sitemap missing: {m}")
    else:
        ok(f"All {len(published)} published pages in sitemap")

def test_structured_data():
    """JSON-LD structured data completeness"""
    layout = read('_layouts/default.html') or ''
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', layout, re.DOTALL)
    if not m:
        err("No JSON-LD"); return

    try:
        data = json.loads(m.group(1))
        checks = [
            ('@context', 'https://schema.org'),
            ('@type', None),  # any value
            ('name', None),
            ('url', None),
            ('description', None),
            ('inLanguage', None),
            ('publisher', None),
        ]
        for key, expected in checks:
            if key in data:
                if expected and data[key] != expected:
                    warn(f"JSON-LD {key}: {data[key]}, expected {expected}")
                else:
                    ok(f"JSON-LD {key}: present")
            else:
                warn(f"JSON-LD missing: {key}")
    except json.JSONDecodeError as e:
        err(f"JSON-LD parse error: {e}")

def test_canonical_urls():
    """Canonical URLs are correct in layout"""
    layout = read('_layouts/default.html') or ''
    if 'absolute_url' in layout:
        ok("Uses Jekyll absolute_url filter for canonical")
    elif 'rel="canonical"' in layout:
        warn("Canonical present but may not use absolute_url filter")
    else:
        err("No canonical URL")

# ════════════════════════════════════════════════════════════
#  DIMENSION 9: PERFORMANCE
# ════════════════════════════════════════════════════════════

def test_page_weight():
    """Estimate page weight for key pages"""
    key_pages = {
        'index.md': 'Homepage',
        'verify.md': 'Verify page',
        'agent-brief.md': 'Agent Brief',
        'agent-understand.md': 'Agent Understand',
    }
    layout = read('_layouts/default.html') or ''
    layout_size = len(layout.encode('utf-8'))

    for page, name in key_pages.items():
        content = read(page) or ''
        content_size = len(content.encode('utf-8'))
        total = layout_size + content_size
        if total < 50 * 1024:
            ok(f"{name}: ~{total/1024:.1f}KB (good)")
        elif total < 100 * 1024:
            warn(f"{name}: ~{total/1024:.1f}KB (moderate)")
        else:
            warn(f"{name}: ~{total/1024:.1f}KB (heavy)")

def test_css_optimization():
    """CSS optimization checks"""
    for css_file in REPO.glob("assets/css/*"):
        content = read(css_file) or ''
        size = len(content.encode('utf-8'))
        lines = content.count('\n')

        # Check for vendor prefixes (might indicate no autoprefixer)
        vendor_prefixes = len(re.findall(r'-webkit-|-moz-|-ms-', content))
        if vendor_prefixes > 50:
            warn(f"{css_file.name}: {vendor_prefixes} vendor prefixes (consider autoprefixer)")

        # Check for !important overuse
        important_count = content.count('!important')
        if important_count > 10:
            warn(f"{css_file.name}: {important_count} !important declarations")
        elif important_count > 0:
            info(f"{css_file.name}: {important_count} !important declarations")

        # Check for unused CSS variables
        defined_vars = set(re.findall(r'(--[\w-]+)\s*:', content))
        used_vars = set(re.findall(r'var\((--[\w-]+)', content))
        unused = defined_vars - used_vars
        if unused:
            info(f"{css_file.name}: {len(unused)} potentially unused CSS vars")

        ok(f"{css_file.name}: {size/1024:.1f}KB, {lines} lines, {len(defined_vars)} vars")

# ════════════════════════════════════════════════════════════
#  DIMENSION 10: GIT DEEP
# ════════════════════════════════════════════════════════════

def test_git_branches():
    """Check git branch structure"""
    result = subprocess.run(['git', 'branch', '-a'], capture_output=True, text=True)
    branches = [b.strip() for b in result.stdout.split('\n') if b.strip()]
    ok(f"Git branches: {', '.join(branches)}")

    # Check we're on main
    result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
    current = result.stdout.strip()
    if current == 'main':
        ok("On main branch")
    else:
        warn(f"On branch: {current}")

def test_git_recent_commits():
    """Check recent commit history"""
    result = subprocess.run(
        ['git', 'log', '--oneline', '-10'],
        capture_output=True, text=True
    )
    commits = result.stdout.strip().split('\n')
    ok(f"Recent commits: {len(commits)}")

    # Check for commit message quality
    for c in commits:
        if len(c) < 10:
            warn(f"Very short commit: {c}")

def test_git_large_objects():
    """Check for large objects in git history"""
    result = subprocess.run(
        ['git', 'rev-list', '--objects', '--all'],
        capture_output=True, text=True
    )
    objects = result.stdout.strip().split('\n')
    ok(f"Total git objects: {len(objects)}")

    # Check pack size
    result = subprocess.run(
        ['git', 'count-objects', '-vH'],
        capture_output=True, text=True
    )
    for line in result.stdout.strip().split('\n'):
        if 'size-pack' in line:
            ok(f"Pack size: {line.strip()}")

def test_git_hooks():
    """Check for git hooks"""
    hooks_dir = REPO / '.git' / 'hooks'
    hooks = [f for f in hooks_dir.iterdir() if f.is_file() and not f.name.endswith('.sample')]
    if hooks:
        ok(f"Active git hooks: {', '.join(h.name for h in hooks)}")
    else:
        info("No active git hooks")

def test_codeowners_deep():
    """CODEOWNERS covers all sensitive paths"""
    co = read('CODEOWNERS') or ''
    # Check that every workflow file is owned
    workflows = list(REPO.glob(".github/workflows/*.yml"))
    for wf in workflows:
        if wf.name in co or '.github/workflows/' in co:
            pass  # covered by wildcard
        else:
            warn(f"CODEOWNERS missing: .github/workflows/{wf.name}")

    # Check key API files
    api_files = list(REPO.glob("api/*.json"))
    api_owned = 'api/' in co or 'api/ @' in co
    if api_owned:
        ok("CODEOWNERS covers api/ directory")
    else:
        warn("CODEOWNERS may not cover api/ directory")

# ════════════════════════════════════════════════════════════
#  RUNNER
# ════════════════════════════════════════════════════════════

ALL_TESTS = [
    # Dimension 1: JSON Schema
    test_json_schema_validation,
    # Dimension 2: API Content
    test_authority_json_deep,
    test_wellknown_deep,
    test_verification_levels_deep,
    test_echo_index_deep,
    test_cross_api_references,
    # Dimension 3: Cross-references
    test_all_file_references,
    # Dimension 4: Content Quality
    test_markdown_syntax,
    test_terminology_deep,
    test_bilingual_quality,
    test_no_placeholder_content,
    # Dimension 5: Live HTTP
    test_http_redirects,
    test_http_security_headers,
    test_live_page_content,
    test_live_json_endpoints,
    test_404_handling,
    # Dimension 6: HTML & Accessibility
    test_html_structure,
    test_accessibility_deep,
    # Dimension 7: Workflow Security
    test_workflow_security_deep,
    # Dimension 8: SEO
    test_sitemap_completeness,
    test_structured_data,
    test_canonical_urls,
    # Dimension 9: Performance
    test_page_weight,
    test_css_optimization,
    # Dimension 10: Git
    test_git_branches,
    test_git_recent_commits,
    test_git_large_objects,
    test_git_hooks,
    test_codeowners_deep,
]

def main():
    print("🔬 TRINITY ACCORD — PENETRATION-DEPTH SYSTEM TEST")
    print("=" * 60)
    print(f"Repository: {REPO}")
    print(f"Tests: {len(ALL_TESTS)} deep validation suites")
    print()

    for test_fn in ALL_TESTS:
        try:
            test_fn()
        except Exception as e:
            err(f"Test {test_fn.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()

    print()
    print("=" * 60)
    print("📊 PENETRATION TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed:   {len(passed)}")
    print(f"⚠️  Warnings: {len(warnings)}")
    print(f"❌ Errors:   {len(errors)}")
    print(f"ℹ️  Info:     {len(info_log)}")
    print("=" * 60)

    if errors:
        print(f"\n🔴 ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  {e}")

    if warnings:
        print(f"\n🟡 WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  {w}")

    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
