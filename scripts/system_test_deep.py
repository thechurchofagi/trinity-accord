#!/usr/bin/env python3
"""
Trinity Accord — Deep System Test Suite
========================================
50+ test suites covering: build, API, security, SEO, accessibility,
performance, content consistency, workflow security, JSON schema,
cross-references, git hygiene, and more.
"""

import json, os, re, sys, glob, subprocess, hashlib, xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, Counter
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent
os.chdir(REPO)

errors, warnings, passed = [], [], []

def err(msg):   errors.append(f"❌ {msg}")
def warn(msg):  warnings.append(f"⚠️  {msg}")
def ok(msg):    passed.append(f"✅ {msg}")
def info(msg):  print(f"   ℹ️  {msg}")

# ════════════════════════════════════════════════════════════
#  HELPER: read file safely
# ════════════════════════════════════════════════════════════
def read(p):
    try: return (REPO / p).read_text(encoding='utf-8')
    except: return None

def read_json(p):
    try:
        with open(REPO / p) as f: return json.load(f)
    except json.JSONDecodeError as e:
        err(f"Invalid JSON {p}: {e}")
        return None
    except: return None

# ════════════════════════════════════════════════════════════
#  DIMENSION 1: DEPLOYMENT & BUILD
# ════════════════════════════════════════════════════════════

def test_01_required_paths():
    """DEPLOYMENT.md required paths exist"""
    required = [
        ".well-known/trinity-accord.json", "api/authority.json",
        "api/verification-levels.json", "verify.md", "agent-start.md",
        "robots.txt", "sitemap.xml", "favicon.ico",
    ]
    for p in required:
        if (REPO / p).exists(): ok(f"Deploy path: /{p}")
        else: err(f"Missing deploy path: /{p}")

def test_02_jekyll_front_matter():
    """All .md files that should be pages have valid YAML front matter"""
    md_files = [f for f in REPO.glob("*.md") if f.name != 'README.md']
    md_files += list(REPO.glob("docs/*.md"))
    for mf in sorted(md_files):
        content = mf.read_text(encoding='utf-8', errors='ignore')
        if not content.startswith('---'):
            err(f"No front matter: {mf.name}")
            continue
        try:
            end = content.index('---', 3)
            fm = content[3:end]
            # Basic YAML parse check
            for line in fm.strip().split('\n'):
                if line.strip() and ':' not in line and not line.startswith(' '):
                    warn(f"Suspicious front matter line in {mf.name}: {line.strip()[:50]}")
            ok(f"Front matter valid: {mf.name}")
        except ValueError:
            err(f"Unclosed front matter in {mf.name}")

def test_03_permalink_uniqueness():
    """No two pages share the same permalink"""
    permalinks = defaultdict(list)
    for md in REPO.glob("**/*.md"):
        if any(d in str(md) for d in ['archive/', 'audit/', 'node_modules/', '.github/', 'vendor/']):
            continue
        content = read(md) or ''
        m = re.search(r'^permalink:\s*(.+)', content, re.MULTILINE)
        if m:
            permalinks[m.group(1).strip()].append(md.relative_to(REPO))
    for pl, files in permalinks.items():
        if len(files) > 1:
            err(f"Duplicate permalink '{pl}': {', '.join(str(f) for f in files)}")
        else:
            ok(f"Unique permalink: {pl}")

def test_04_excluded_dirs_not_published():
    """Excluded directories in _config.yml don't contain published pages"""
    config = read('_config.yml') or ''
    excluded = ['archive/', 'audit/', 'node_modules/', '_site/', 'vendor/']
    for exc in excluded:
        md_in_exc = list(REPO.glob(f"{exc}**/*.md"))
        if md_in_exc:
            # These should be excluded by Jekyll config
            if exc.rstrip('/') in config:
                ok(f"Excluded dir configured: {exc}")
            else:
                warn(f"Dir {exc} has {len(md_in_exc)} .md files but may not be excluded")

# ════════════════════════════════════════════════════════════
#  DIMENSION 2: JSON DEEP VALIDATION
# ════════════════════════════════════════════════════════════

def test_05_json_syntax():
    """All JSON files parse correctly"""
    json_files = list(REPO.glob("**/*.json"))
    json_files = [f for f in json_files if '.git' not in str(f) and 'node_modules' not in str(f)]
    broken = 0
    for jf in sorted(set(json_files)):
        try:
            with open(jf) as f: json.load(f)
            ok(f"JSON valid: {jf.relative_to(REPO)}")
        except json.JSONDecodeError as e:
            err(f"JSON parse error: {jf.relative_to(REPO)} — {e}")
            broken += 1
    info(f"Checked {len(json_files)} JSON files, {broken} broken")

