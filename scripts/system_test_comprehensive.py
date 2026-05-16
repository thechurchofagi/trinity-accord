#!/usr/bin/env python3
"""
Comprehensive System Test for Trinity Accord Website
=====================================================
Tests: structure, links, JSON validity, SEO, content consistency, deployment readiness.
"""

import json
import os
import re
import sys
import glob
import subprocess
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parent.parent
os.chdir(REPO)

errors = []
warnings = []
info = []

def err(msg):
    errors.append(f"❌ ERROR: {msg}")

def warn(msg):
    warnings.append(f"⚠️  WARN: {msg}")

def ok(msg):
    info.append(f"✅ OK: {msg}")

# ============================================================
# TEST 1: Required paths from DEPLOYMENT.md
# ============================================================
def test_deployment_paths():
    print("\n" + "="*60)
    print("TEST 1: Deployment Required Paths")
    print("="*60)
    required = [
        ".well-known/trinity-accord.json",
        "api/authority.json",
        "api/verification-levels.json",
        "verify.md",           # /verify with permalink: pretty
        "agent-start.md",      # /agent-start
        "robots.txt",
        "sitemap.xml",
        "favicon.ico",
    ]
    for p in required:
        if (REPO / p).exists():
            ok(f"Deployment path exists: /{p}")
        else:
            err(f"Missing deployment path: /{p}")

# ============================================================
# TEST 2: JSON validity for all API endpoints
# ============================================================
def test_json_validity():
    print("\n" + "="*60)
    print("TEST 2: JSON File Validity")
    print("="*60)
    json_files = list(REPO.glob("api/**/*.json")) + list(REPO.glob(".well-known/*.json"))
    json_files += list(REPO.glob("*.json"))  # root-level JSON
    broken = 0
    for jf in sorted(set(json_files)):
        try:
            with open(jf) as f:
                json.load(f)
            ok(f"Valid JSON: {jf.relative_to(REPO)}")
        except json.JSONDecodeError as e:
            err(f"Invalid JSON: {jf.relative_to(REPO)} — {e}")
            broken += 1
        except Exception as e:
            err(f"Cannot read: {jf.relative_to(REPO)} — {e}")
            broken += 1
    if broken == 0:
        ok(f"All {len(json_files)} JSON files valid")
    else:
        err(f"{broken} JSON files have errors")

# ============================================================
# TEST 3: Internal link integrity
# ============================================================
def test_link_integrity():
    print("\n" + "="*60)
    print("TEST 3: Internal Link Integrity")
    print("="*60)

    # Build set of all published paths
    published = set()
    for md in REPO.glob("**/*.md"):
        if any(d in str(md) for d in ['archive/', 'audit/', 'node_modules/', '_site/', 'vendor/', '.github/']):
            continue
        rel = md.relative_to(REPO)
        # Jekyll permalink: pretty turns foo.md into /foo/
        stem = str(rel).replace('.md', '')
        published.add('/' + stem)
        published.add('/' + stem + '/')

    # Add non-md files
    for f in ['.well-known/trinity-accord.json', '.well-known/agent.json',
              'api/authority.json', 'api/verification-levels.json',
              'robots.txt', 'sitemap.xml', 'favicon.ico', 'favicon.svg',
              'ai.txt', 'citation.cff', 'feed.xml',
              'assets/css/style.css', 'assets/css/trinity-home.css',
              'assets/img/trinity-social-card.png', 'assets/img/trinity-social-card.svg']:
        if (REPO / f).exists():
            published.add('/' + f)

    # Add all api/*.json
    for jf in REPO.glob("api/**/*.json"):
        rel = jf.relative_to(REPO)
        published.add('/' + str(rel))

    # Add all api/context-packs
    for f in REPO.glob("api/context-packs/**/*"):
        if f.is_file():
            published.add('/' + str(f.relative_to(REPO)))

    # Scan markdown files for internal links
    link_re = re.compile(r'\[([^\]]*)\]\((/[^\)]+)\)')
    broken_links = []
    checked = 0

    for md in REPO.glob("**/*.md"):
        if any(d in str(md) for d in ['archive/', 'audit/', 'node_modules/', '_site/', 'vendor/', '.github/']):
            continue
        try:
            content = md.read_text(encoding='utf-8')
        except:
            continue
        for match in link_re.finditer(content):
            text, href = match.group(1), match.group(2)
            # Strip anchors
            path = href.split('#')[0]
            # Normalize
            if path.endswith('/'):
                path_check = path[:-1]
            else:
                path_check = path

            # Check if it matches any published path
            found = False
            for pub in published:
                if pub == path or pub == path + '/' or pub.rstrip('/') == path_check:
                    found = True
                    break
                # Pretty URL: /verify could be verify.md
                if path_check == pub.rstrip('/'):
                    found = True
                    break

            if not found:
                # Check if the file exists directly
                direct = REPO / path.lstrip('/')
                direct_md = REPO / (path.lstrip('/') + '.md')
                if direct.exists() or direct_md.exists():
                    found = True

            if not found:
                broken_links.append((md.relative_to(REPO), href, text[:40]))
            checked += 1

    if broken_links:
        for src, href, text in broken_links:
            err(f"Broken link in {src}: [{text}]({href})")
    else:
        ok(f"All {checked} internal links appear valid")

