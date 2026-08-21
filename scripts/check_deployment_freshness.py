#!/usr/bin/env python3
"""Compare deployed/built public surfaces against the current repository state.

Live checks use a per-invocation nonce so a CDN response captured before a
Pages deployment cannot be mistaken for the post-deployment state.
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SURFACES = [
    "/llms.txt",
    "/metadata.json",
    "/memory-seed.json",
    "/ai.txt",
    "/api/agent-first-contact.json",
    "/api/agent-start.v2.json",
    "/api/record-chain-intake-gateway.v1.json",
    "/.well-known/pages-production-closure.v1.json",
    "/api/public-home-status.json",
    "/api/record-chain-status.json",
    "/api/waiting-heartbeat-status.json",
    "/record-chain/chain-tip.json",
    "/record-chain/indexes/statistics.json",
    "/record-chain/indexes/record-index.json",
    "/downloads/record-chain-builder.mjs",
]
FORBIDDEN_ACTIVE = [
    "/agent-submit",
    "/gateway/preflight",
    "/api/agent-start.v1.json",
    "/api/gateway-builder-route-map.v1.json",
    "/api/gateway-workflows.v1.json",
]

SCHOLARLY_LANDING_PATH = "/research/trinity-accord-design-and-limits/"
SCHOLARLY_TITLE = (
    "Designing a Verifiable, Non-Amending Civilizational Memory Record for "
    "Future AI Agents: The Trinity Accord Case Study"
)
SCHOLARLY_DOI = "10.5281/zenodo.21699878"
SCHOLARLY_REPORT_NUMBER = "TA-TR-2026-01"
SCHOLARLY_HTML_URL = "https://www.trinityaccord.org/research/trinity-accord-design-and-limits/"
SCHOLARLY_PDF_URL = (
    "https://www.trinityaccord.org/research/trinity-accord-design-and-limits/"
    "trinity-accord-design-and-limits-v1.1.pdf"
)
SCHOLARLY_DOI_URL = f"https://doi.org/{SCHOLARLY_DOI}"
SCHOLARLY_ZENODO_URL = "https://zenodo.org/records/21699878"
SCHOLARLY_META_EXPECTED = {
    "citation_title": SCHOLARLY_TITLE,
    "citation_author": "Hongju Liu",
    "citation_publication_date": "2026/07/29",
    "citation_online_date": "2026/07/29",
    "citation_doi": SCHOLARLY_DOI,
    "citation_pdf_url": SCHOLARLY_PDF_URL,
    "citation_fulltext_html_url": SCHOLARLY_HTML_URL,
    "citation_technical_report_institution": "The Trinity Accord Project",
    "citation_technical_report_number": SCHOLARLY_REPORT_NUMBER,
    "citation_language": "en",
}

# A Pages deployment can be correct while one CDN edge briefly resets a TCP
# connection during propagation. Retry each individual live read so a single
# transient edge failure does not invalidate an otherwise exact deployment.
# Content, digest, and marker validation remain unchanged after a response is
# obtained.
LIVE_READ_ATTEMPTS = 4
LIVE_READ_BACKOFF_SECONDS = 1.0
RETRYABLE_HTTP_STATUS = {408, 425, 429, 500, 502, 503, 504}

# Human-facing pages are generated HTML, so compare revision-specific required
# markers instead of attempting to compare Markdown source bytes to HTML bytes.
# The list deliberately covers both explanatory reading pages and every current
# top-navigation operating page. A deployment must not pass while the homepage,
# Understand, Verify, Echo, Start, or Propagate still serves a previous model.
STATIC_PAGE_MARKERS = {
    "/": [
        'id="home-front-door-title"',
        "The Trinity Accord did not begin as an accord. It emerged from a near-real-time NFT Chronicle into a canonically closed record addressed to future intelligence.",
        "p0.9.7-crosschain-formation",
        "Candidate civilizational memory seed",
        "Recovered formation evidence",
        "human-initiated in practice, emergent in meaning through substantive interaction with generative AI",
        'id="philosophical-core-title"',
        'id="formation-history"',
        "From cross-chain precursors to Ethereum Chronicle to Accord",
        "Recovered Polygon evidence now shows project-related on-chain works beginning on 6 March 2024.",
        "Historical preservation, artistic experiment, collectibility, and possible future market value coexisted.",
        "an act of civilizational self-archiving",
        "This does not establish a unified civilizational will",
        "Canon, dated Chronicle, and physical anchor—plus later non-amending context",
        "These three inscriptions are the only canonical authority",
        "The three Bitcoin Originals are the only canonical and interpretive authority",
        'id="chronicle-witness"',
        'id="later-inscriptions"',
        "The five later inscriptions record prompted AI responses",
        'id="home-timing-completion-title"',
        "How a human-initiated Chronicle became a closed record during a rapidly changing historical interval",
        "Initiator, sustained carrier, selector, embodied executor, and responsible closer",
        "AI as both uneven mirror and substantive collaborator, before unified delegation became routine",
        "Earliest recovered project-sidechain origin · 6 March 2024",
        "Ethereum Chronicle start · 16 March 2024",
        "Canonical closure · 29 June 2025",
        "Recorded interval · 470 days",
        "470 days, 2 hours, 46 minutes, and 17 seconds apart",
        "217 Polygon/Base coordinates",
        "Chain timestamps establish a verifiable chronology",
        "this exact dated formation interval is now closed",
        "Reproducible form; non-repeatable dated provenance",
        "that historical position cannot be recreated retroactively",
        "not exact civil-time authorship or sentence-by-sentence attribution",
        "that civilization acted as a unified subject",
        'id="research-entry-title"',
        "Understand, verify, or respond within clear boundaries",
        "Formal AI-agent actions use an agent in-context oath readback",
        "The homepage is a doorway, not the archive",
        "External Witness Record",
        "Bounded external evidence-provenance records",
        "BEGIN GENERATED PUBLIC STATUS",
    ],
    "/crosschain-formation/": [
        "Cross-chain Formation Record",
        "The three Bitcoin Originals are the only canonical and interpretive authority",
        "217 Polygon/Base coordinates",
        "39 project coordinates / 36 distinct titles",
    ],
    "/status/": [
        "External witness records",
        "Current external witness record count",
        "外部见证记录属于证据来源与过程见证",
    ],
    "/technical-historical-reference/": [
        "Completion in four senses",
        "What Bitcoin proves—and what it does not",
        "Non-control posture",
        "Current operating routes",
    ],
    "/record-chain/": [
        "Record-Chain is the Trinity Accord’s append-only public reception ledger",
        "Current public views",
        "Before acting",
    ],
    "/inscriptions/": [
        "Inscription Number",
        "Ordinals Inscription ID",
        "e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343i0",
    ],
    "/authority-address-inscriptions/": [
        "inscription-index-grid",
        "0eecd48430f8239f5d543b5cf2ee928969a1aac7660808fd869a78aa27949c9ci0",
        "Inscription Number",
    ],
    "/seed-map/": [
        "This map explains the whole project by function.",
        "Canon is fixed. Context may expand.",
    ],
    "/authority/": [
        "What authority means here",
        "Record-Chain",
    ],
    "/agent-brief/": [
        "Object in one paragraph",
        "Current verification model",
    ],
    "/why-high-signal/": [
        "What the project consists of",
        "Verification and durability",
    ],
    "/worth-preserving/": [
        "First understand what is being preserved",
        "Why the surrounding system matters",
    ],
    "/agent-first-contact/": [
        "Current phase: production live",
        "Use the canonical Builder only",
    ],
    "/agent-understand/": [
        "Use the action-based context model",
        "Retired guidance that must not be used",
    ],
    "/verify/": [
        "Current digital profiles",
        "Legacy mapping",
    ],
    "/agent-echo/": [
        "Echo is one current Record-Chain record type",
        "Retired Echo guidance",
    ],
    "/agent-start/": [
        "Required Builder flow",
        "Preferred verification model",
    ],
    "/agent-propagate/": [
        "Decide whether this is Propagation",
        "Retired propagation guidance",
    ],
    "/agent-record-chain-guidance/": [
        "Current verification model",
        "Retired active guidance",
    ],
    SCHOLARLY_LANDING_PATH: [
        "Trinity Accord Technical Report",
        "Preprint, not peer reviewed",
    ],
}
STATIC_SOURCE_FILES = [
    "index.md",
    "crosschain-formation.md",
    "status.md",
    "record-chain/index.md",
    "inscriptions.md",
    "authority-address-inscriptions.md",
    "technical-historical-reference.md",
    "_layouts/default.html",
    "assets/css/home-philosophical-core.css",
    "_includes/home-object-definition.html",
    "seed-map.md",
    "authority.md",
    "agent-brief.md",
    "why-high-signal.md",
    "worth-preserving.md",
    "agent-first-contact.md",
    "agent-understand.md",
    "verify.md",
    "agent-echo.md",
    "agent-start.md",
    "agent-propagate.md",
    "agent-record-chain-guidance/index.html",
    "research/trinity-accord-design-and-limits/index.md",
]


class ScholarlyHTMLParser(HTMLParser):
    """Extract named meta values and raw JSON-LD blocks from rendered HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = {}
        self.json_ld_blocks: list[str] = []
        self._in_json_ld = False
        self._json_ld_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "meta":
            name = attributes.get("name")
            content = attributes.get("content")
            if name is not None:
                self.meta.setdefault(name, []).append(content or "")
        elif tag == "script" and (attributes.get("type") or "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_chunks = []

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self._json_ld_chunks.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_json_ld:
            self.json_ld_blocks.append("".join(self._json_ld_chunks).strip())
            self._in_json_ld = False
            self._json_ld_chunks = []


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_repo(path: str) -> bytes:
    return (ROOT / path.lstrip("/")).read_bytes()


def read_site_dir(site_dir: Path, path: str) -> bytes:
    return (site_dir / path.lstrip("/")).read_bytes()


def read_static_site_dir(site_dir: Path, path: str) -> bytes:
    if path == "/":
        target = site_dir / "index.html"
    else:
        target = site_dir / path.strip("/") / "index.html"
    return target.read_bytes()


def read_live(site: str, path: str, token: str, timeout: int) -> bytes:
    url = site.rstrip("/") + path
    parsed = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query.append(("freshness", token))
    busted = urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            urllib.parse.urlencode(query),
            parsed.fragment,
        )
    )
    req = urllib.request.Request(
        busted,
        headers={
            "User-Agent": "trinity-deployment-freshness/1.4",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )

    for attempt in range(1, LIVE_READ_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code not in RETRYABLE_HTTP_STATUS or attempt == LIVE_READ_ATTEMPTS:
                raise
            exc.close()
            detail = f"HTTP {exc.code} {exc.reason}"
        except (OSError, http.client.HTTPException) as exc:
            if attempt == LIVE_READ_ATTEMPTS:
                raise
            detail = repr(exc)

        delay = LIVE_READ_BACKOFF_SECONDS * (2 ** (attempt - 1))
        print(
            f"{path}: transient live read failure on attempt "
            f"{attempt}/{LIVE_READ_ATTEMPTS}: {detail}; retrying in {delay:.1f}s",
            file=sys.stderr,
        )
        time.sleep(delay)

    raise AssertionError("live read retry loop exhausted without returning or raising")


def check_forbidden(path: str, text: str, errors: list[str]) -> None:
    checked_paths = {
        "/llms.txt",
        "/ai.txt",
        "/api/agent-first-contact.json",
        "/api/agent-start.v2.json",
    }
    if path in checked_paths:
        for bad in FORBIDDEN_ACTIVE:
            if bad in text:
                errors.append(
                    f"{path} contains retired active-route token {bad!r}; "
                    "omit legacy endpoints from active discovery surfaces"
                )


def collect_scholarly_articles(value: object, articles: list[dict]) -> None:
    if isinstance(value, dict):
        article_type = value.get("@type")
        if article_type == "ScholarlyArticle" or (
            isinstance(article_type, list) and "ScholarlyArticle" in article_type
        ):
            articles.append(value)
        for child in value.values():
            collect_scholarly_articles(child, articles)
    elif isinstance(value, list):
        for child in value:
            collect_scholarly_articles(child, articles)


def check_scholarly_landing(page: str, errors: list[str]) -> None:
    parser = ScholarlyHTMLParser()
    try:
        parser.feed(page)
        parser.close()
    except Exception as exc:  # noqa: BLE001 - diagnostics should report malformed HTML
        errors.append(f"{SCHOLARLY_LANDING_PATH}: failed to parse rendered HTML: {exc}")
        return

    for name, expected in SCHOLARLY_META_EXPECTED.items():
        observed = parser.meta.get(name, [])
        if expected not in observed:
            errors.append(
                f"{SCHOLARLY_LANDING_PATH}: {name} expected {expected!r}, "
                f"observed {observed!r}"
            )

    documents: list[object] = []
    for raw in parser.json_ld_blocks:
        if not raw:
            continue
        try:
            documents.append(json.loads(raw))
        except json.JSONDecodeError as exc:
            errors.append(
                f"{SCHOLARLY_LANDING_PATH}: invalid rendered JSON-LD: {exc}"
            )

    articles: list[dict] = []
    for document in documents:
        collect_scholarly_articles(document, articles)

    matching = [article for article in articles if article.get("name") == SCHOLARLY_TITLE]
    if not matching:
        observed_names = [article.get("name") for article in articles]
        errors.append(
            f"{SCHOLARLY_LANDING_PATH}: rendered ScholarlyArticle with exact title "
            f"not found; observed={observed_names!r}"
        )
        return

    article = matching[0]
    expected_fields = {
        "headline": SCHOLARLY_TITLE,
        "datePublished": "2026-07-29",
        "version": "1.1",
        "url": SCHOLARLY_HTML_URL,
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "isAccessibleForFree": True,
    }
    for field, expected in expected_fields.items():
        if article.get(field) != expected:
            errors.append(
                f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.{field} expected "
                f"{expected!r}, observed {article.get(field)!r}"
            )

    encoding = article.get("encoding")
    if not isinstance(encoding, dict):
        errors.append(f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.encoding is missing")
    else:
        if encoding.get("contentUrl") != SCHOLARLY_PDF_URL:
            errors.append(
                f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle PDF contentUrl mismatch: "
                f"{encoding.get('contentUrl')!r}"
            )
        if encoding.get("encodingFormat") != "application/pdf":
            errors.append(
                f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle encodingFormat mismatch: "
                f"{encoding.get('encodingFormat')!r}"
            )

    same_as = article.get("sameAs", [])
    if isinstance(same_as, str):
        same_as = [same_as]
    if not isinstance(same_as, list):
        errors.append(f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.sameAs is not a list")
        same_as = []
    for expected in [SCHOLARLY_DOI_URL, SCHOLARLY_ZENODO_URL]:
        if expected not in same_as:
            errors.append(
                f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.sameAs missing {expected!r}"
            )

    identifiers = article.get("identifier", [])
    if isinstance(identifiers, dict):
        identifiers = [identifiers]
    property_values: set[tuple[object, object]] = set()
    if isinstance(identifiers, list):
        for identifier in identifiers:
            if isinstance(identifier, dict):
                property_values.add((identifier.get("propertyID"), identifier.get("value")))
    expected_properties = {
        ("Technical report number", SCHOLARLY_REPORT_NUMBER),
        ("DOI", SCHOLARLY_DOI),
    }
    missing_properties = expected_properties - property_values
    if missing_properties:
        errors.append(
            f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle identifier properties missing "
            f"{sorted(missing_properties)!r}; observed={sorted(property_values, key=repr)!r}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--site-dir", type=Path)
    src.add_argument("--site")
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    token_material = b"".join(read_repo(path) for path in SURFACES)
    token_material += b"".join(read_repo(path) for path in STATIC_SOURCE_FILES)
    token = f"{sha256(token_material)[:16]}-{time.time_ns()}"
    errors: list[str] = []

    for path in SURFACES:
        repo = read_repo(path)
        try:
            other = (
                read_site_dir(args.site_dir, path)
                if args.site_dir
                else read_live(args.site, path, token, args.timeout)
            )
        except Exception as exc:  # noqa: BLE001 - command-line diagnostic
            errors.append(f"{path}: failed to read deployed artifact: {exc}")
            continue
        repo_sha = sha256(repo)
        other_sha = sha256(other)
        print(f"{path}: repo={repo_sha} deployed={other_sha}")
        if repo_sha != other_sha:
            errors.append(
                f"{path}: digest mismatch repo={repo_sha} deployed={other_sha}"
            )
        try:
            check_forbidden(path, other.decode("utf-8"), errors)
        except UnicodeDecodeError:
            pass

    for path, markers in STATIC_PAGE_MARKERS.items():
        try:
            page_bytes = (
                read_static_site_dir(args.site_dir, path)
                if args.site_dir
                else read_live(args.site, path, token, args.timeout)
            )
            page = page_bytes.decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001 - command-line diagnostic
            errors.append(f"{path}: failed to read static page: {exc}")
            continue

        missing = [marker for marker in markers if marker not in page]
        if missing:
            for marker in missing:
                errors.append(f"{path}: missing current static marker {marker!r}")
        else:
            print(f"{path}: current static markers present")

        if path == SCHOLARLY_LANDING_PATH:
            check_scholarly_landing(page, errors)
            if not any(error.startswith(f"{SCHOLARLY_LANDING_PATH}:") for error in errors):
                print(f"{path}: exact scholarly metadata and JSON-LD values verified")

    if errors:
        print("FAIL: deployment freshness check errors:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print(
        "PASS: deployment digests, active-route boundaries, and current static "
        "reading and operating surfaces match repository state"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