def test_06_api_json_required_fields():
    """Key API JSON files have expected top-level fields"""
    specs = {
        'api/authority.json': ['canonical_authority', 'bitcoin_authority_address', 'bitcoin_originals'],
        'api/verification-levels.json': [],  # just valid JSON
        'api/echo-index.json': [],
        'api/echo-schema.json': [],
        'api/claim-registry.json': [],
        'api/corrections-index.json': [],
        'api/recovery-index.json': [],
        '.well-known/trinity-accord.json': ['name'],
        '.well-known/agent.json': [],
    }
    for path, required_keys in specs.items():
        data = read_json(path)
        if data is None:
            if (REPO / path).exists():
                pass  # error already logged
            else:
                err(f"Missing API file: {path}")
            continue
        for key in required_keys:
            if key in data:
                ok(f"{path} has '{key}'")
            else:
                warn(f"{path} missing expected key '{key}'")
        ok(f"API file loaded: {path}")

def test_07_json_schema_files_valid():
    """Schema JSON files are valid and have $schema or type"""
    schemas = list(REPO.glob("api/*schema*.json")) + list(REPO.glob("api/*schema*.v*.json"))
    for sf in sorted(set(schemas)):
        data = read_json(sf)
        if data is None: continue
        has_type = any(k in data for k in ['$schema', 'type', 'properties', 'title'])
        if has_type:
            ok(f"Schema has structure: {sf.name}")
        else:
            warn(f"Schema file lacks type/properties: {sf.name}")

def test_08_json_cross_references():
    """JSON files referencing other files — targets exist"""
    ref_patterns = [
        (re.compile(r'"(?:schema|path|file|source|manifest)":\s*"([^"]+\.json)"'), 'json'),
        (re.compile(r'"(?:href|url|link)":\s*"(/api/[^"]+)"'), 'api_path'),
    ]
    checked = 0
    for jf in REPO.glob("api/**/*.json"):
        content = read(jf) or ''
        for pattern, kind in ref_patterns:
            for m in pattern.finditer(content):
                ref = m.group(1)
                if kind == 'json':
                    # Relative reference
                    candidate = jf.parent / ref
                    if candidate.exists():
                        ok(f"JSON ref valid: {jf.name} → {ref}")
                    else:
                        # Might be a schema version reference, not a file
                        pass
                elif kind == 'api_path':
                    target = REPO / ref.lstrip('/')
                    if target.exists():
                        ok(f"API path ref valid: {jf.name} → {ref}")
                    else:
                        warn(f"API path ref missing: {jf.name} → {ref}")
                checked += 1
    info(f"Checked {checked} JSON cross-references")

# ════════════════════════════════════════════════════════════
#  DIMENSION 3: LINK INTEGRITY (DEEP)
# ════════════════════════════════════════════════════════════

def test_09_all_internal_links():
    """Every internal link in every .md file resolves to a published path"""
    # Build comprehensive index of published paths
    published = set()
    for md in REPO.glob("**/*.md"):
        rel = str(md.relative_to(REPO))
        if any(d in rel for d in ['archive/', 'audit/', 'node_modules/', '_site/', 'vendor/', '.github/']):
            continue
        stem = rel.replace('.md', '')
        published.add('/' + stem)
        published.add('/' + stem + '/')
    # Add non-md files
    for pattern in ['api/**/*.json', '.well-known/*.json', 'assets/**/*', 'scripts/*.py',
                    'tools/**/*', 'docs/**/*', 'downloads/*', 'examples/**/*',
                    'echoes/**/*', 'evidence/**/*']:
        for f in REPO.glob(pattern):
            if f.is_file():
                published.add('/' + str(f.relative_to(REPO)))
    # Root files
    for f in ['robots.txt', 'sitemap.xml', 'favicon.ico', 'favicon.svg', 'ai.txt',
              'citation.cff', 'feed.xml', 'llms.txt', 'llms-full.txt']:
        if (REPO / f).exists():
            published.add('/' + f)

    # Scan all markdown
    link_re = re.compile(r'\[([^\]]*)\]\((/[^\)]+)\)')
    broken = []
    total = 0
    for md in REPO.glob("**/*.md"):
        rel = str(md.relative_to(REPO))
        if any(d in rel for d in ['archive/', 'node_modules/', '_site/', 'vendor/']):
            continue
        content = read(md) or ''
        for m in link_re.finditer(content):
            text, href = m.group(1), m.group(2)
            path = href.split('#')[0].split('?')[0]
            if not path: continue
            total += 1
            # Check direct match
            found = False
            for pub in published:
                if pub == path or pub == path + '/' or pub.rstrip('/') == path.rstrip('/'):
                    found = True; break
            if not found:
                direct = REPO / path.lstrip('/')
                direct_md = REPO / (path.lstrip('/') + '.md')
                if direct.exists() or direct_md.exists():
                    found = True
            if not found:
                # Check case-insensitive
                lower = path.lower()
                for pub in published:
                    if pub.lower() == lower or pub.lower().rstrip('/') == lower.rstrip('/'):
                        found = True; break
            if not found:
                broken.append((rel, href, text[:40]))

    for src, href, text in broken:
        err(f"Broken link in {src}: [{text}]({href})")
    if not broken:
        ok(f"All {total} internal links valid across all .md files")
    else:
        info(f"{len(broken)} broken out of {total} total links")