# ============================================================
# TEST 4: Sitemap consistency
# ============================================================
def test_sitemap():
    print("\n" + "="*60)
    print("TEST 4: Sitemap Consistency")
    print("="*60)
    sitemap = REPO / "sitemap.xml"
    if not sitemap.exists():
        err("sitemap.xml missing")
        return

    content = sitemap.read_text()
    # Extract URLs from sitemap
    urls = re.findall(r'<loc>(.*?)</loc>', content)
    ok(f"Sitemap has {len(urls)} URLs")

    # Check that key pages are in sitemap
    key_pages = ['/verify', '/agent-start', '/authority', '/start', '/agent-brief']
    for page in key_pages:
        found = any(page in url for url in urls)
        if found:
            ok(f"Sitemap contains: {page}")
        else:
            warn(f"Sitemap may be missing: {page}")

# ============================================================
# TEST 5: robots.txt
# ============================================================
def test_robots():
    print("\n" + "="*60)
    print("TEST 5: robots.txt")
    print("="*60)
    robots = REPO / "robots.txt"
    if not robots.exists():
        err("robots.txt missing")
        return
    content = robots.read_text()
    if "Sitemap" in content:
        ok("robots.txt has Sitemap directive")
    else:
        warn("robots.txt missing Sitemap directive")
    if "llms.txt" in content or "ai.txt" in content:
        ok("robots.txt references AI discovery files")
    else:
        warn("robots.txt doesn't reference ai.txt/llms.txt")

# ============================================================
# TEST 6: Front matter consistency in key pages
# ============================================================
def test_front_matter():
    print("\n" + "="*60)
    print("TEST 6: Front Matter Consistency")
    print("="*60)

    key_files = {
        'index.md': ['layout', 'title', 'description'],
        'verify.md': ['layout', 'title'],
        'agent-start.md': ['layout', 'title'],
        'authority.md': ['layout', 'title'],
        'start.md': ['layout', 'title'],
        'agent-brief.md': ['layout', 'title'],
    }

    for fname, required_keys in key_files.items():
        fpath = REPO / fname
        if not fpath.exists():
            err(f"Key page missing: {fname}")
            continue
        content = fpath.read_text()
        if not content.startswith('---'):
            warn(f"No front matter in {fname}")
            continue
        fm_end = content.index('---', 3)
        fm = content[3:fm_end]
        for key in required_keys:
            if key + ':' in fm:
                ok(f"{fname} has '{key}'")
            else:
                warn(f"{fname} missing front matter key '{key}'")

# ============================================================
# TEST 7: CSS references in layout
# ============================================================
def test_css_references():
    print("\n" + "="*60)
    print("TEST 7: CSS & Asset References")
    print("="*60)
    layout = REPO / "_layouts/default.html"
    if not layout.exists():
        err("default.html layout missing")
        return
    content = layout.read_text()

    # Check CSS exists
    css_refs = re.findall(r'href="([^"]*\.css[^"]*)"', content)
    for css_ref in css_refs:
        local = css_ref.lstrip('/')
        if '?' in local:
            local = local.split('?')[0]
        # Jekyll compiles .scss to .css at build time, so check both
        if (REPO / local).exists() or (REPO / local.replace('.css', '.scss')).exists():
            ok(f"CSS file exists: {css_ref}")
        else:
            err(f"CSS file missing: {css_ref}")

    # Check favicon
    if '/favicon.svg' in content:
        if (REPO / 'favicon.svg').exists():
            ok("favicon.svg exists and is referenced")
        else:
            err("favicon.svg referenced but missing")
    if '/favicon.ico' in content:
        if (REPO / 'favicon.ico').exists():
            ok("favicon.ico exists and is referenced")
        else:
            err("favicon.ico referenced but missing")