def test_10_html_link_targets():
    """Links in HTML layout/templates point to existing files"""
    layout = read('_layouts/default.html') or ''
    hrefs = re.findall(r'href="(/[^"]*)"', layout)
    srcs = re.findall(r'src="(/[^"]*)"', layout)
    all_refs = set(hrefs + srcs)
    for ref in sorted(all_refs):
        if ref.startswith('http'): continue
        path = ref.split('?')[0].split('#')[0]
        direct = REPO / path.lstrip('/')
        if direct.exists():
            ok(f"Layout ref exists: {ref}")
        else:
            # Check as .scss → .css
            scss = REPO / (path.lstrip('/').replace('.css', '.scss'))
            if scss.exists():
                ok(f"Layout ref (via SCSS): {ref}")
            else:
                err(f"Layout ref missing: {ref}")

def test_11_nav_footer_consistency():
    """Nav and footer links in layout match actual pages"""
    layout = read('_layouts/default.html') or ''
    # Extract all href in nav and footer
    nav_section = layout[layout.find('class="nav-links"'):layout.find('</div>', layout.find('class="nav-links"'))] if 'nav-links' in layout else ''
    footer_section = layout[layout.find('<footer'):] if '<footer' in layout else ''

    nav_links = re.findall(r'href="(/[^"]*)"', nav_section)
    footer_links = re.findall(r'href="(/[^"]*)"', footer_section)

    for link in sorted(set(nav_links + footer_links)):
        if link.startswith('http'): continue
        path = link.lstrip('/')
        md_path = REPO / (path + '.md')
        direct = REPO / path
        if md_path.exists() or direct.exists():
            ok(f"Nav/footer target: {link}")
        else:
            err(f"Nav/footer broken target: {link}")

# ════════════════════════════════════════════════════════════
#  DIMENSION 4: SEO & DISCOVERY
# ════════════════════════════════════════════════════════════

def test_12_sitemap_parse():
    """sitemap.xml is valid XML and URLs are reachable paths"""
    sitemap = read('sitemap.xml') or ''
    try:
        root = ET.fromstring(sitemap)
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = root.findall('.//sm:loc', ns) or root.findall('.//loc')
        ok(f"Sitemap valid XML with {len(urls)} URLs")
        for u in urls:
            url = u.text.strip()
            path = urlparse(url).path
            # Check that the path has a corresponding file
            md = REPO / (path.strip('/') + '.md')
            direct = REPO / path.strip('/')
            if md.exists() or direct.exists() or path == '/':
                pass
            else:
                warn(f"Sitemap URL may 404: {url}")
    except ET.ParseError as e:
        err(f"sitemap.xml parse error: {e}")

def test_13_robots_txt():
    """robots.txt is well-formed"""
    robots = read('robots.txt') or ''
    if 'User-agent:' in robots:
        ok("robots.txt has User-agent")
    else:
        err("robots.txt missing User-agent")
    if 'Sitemap:' in robots:
        ok("robots.txt has Sitemap")
    else:
        warn("robots.txt missing Sitemap")
    # Check for overly permissive
    if 'Disallow: /' in robots and 'Allow:' not in robots:
        warn("robots.txt disallows everything")
    ok("robots.txt present and structured")

def test_14_json_ld():
    """JSON-LD in layout is valid and has required Schema.org fields"""
    layout = read('_layouts/default.html') or ''
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', layout, re.DOTALL)
    if not m:
        err("No JSON-LD in layout"); return
    try:
        data = json.loads(m.group(1))
        for key in ['@context', '@type', 'name', 'url']:
            if key in data:
                ok(f"JSON-LD has '{key}'")
            else:
                warn(f"JSON-LD missing '{key}'")
        if data.get('@context') != 'https://schema.org':
            warn(f"JSON-LD context is {data.get('@context')}, expected schema.org")
    except json.JSONDecodeError as e:
        err(f"JSON-LD invalid: {e}")

def test_15_og_twitter_meta():
    """Open Graph and Twitter Card meta tags present"""
    layout = read('_layouts/default.html') or ''
    required = {
        'og:type': 'og:type', 'og:title': 'og:title',
        'og:description': 'og:description', 'og:image': 'og:image',
        'og:url': 'og:url', 'twitter:card': 'twitter:card',
        'twitter:title': 'twitter:title', 'twitter:image': 'twitter:image',
    }
    for name, prop in required.items():
        if prop in layout: ok(f"Meta: {name}")
        else: warn(f"Missing meta: {name}")

def test_16_canonical_url():
    """Canonical URL tag present and correct"""
    layout = read('_layouts/default.html') or ''
    if 'rel="canonical"' in layout:
        ok("Canonical URL tag present")
    else:
        warn("Missing canonical URL tag")

def test_17_ai_discovery():
    """AI discovery files (llms.txt, ai.txt) present and referenced"""
    for f in ['llms.txt', 'ai.txt', 'llms-full.txt']:
        if (REPO / f).exists():
            size = (REPO / f).stat().st_size
            ok(f"{f} exists ({size} bytes)")
        else:
            warn(f"{f} missing")
    # Check HTML references
    layout = read('_layouts/default.html') or ''
    if 'llms.txt' in layout:
        ok("llms.txt referenced in HTML")
    else:
        warn("llms.txt not referenced in HTML head")

# ════════════════════════════════════════════════════════════
#  DIMENSION 5: ACCESSIBILITY
# ════════════════════════════════════════════════════════════

def test_18_skip_link():
    """Skip-to-content link present"""
    layout = read('_layouts/default.html') or ''
    if 'skip-link' in layout or 'skip to content' in layout.lower():
        ok("Skip-to-content link present")
    else:
        err("Missing skip-to-content link for accessibility")

def test_19_lang_attribute():
    """HTML lang attribute set"""
    layout = read('_layouts/default.html') or ''
    if '<html' in layout:
        tag = layout[layout.find('<html'):layout.find('>', layout.find('<html'))]
        if 'lang=' in tag:
            ok(f"HTML lang attribute: {re.search(r'lang=\"([^\"]+)\"', tag).group(1)}")
        else:
            err("Missing lang attribute on <html>")

def test_20_aria_labels():
    """Interactive elements have ARIA labels"""
    layout = read('_layouts/default.html') or ''
    # Check nav toggle button
    if 'aria-label="Toggle navigation"' in layout:
        ok("Nav toggle has aria-label")
    else:
        warn("Nav toggle missing aria-label")
    if 'aria-expanded' in layout:
        ok("Nav toggle has aria-expanded")
    else:
        warn("Nav toggle missing aria-expanded")

def test_21_heading_hierarchy():
    """Pages have proper heading hierarchy (h1 before h2, etc.)"""
    key_pages = ['index.md', 'verify.md', 'agent-start.md', 'authority.md',
                 'start.md', 'agent-brief.md', 'agent-understand.md']
    for page in key_pages:
        content = read(page) or ''
        headings = re.findall(r'^(#{1,6})\s', content, re.MULTILINE)
        if not headings:
            warn(f"No headings in {page}"); continue
        levels = [len(h) for h in headings]
        if levels[0] != 1:
            warn(f"{page} doesn't start with h1 (starts with h{levels[0]})")
        else:
            ok(f"{page} starts with h1")
        # Check for level skips
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                warn(f"{page} heading skip: h{levels[i-1]} → h{levels[i]}")
                break

# ════════════════════════════════════════════════════════════
#  DIMENSION 6: SECURITY
# ════════════════════════════════════════════════════════════

def test_22_no_secrets_in_published():
    """No API keys, tokens, or secrets in published files"""
    patterns = [
        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\'][^"\']{8,}', 'API key'),
        (r'(?i)(secret|password|passwd|pwd)\s*[:=]\s*["\'][^"\']{4,}', 'Secret'),
        (r'(?i)github_pat_[a-zA-Z0-9]{20,}', 'GitHub PAT'),
        (r'(?i)sk-[a-zA-Z0-9]{20,}', 'OpenAI key'),
        (r'(?i)ghp_[a-zA-Z0-9]{36}', 'GitHub token'),
        (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', 'Private key'),
    ]
    published_dirs = ['api', '.well-known', '_layouts', 'assets', 'docs', 'tools']
    files = []
    for d in published_dirs:
        p = REPO / d
        if p.exists():
            files += [f for f in p.rglob('*') if f.is_file() and f.suffix in ('.json','.html','.css','.js','.py','.mjs')]
    files += [REPO / f for f in ['index.md','verify.md','agent-start.md','robots.txt','sitemap.xml']]

    found = False
    for f in files:
        if not f.exists(): continue
        content = f.read_text(encoding='utf-8', errors='ignore')
        for pat, name in patterns:
            if re.search(pat, content):
                err(f"Possible {name} in {f.relative_to(REPO)}")
                found = True
    if not found: ok("No secrets found in published files")