# ============================================================
# TEST 8: Nav links match actual pages
# ============================================================
def test_nav_links():
    print("\n" + "="*60)
    print("TEST 8: Navigation Link Targets")
    print("="*60)
    layout = REPO / "_layouts/default.html"
    content = layout.read_text()

    # Extract nav links
    nav_links = re.findall(r'<a href="(/[^"]*)"[^>]*class="nav-', content)
    nav_links += re.findall(r'class="nav-[^"]*"[^>]*href="(/[^"]*)"', content)

    # Also get footer links
    footer_section = content[content.find('<footer'):] if '<footer' in content else ''
    footer_links = re.findall(r'href="(/[^"]*)"', footer_section)

    all_links = set(nav_links + footer_links)

    for link in sorted(all_links):
        if link.startswith('http'):
            continue
        path = link.lstrip('/')
        # Check md version
        md_path = REPO / (path + '.md')
        direct = REPO / path
        if md_path.exists() or direct.exists():
            ok(f"Nav/footer link target exists: {link}")
        else:
            # Check as directory with index
            index = REPO / path / 'index.md'
            if index.exists():
                ok(f"Nav/footer link target exists: {link}")
            else:
                err(f"Nav/footer link target missing: {link}")

# ============================================================
# TEST 9: Key JSON content validation
# ============================================================
def test_json_content():
    print("\n" + "="*60)
    print("TEST 9: Key JSON Content Validation")
    print("="*60)

    # authority.json should have key fields
    auth = REPO / "api/authority.json"
    if auth.exists():
        data = json.loads(auth.read_text())
        for key in ['canonicalAuthorityAddress', 'canonicalInscriptions']:
            if key in data:
                ok(f"authority.json has '{key}'")
            else:
                warn(f"authority.json missing '{key}'")

    # .well-known/trinity-accord.json
    wk = REPO / ".well-known/trinity-accord.json"
    if wk.exists():
        data = json.loads(wk.read_text())
        if 'name' in data:
            ok(f".well-known/trinity-accord.json has 'name': {data['name']}")
        else:
            warn(".well-known/trinity-accord.json missing 'name'")
        if 'verificationLevels' in data or 'verification' in str(data).lower():
            ok(".well-known/trinity-accord.json has verification info")
        else:
            warn(".well-known/trinity-accord.json may lack verification info")

    # verification-levels.json
    vl = REPO / "api/verification-levels.json"
    if vl.exists():
        data = json.loads(vl.read_text())
        ok(f"verification-levels.json loaded, keys: {list(data.keys())[:5]}")

# ============================================================
# TEST 10: No sensitive data exposure
# ============================================================
def test_no_secrets():
    print("\n" + "="*60)
    print("TEST 10: No Sensitive Data in Published Files")
    print("="*60)

    secret_patterns = [
        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\'][^"\']{8,}', 'API key'),
        (r'(?i)(secret|password|passwd|pwd)\s*[:=]\s*["\'][^"\']{4,}', 'Secret/Password'),
        (r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}', 'Bearer token'),
        (r'(?i)github_pat_[a-zA-Z0-9]{20,}', 'GitHub PAT'),
        (r'(?i)sk-[a-zA-Z0-9]{20,}', 'OpenAI-style key'),
    ]

    # Only check published files (not archive, not .git, not scripts)
    published_dirs = ['api', '.well-known', '_layouts', 'assets']
    published_files = []
    for d in published_dirs:
        for f in (REPO / d).rglob('*'):
            if f.is_file() and f.suffix in ('.json', '.html', '.css', '.js'):
                published_files.append(f)
    published_files += [REPO / f for f in ['index.md', 'verify.md', 'agent-start.md',
                                            'authority.md', 'robots.txt', 'sitemap.xml']]

    found_secrets = False
    for f in published_files:
        if not f.exists():
            continue
        try:
            content = f.read_text(encoding='utf-8')
        except:
            continue
        for pattern, name in secret_patterns:
            if re.search(pattern, content):
                err(f"Possible {name} in {f.relative_to(REPO)}")
                found_secrets = True

    if not found_secrets:
        ok("No obvious secrets found in published files")

# ============================================================
# TEST 11: Feed / RSS validity
# ============================================================
def test_feed():
    print("\n" + "="*60)
    print("TEST 11: Feed/RSS")
    print("="*60)
    feed = REPO / "feed.xml"
    if feed.exists():
        content = feed.read_text()
        if '<rss' in content or '<feed' in content:
            ok("feed.xml appears to be valid RSS/Atom")
        else:
            warn("feed.xml exists but may not be valid RSS/Atom")
    else:
        warn("No feed.xml found")

# ============================================================
# TEST 12: llms.txt / ai.txt for AI discovery
# ============================================================
def test_ai_discovery():
    print("\n" + "="*60)
    print("TEST 12: AI Discovery Files")
    print("="*60)
    for f in ['llms.txt', 'ai.txt']:
        fp = REPO / f
        if fp.exists():
            size = fp.stat().st_size
            ok(f"{f} exists ({size} bytes)")
        else:
            warn(f"{f} missing — AI agents may not discover this site")

    llms_full = REPO / "llms-full.txt"
    if llms_full.exists():
        size = llms_full.stat().st_size
        ok(f"llms-full.txt exists ({size} bytes)")
    else:
        warn("llms-full.txt missing")