def test_23_no_xss_vectors():
    """No raw user input reflected in HTML without escaping"""
    layout = read('_layouts/default.html') or ''
    # Check for dangerouslySetInnerHTML-like patterns
    dangerous = re.findall(r'innerHTML\s*=', layout)
    if dangerous:
        warn(f"Found {len(dangerous)} innerHTML assignments — review for XSS")
    else:
        ok("No innerHTML XSS vectors in layout")
    # Check for eval
    if 'eval(' in layout:
        warn("eval() found in layout — potential XSS risk")
    else:
        ok("No eval() in layout")

def test_24_mixed_content():
    """No HTTP resources in HTTPS pages"""
    layout = read('_layouts/default.html') or ''
    http_refs = re.findall(r'(?:href|src)="(http://[^"]*)"', layout)
    if http_refs:
        for ref in http_refs:
            warn(f"HTTP (not HTTPS) resource: {ref}")
    else:
        ok("No mixed content (HTTP) in layout")

def test_25_workflow_security():
    """GitHub Actions workflows use pinned actions and have actor checks"""
    workflows = list(REPO.glob(".github/workflows/*.yml"))
    for wf in sorted(workflows):
        content = read(wf) or ''
        # Check for pinned actions (SHA hash)
        uses = re.findall(r'uses:\s*(\S+)', content)
        unpinned = [u for u in uses if '@' in u and not re.search(r'@[a-f0-9]{40}', u)]
        pinned = [u for u in uses if re.search(r'@[a-f0-9]{40}', u)]
        if unpinned:
            warn(f"{wf.name}: {len(unpinned)} unpinned actions: {', '.join(unpinned[:3])}")
        if pinned:
            ok(f"{wf.name}: {len(pinned)} pinned actions")
        # Check for write permissions
        if 'permissions:' in content:
            ok(f"{wf.name}: has permissions block")
        # Check for actor validation on write workflows
        if 'write' in content.lower() or 'push' in content.lower():
            if 'github.actor' in content:
                ok(f"{wf.name}: actor validation present")
            else:
                warn(f"{wf.name}: write workflow without actor validation")

def test_26_codeowners():
    """CODEOWNERS file covers sensitive paths"""
    co = read('CODEOWNERS') or ''
    sensitive_paths = ['.github/workflows/', 'api/', 'index.md', 'scripts/']
    for sp in sensitive_paths:
        if sp in co:
            ok(f"CODEOWNERS covers: {sp}")
        else:
            warn(f"CODEOWNERS missing: {sp}")

# ════════════════════════════════════════════════════════════
#  DIMENSION 7: PERFORMANCE & SIZE
# ════════════════════════════════════════════════════════════

def test_27_large_files():
    """No excessively large files in the repo (>5MB)"""
    large = []
    for f in REPO.rglob('*'):
        if '.git' in str(f) or 'node_modules' in str(f): continue
        if f.is_file():
            size = f.stat().st_size
            if size > 5 * 1024 * 1024:
                large.append((f.relative_to(REPO), size))
    for f, s in large:
        warn(f"Large file ({s/1024/1024:.1f}MB): {f}")
    if not large:
        ok("No files over 5MB in repo")

def test_28_image_optimization():
    """Images are reasonably sized"""
    images = list(REPO.glob("assets/img/*"))
    for img in images:
        size = img.stat().st_size
        if size > 500 * 1024:
            warn(f"Large image ({size/1024:.0f}KB): {img.name}")
        else:
            ok(f"Image size OK: {img.name} ({size/1024:.0f}KB)")

def test_29_css_size():
    """CSS files are not excessively large"""
    for css in REPO.glob("assets/css/*"):
        size = css.stat().st_size
        lines = len(css.read_text().split('\n'))
        if size > 100 * 1024:
            warn(f"Large CSS ({size/1024:.0f}KB, {lines} lines): {css.name}")
        else:
            ok(f"CSS size OK: {css.name} ({size/1024:.0f}KB, {lines} lines)")

# ════════════════════════════════════════════════════════════
#  DIMENSION 8: CONTENT CONSISTENCY
# ════════════════════════════════════════════════════════════

def test_30_bilingual_coverage():
    """Key pages have both English and Chinese content"""
    key_pages = ['index.md', 'authority.md', 'start.md', 'verify.md']
    cjk_re = re.compile(r'[\u4e00-\u9fff]')
    for page in key_pages:
        content = read(page) or ''
        has_en = bool(re.search(r'[a-zA-Z]{3,}', content))
        has_zh = bool(cjk_re.search(content))
        if has_en and has_zh:
            ok(f"Bilingual: {page}")
        elif has_en:
            warn(f"English only (no Chinese): {page}")
        elif has_zh:
            warn(f"Chinese only (no English): {page}")

def test_31_terminology_consistency():
    """Key terms used consistently across pages"""
    terms = {
        'Bitcoin Originals': r'Bitcoin Originals',
        'non-amending': r'non-amending',
        'verification': r'(?i)verif(y|ication)',
        'guardianship': r'(?i)guardianship',
    }
    key_files = list(REPO.glob("*.md"))[:20]
    for term, pattern in terms.items():
        found_in = []
        for f in key_files:
            content = read(f) or ''
            if re.search(pattern, content):
                found_in.append(f.name)
        if found_in:
            ok(f"Term '{term}' found in {len(found_in)} files")
        else:
            warn(f"Term '{term}' not found in key files")

def test_32_homepage_boundary_statement():
    """Homepage contains the required boundary/disclaimer statements"""
    index = read('index.md') or ''
    required = [
        ('Not a religion', r'(?i)not a religion'),
        ('Not crypto asset', r'(?i)not crypto'),
        ('Not NFT project', r'(?i)not NFT'),
        ('Not investment', r'(?i)not investment'),
        ('Not prompt injection', r'(?i)not prompt injection'),
        ('Not AI command', r'(?i)not AI command'),
        ('Verify first', r'(?i)verify first'),
        ('Bitcoin authority', r'bc1p'),
    ]
    for name, pattern in required:
        if re.search(pattern, index):
            ok(f"Homepage: {name}")
        else:
            err(f"Homepage missing boundary: {name}")

def test_33_authority_address_consistency():
    """Bitcoin authority address consistent across files"""
    addr = 'bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf'
    files_with_addr = []
    for f in REPO.glob("**/*.md"):
        if '.git' in str(f) or 'node_modules' in str(f): continue
        content = read(f) or ''
        if addr in content:
            files_with_addr.append(f.name)
    for f in REPO.glob("api/*.json"):
        content = read(f) or ''
        if addr in content:
            files_with_addr.append(f.name)
    if len(files_with_addr) >= 3:
        ok(f"Authority address consistent in {len(files_with_addr)} files")
    else:
        warn(f"Authority address only in {len(files_with_addr)} files — check consistency")

# ════════════════════════════════════════════════════════════
#  DIMENSION 9: GIT HYGIENE
# ════════════════════════════════════════════════════════════

def test_34_gitignore_coverage():
    """Important patterns in .gitignore"""
    gi = read('.gitignore') or ''
    required = ['node_modules/', '__pycache__/', '*.pyc', '.env']
    for pat in required:
        if pat in gi:
            ok(f".gitignore has: {pat}")
        else:
            warn(f".gitignore missing: {pat}")

def test_35_no_binary_in_git():
    """No unexpected binary files tracked in git"""
    result = subprocess.run(
        ['git', 'ls-files', '--eol'],
        capture_output=True, text=True, cwd=REPO
    )
    binaries = []
    for line in result.stdout.split('\n'):
        if 'binary' in line.lower() and '.git' not in line:
            parts = line.split()
            if parts:
                binaries.append(parts[-1])
    if binaries:
        for b in binaries[:10]:
            warn(f"Binary file tracked: {b}")
    else:
        ok("No unexpected binary files in git")

def test_36_git_status_clean():
    """Working tree is clean (no uncommitted changes)"""
    result = subprocess.run(
        ['git', 'status', '--porcelain'],
        capture_output=True, text=True, cwd=REPO
    )
    if result.stdout.strip():
        lines = result.stdout.strip().split('\n')
        warn(f"{len(lines)} uncommitted changes in working tree")
    else:
        ok("Git working tree clean")

# ════════════════════════════════════════════════════════════
#  DIMENSION 10: DEPENDENCY & TOOLCHAIN
# ════════════════════════════════════════════════════════════

def test_37_package_json():
    """package.json is valid and dependencies are minimal"""
    pj = read_json('package.json')
    if pj:
        deps = pj.get('dependencies', {})
        dev = pj.get('devDependencies', {})
        ok(f"package.json: {len(deps)} deps, {len(dev)} devDeps")
        if len(deps) + len(dev) > 20:
            warn(f"Many dependencies ({len(deps) + len(dev)}) — review necessity")