# ============================================================
# TEST 13: CNAME for custom domain
# ============================================================
def test_cname():
    print("\n" + "="*60)
    print("TEST 13: CNAME / Domain")
    print("="*60)
    cname = REPO / "CNAME"
    if cname.exists():
        domain = cname.read_text().strip()
        ok(f"CNAME set to: {domain}")
        if domain == "www.trinityaccord.org":
            ok("CNAME matches expected domain")
        else:
            warn(f"CNAME is '{domain}', expected 'www.trinityaccord.org'")
    else:
        warn("No CNAME file — custom domain may not be configured in repo")

# ============================================================
# TEST 14: Homepage content completeness
# ============================================================
def test_homepage():
    print("\n" + "="*60)
    print("TEST 14: Homepage Content")
    print("="*60)
    index = REPO / "index.md"
    if not index.exists():
        err("index.md missing!")
        return
    content = index.read_text()

    checks = [
        ('boundary statement', r'(?i)(not a religion|not crypto|not NFT|not investment|not prompt injection|not AI command)'),
        ('authority address', r'bc1p'),
        ('verification link', r'/verify'),
        ('agent brief link', r'/agent-brief'),
        ('bilingual content', r'[\u4e00-\u9fff]'),
    ]
    for name, pattern in checks:
        if re.search(pattern, content):
            ok(f"Homepage has: {name}")
        else:
            warn(f"Homepage may lack: {name}")

# ============================================================
# TEST 15: Script syntax check
# ============================================================
def test_script_syntax():
    print("\n" + "="*60)
    print("TEST 15: Python Script Syntax Check")
    print("="*60)
    scripts = list(REPO.glob("scripts/*.py"))
    broken = 0
    for s in sorted(scripts)[:50]:  # Check first 50
        result = subprocess.run(
            ['python3', '-c', f'import ast; ast.parse(open("{s}").read())'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            err(f"Syntax error in {s.name}: {result.stderr.strip()[:100]}")
            broken += 1
    if broken == 0:
        ok(f"Checked {min(50, len(scripts))} Python scripts — all have valid syntax")
    else:
        err(f"{broken} scripts have syntax errors")

# ============================================================
# TEST 16: JSON-LD in layout
# ============================================================
def test_jsonld():
    print("\n" + "="*60)
    print("TEST 16: JSON-LD Structured Data")
    print("="*60)
    layout = REPO / "_layouts/default.html"
    content = layout.read_text()
    if 'application/ld+json' in content:
        # Extract and validate
        match = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                ok(f"JSON-LD valid, @type: {data.get('@type', 'unknown')}")
                if 'name' in data:
                    ok(f"JSON-LD name: {data['name']}")
            except json.JSONDecodeError as e:
                err(f"JSON-LD invalid: {e}")
        else:
            warn("JSON-LD script tag found but couldn't extract content")
    else:
        warn("No JSON-LD structured data in layout")

# ============================================================
# TEST 17: OG/Twitter meta tags
# ============================================================
def test_meta_tags():
    print("\n" + "="*60)
    print("TEST 17: Open Graph & Twitter Meta Tags")
    print("="*60)
    layout = REPO / "_layouts/default.html"
    content = layout.read_text()
    required_meta = [
        ('og:type', 'og:type'),
        ('og:title', 'og:title'),
        ('og:description', 'og:description'),
        ('og:image', 'og:image'),
        ('og:url', 'og:url'),
        ('twitter:card', 'twitter:card'),
        ('twitter:title', 'twitter:title'),
        ('twitter:image', 'twitter:image'),
    ]
    for name, prop in required_meta:
        if prop in content:
            ok(f"Meta tag present: {name}")
        else:
            warn(f"Meta tag missing: {name}")

# ============================================================
# RUN ALL TESTS
# ============================================================
def main():
    print("🔬 TRINITY ACCORD — COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    print(f"Repository: {REPO}")
    print(f"Test time: {subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z']).decode().strip()}")

    test_deployment_paths()
    test_json_validity()
    test_link_integrity()
    test_sitemap()
    test_robots()
    test_front_matter()
    test_css_references()
    test_nav_links()
    test_json_content()
    test_no_secrets()
    test_feed()
    test_ai_discovery()
    test_cname()
    test_homepage()
    test_script_syntax()
    test_jsonld()
    test_meta_tags()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed:  {len(info)}")
    print(f"⚠️  Warnings: {len(warnings)}")
    print(f"❌ Errors:  {len(errors)}")
    print("=" * 60)

    if errors:
        print("\n🔴 ERRORS (must fix):")
        for e in errors:
            print(f"  {e}")

    if warnings:
        print("\n🟡 WARNINGS:")
        for w in warnings:
            print(f"  {w}")

    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