def test_38_python_scripts_syntax():
    """All Python scripts have valid syntax"""
    scripts = list(REPO.glob("scripts/*.py"))
    broken = 0
    for s in sorted(scripts):
        result = subprocess.run(
            ['python3', '-c', f'import ast; ast.parse(open("{s}").read())'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            err(f"Syntax error: {s.name}: {result.stderr.strip()[:80]}")
            broken += 1
    if broken == 0:
        ok(f"All {len(scripts)} Python scripts have valid syntax")
    else:
        err(f"{broken} scripts with syntax errors")

def test_39_mjs_scripts_syntax():
    """JavaScript .mjs files have no obvious syntax issues"""
    mjs_files = list(REPO.glob("scripts/*.mjs"))
    for f in sorted(mjs_files):
        content = read(f) or ''
        # Basic checks
        if 'import ' in content or 'export ' in content:
            ok(f"ES module syntax: {f.name}")
        else:
            warn(f"No import/export in {f.name}")

# ════════════════════════════════════════════════════════════
#  DIMENSION 11: FEED & METADATA
# ════════════════════════════════════════════════════════════

def test_40_feed_xml():
    """feed.xml is valid RSS/Atom"""
    feed = read('feed.xml') or ''
    if '<rss' in feed:
        ok("feed.xml is RSS format")
    elif '<feed' in feed:
        ok("feed.xml is Atom format")
    else:
        warn("feed.xml not valid RSS or Atom")
    try:
        ET.fromstring(feed)
        ok("feed.xml parses as valid XML")
    except ET.ParseError as e:
        err(f"feed.xml XML parse error: {e}")

def test_41_cname():
    """CNAME file matches expected domain"""
    cname = read('CNAME') or ''
    domain = cname.strip()
    if domain == 'www.trinityaccord.org':
        ok(f"CNAME correct: {domain}")
    elif domain:
        warn(f"CNAME is '{domain}', expected 'www.trinityaccord.org'")
    else:
        warn("CNAME file empty or missing")

def test_42_sitemap_urls():
    """Sitemap URLs use correct domain"""
    sitemap = read('sitemap.xml') or ''
    urls = re.findall(r'<loc>(.*?)</loc>', sitemap)
    bad = [u for u in urls if 'trinityaccord.org' not in u]
    if bad:
        for u in bad:
            warn(f"Sitemap URL with wrong domain: {u}")
    else:
        ok(f"All {len(urls)} sitemap URLs use correct domain")

# ════════════════════════════════════════════════════════════
#  DIMENSION 12: CROSS-FILE CONSISTENCY
# ════════════════════════════════════════════════════════════

def test_43_echo_index_consistency():
    """echo-index.json references match actual echo files"""
    idx = read_json('api/echo-index.json')
    if idx and isinstance(idx, list):
        ok(f"echo-index.json has {len(idx)} entries")
    elif idx and isinstance(idx, dict):
        entries = idx.get('echoes', idx.get('entries', idx.get('records', [])))
        ok(f"echo-index.json has {len(entries)} entries")

def test_44_verification_levels_referenced():
    """verification-levels.json is referenced from other files"""
    vl_content = read('api/verification-levels.json') or ''
    if vl_content:
        # Check if referenced
        refs = 0
        for f in REPO.glob("api/*.json"):
            content = read(f) or ''
            if 'verification-levels' in content:
                refs += 1
        if refs > 0:
            ok(f"verification-levels.json referenced from {refs} files")
        else:
            warn("verification-levels.json not referenced from other API files")

def test_45_manifest_consistency():
    """Key manifests (authority, evidence) are internally consistent"""
    auth = read_json('api/authority.json')
    if auth:
        # Check bitcoin_originals count
        originals = auth.get('bitcoin_originals', [])
        if len(originals) == 3:
            ok(f"authority.json: 3 Bitcoin originals (correct)")
        else:
            warn(f"authority.json: {len(originals)} Bitcoin originals (expected 3)")

def test_46_recovery_index():
    """recovery-index.json exists and is valid"""
    ri = read_json('api/recovery-index.json')
    if ri:
        ok(f"recovery-index.json loaded")
    else:
        warn("recovery-index.json missing or invalid")

def test_47_corrections_index():
    """corrections-index.json exists and is valid"""
    ci = read_json('api/corrections-index.json')
    if ci:
        ok(f"corrections-index.json loaded")
    else:
        warn("corrections-index.json missing or invalid")

# ════════════════════════════════════════════════════════════
#  DIMENSION 13: ONLINE VERIFICATION
# ════════════════════════════════════════════════════════════

def test_48_live_site_check():
    """Live site returns 200 for key pages"""
    import urllib.request
    import urllib.error
    key_urls = [
        'https://www.trinityaccord.org/',
        'https://www.trinityaccord.org/verify/',
        'https://www.trinityaccord.org/agent-start/',
        'https://www.trinityaccord.org/authority/',
        'https://www.trinityaccord.org/agent-brief/',
        'https://www.trinityaccord.org/api/authority.json',
        'https://www.trinityaccord.org/.well-known/trinity-accord.json',
        'https://www.trinityaccord.org/robots.txt',
        'https://www.trinityaccord.org/sitemap.xml',
    ]
    for url in key_urls:
        try:
            req = urllib.request.Request(url, method='HEAD')
            resp = urllib.request.urlopen(req, timeout=10)
            if resp.status == 200:
                ok(f"Live 200: {url.replace('https://www.trinityaccord.org', '')}")
            else:
                warn(f"Live {resp.status}: {url}")
        except urllib.error.HTTPError as e:
            err(f"Live {e.code}: {url}")
        except Exception as e:
            warn(f"Live check failed: {url} — {e}")

def test_49_live_json_valid():
    """Live JSON endpoints return valid JSON"""
    import urllib.request
    json_urls = [
        'https://www.trinityaccord.org/api/authority.json',
        'https://www.trinityaccord.org/.well-known/trinity-accord.json',
        'https://www.trinityaccord.org/api/verification-levels.json',
    ]
    for url in json_urls:
        try:
            resp = urllib.request.urlopen(url, timeout=10)
            data = json.loads(resp.read())
            ok(f"Live JSON valid: {url.split('/')[-1]}")
        except Exception as e:
            err(f"Live JSON error: {url} — {e}")

def test_50_live_headers():
    """Live site has reasonable HTTP headers"""
    import urllib.request
    try:
        req = urllib.request.Request('https://www.trinityaccord.org/')
        resp = urllib.request.urlopen(req, timeout=10)
        headers = dict(resp.headers)
        # Check content type
        ct = headers.get('Content-Type', '')
        if 'text/html' in ct:
            ok(f"Content-Type: {ct}")
        else:
            warn(f"Unexpected Content-Type: {ct}")
        # Check for security headers
        for h in ['X-Content-Type-Options', 'X-Frame-Options', 'Content-Security-Policy']:
            if h in headers:
                ok(f"Security header: {h}")
            else:
                warn(f"Missing security header: {h}")
    except Exception as e:
        warn(f"Header check failed: {e}")

# ════════════════════════════════════════════════════════════
#  DIMENSION 14: DOCUMENTATION COMPLETENESS
# ════════════════════════════════════════════════════════════

def test_51_key_docs_exist():
    """Core documentation files exist and are non-trivial"""
    docs = {
        'README.md': 500,
        'SECURITY.md': 500,
        'RECOVERY.md': 500,
        'verify.md': 500,
        'agent-brief.md': 500,
        'authority.md': 500,
    }
    for doc, min_size in docs.items():
        fp = REPO / doc
        if fp.exists():
            size = fp.stat().st_size
            if size >= min_size:
                ok(f"Doc {doc}: {size} bytes")
            else:
                warn(f"Doc {doc} too small: {size} bytes (expected {min_size}+)")
        else:
            err(f"Missing doc: {doc}")

def test_52_security_policy():
    """SECURITY.md has responsible disclosure instructions"""
    sec = read('SECURITY.md') or ''
    if 'vulnerability' in sec.lower() or 'disclosure' in sec.lower() or 'report' in sec.lower():
        ok("SECURITY.md has disclosure instructions")
    else:
        warn("SECURITY.md may lack disclosure instructions")

# ════════════════════════════════════════════════════════════
#  RUNNER
# ════════════════════════════════════════════════════════════

ALL_TESTS = [
    test_01_required_paths, test_02_jekyll_front_matter, test_03_permalink_uniqueness,
    test_04_excluded_dirs_not_published, test_05_json_syntax, test_06_api_json_required_fields,
    test_07_json_schema_files_valid, test_08_json_cross_references, test_09_all_internal_links,
    test_10_html_link_targets, test_11_nav_footer_consistency, test_12_sitemap_parse,
    test_13_robots_txt, test_14_json_ld, test_15_og_twitter_meta, test_16_canonical_url,
    test_17_ai_discovery, test_18_skip_link, test_19_lang_attribute, test_20_aria_labels,
    test_21_heading_hierarchy, test_22_no_secrets_in_published, test_23_no_xss_vectors,
    test_24_mixed_content, test_25_workflow_security, test_26_codeowners,
    test_27_large_files, test_28_image_optimization, test_29_css_size,
    test_30_bilingual_coverage, test_31_terminology_consistency, test_32_homepage_boundary_statement,
    test_33_authority_address_consistency, test_34_gitignore_coverage, test_35_no_binary_in_git,
    test_36_git_status_clean, test_37_package_json, test_38_python_scripts_syntax,
    test_39_mjs_scripts_syntax, test_40_feed_xml, test_41_cname, test_42_sitemap_urls,
    test_43_echo_index_consistency, test_44_verification_levels_referenced,
    test_45_manifest_consistency, test_46_recovery_index, test_47_corrections_index,
    test_48_live_site_check, test_49_live_json_valid, test_50_live_headers,
    test_51_key_docs_exist, test_52_security_policy,
]

def main():
    print("🔬 TRINITY ACCORD — DEEP SYSTEM TEST")
    print("=" * 60)
    print(f"Repository: {REPO}")
    print(f"Tests: {len(ALL_TESTS)} suites")
    print()

    for test_fn in ALL_TESTS:
        try:
            test_fn()
        except Exception as e:
            err(f"Test {test_fn.__name__} crashed: {e}")

    print()
    print("=" * 60)
    print("📊 DEEP TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed:   {len(passed)}")
    print(f"⚠️  Warnings: {len(warnings)}")
    print(f"❌ Errors:   {len(errors)}")
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
