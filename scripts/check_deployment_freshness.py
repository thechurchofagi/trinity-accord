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

# In the HTML tree builder's "in head" insertion mode, these start tags do not
# implicitly close the document head. A body-content start tag such as <main>
# does. Tracking this prevents metadata from an implied body from being accepted
# when optional </head> and <body> tags are omitted.
HEAD_MODE_START_TAGS = {
    "base",
    "basefont",
    "bgsound",
    "head",
    "html",
    "link",
    "meta",
    "noframes",
    "noscript",
    "script",
    "style",
    "template",
    "title",
}
AFTER_HEAD_MODE_START_TAGS = {
    "base",
    "basefont",
    "bgsound",
    "html",
    "link",
    "meta",
    "noframes",
    "script",
    "style",
    "template",
}
HEAD_TEXT_TAGS = {"noframes", "noscript", "script", "style", "title"}
HTML_VOID_ELEMENTS = {
    "area",
    "base",
    "basefont",
    "bgsound",
    "br",
    "col",
    "embed",
    "frame",
    "hr",
    "img",
    "input",
    "keygen",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
SCHEMA_ORG_BASES = {"http://schema.org", "https://schema.org"}
SCHEMA_ORG_VOCAB_BASES = {"http://schema.org/", "https://schema.org/"}
SCHEMA_ORG_REMOTE_CONTEXTS = SCHEMA_ORG_BASES | SCHEMA_ORG_VOCAB_BASES
SCHEMA_ORG_ARTICLE_IRIS = {
    f"{base}/ScholarlyArticle" for base in SCHEMA_ORG_BASES
}
SCHOLARLY_SCHEMA_TERMS = {
    "ScholarlyArticle",
    "name",
    "headline",
    "datePublished",
    "version",
    "url",
    "license",
    "isAccessibleForFree",
    "encoding",
    "contentUrl",
    "encodingFormat",
    "sameAs",
    "identifier",
    "propertyID",
    "value",
}
SchemaContextState = tuple[
    bool, dict[str, bool], dict[str, str], bool, frozenset[str]
]
DEFAULT_SCHEMA_CONTEXT_STATE: SchemaContextState = (
    False, {}, {}, False, frozenset()
)

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


def _first_attributes(
    attrs: list[tuple[str, str | None]],
) -> tuple[dict[str, str | None], set[str], dict[str, list[str | None]]]:
    """Return browser-first attributes plus duplicate names and all raw values."""
    first: dict[str, str | None] = {}
    duplicates: set[str] = set()
    values: dict[str, list[str | None]] = {}
    for raw_name, value in attrs:
        name = raw_name.lower()
        values.setdefault(name, []).append(value)
        if name in first:
            duplicates.add(name)
        else:
            first[name] = value
    return first, duplicates, values


class ScholarlyHTMLParser(HTMLParser):
    """Extract browser-visible head citation meta and document-wide JSON-LD."""

    _SVG_HTML_INTEGRATION_POINTS = {"foreignobject", "desc", "title"}
    _MATHML_TEXT_INTEGRATION_POINTS = {"mi", "mo", "mn", "ms", "mtext"}
    _MATHML_HTML_ENCODINGS = {"text/html", "application/xhtml+xml"}
    _FOREIGN_HTML_BREAKOUT_TAGS = {
        "b", "big", "blockquote", "body", "br", "center", "code",
        "dd", "div", "dl", "dt", "em", "embed", "h1", "h2",
        "h3", "h4", "h5", "h6", "head", "hr", "i", "img",
        "li", "listing", "menu", "meta", "nobr", "ol", "p",
        "pre", "ruby", "s", "small", "span", "strong", "strike",
        "sub", "sup", "table", "tt", "u", "ul", "var",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.meta: dict[str, list[str]] = {}
        self.json_ld_blocks: list[str] = []
        self.errors: list[str] = []
        self._in_head = False
        self._after_head = False
        self._head_seen = False
        self._body_started = False
        self._template_depth = 0
        # Retained as a diagnostic counter for open SVG/MathML-namespace
        # elements. Namespace-sensitive decisions use _element_stack so
        # HTML integration points are handled correctly.
        self._foreign_content_depth = 0
        self._element_stack: list[
            tuple[str, str, dict[str, str | None]]
        ] = []
        self._head_text_stack: list[str] = []
        self._in_noscript_raw = False
        self._in_json_ld = False
        self._json_ld_chunks: list[str] = []

    def _namespace_for_start(
        self,
        tag: str,
        attributes: dict[str, str | None],
    ) -> str:
        if not self._element_stack:
            return "html"
        parent_tag, parent_namespace, parent_attributes = self._element_stack[-1]
        if parent_namespace == "html":
            if tag == "svg":
                return "svg"
            if tag == "math":
                return "math"
            return "html"
        if parent_namespace == "svg":
            if parent_tag in self._SVG_HTML_INTEGRATION_POINTS:
                if tag == "svg":
                    return "svg"
                if tag == "math":
                    return "math"
                return "html"
            return "svg"
        if parent_namespace == "math":
            if (
                parent_tag in self._MATHML_TEXT_INTEGRATION_POINTS
                and tag not in {"mglyph", "malignmark"}
            ):
                if tag == "svg":
                    return "svg"
                if tag == "math":
                    return "math"
                return "html"
            if parent_tag == "annotation-xml":
                encoding = (parent_attributes.get("encoding") or "").lower()
                if encoding in self._MATHML_HTML_ENCODINGS:
                    if tag == "svg":
                        return "svg"
                    if tag == "math":
                        return "math"
                    return "html"
            return "math"
        return "html"

    @classmethod
    def _is_foreign_html_breakout(
        cls, tag: str, attributes: dict[str, str | None]
    ) -> bool:
        if tag in cls._FOREIGN_HTML_BREAKOUT_TAGS:
            return True
        return tag == "font" and any(
            name in attributes for name in {"color", "face", "size"}
        )

    def _pop_open_foreign_content(self) -> None:
        while self._element_stack and self._element_stack[-1][1] != "html":
            _tag, namespace, _attributes = self._element_stack.pop()
            if namespace != "html":
                self._foreign_content_depth = max(
                    0, self._foreign_content_depth - 1
                )

    def _push_element(
        self,
        tag: str,
        namespace: str,
        attributes: dict[str, str | None],
    ) -> None:
        self._element_stack.append((tag, namespace, attributes))
        if namespace != "html":
            self._foreign_content_depth += 1
        if tag == "template" and namespace == "html":
            self._template_depth += 1

    def _pop_through_matching_element(self, tag: str) -> str | None:
        match_index = None
        for index in range(len(self._element_stack) - 1, -1, -1):
            stack_tag, stack_namespace, _attributes = self._element_stack[index]
            if (
                stack_tag == "template"
                and stack_namespace == "html"
                and tag != "template"
            ):
                # HTML template contents form a tree-builder boundary. An end
                # tag outside the template insertion mode cannot pop through an
                # open HTML template to close an ancestor document element.
                break
            if stack_tag == tag:
                match_index = index
                break
        if match_index is None:
            return None
        matched_namespace = self._element_stack[match_index][1]
        popped = self._element_stack[match_index:]
        del self._element_stack[match_index:]
        for popped_tag, namespace, _attributes in popped:
            if namespace != "html":
                self._foreign_content_depth = max(
                    0, self._foreign_content_depth - 1
                )
            if popped_tag == "template" and namespace == "html":
                self._template_depth = max(0, self._template_depth - 1)
        return matched_namespace

    def _handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
        *,
        self_closing: bool,
    ) -> None:
        tag = tag.lower()
        if self._in_noscript_raw:
            return
        attributes, duplicates, values = _first_attributes(attrs)
        namespace = self._namespace_for_start(tag, attributes)
        if (
            namespace != "html"
            and self._is_foreign_html_breakout(tag, attributes)
        ):
            self._pop_open_foreign_content()
            namespace = self._namespace_for_start(tag, attributes)

        # A non-head HTML start tag implicitly ends the optional document
        # head even when both </head> and <body> are omitted.
        if (
            namespace == "html"
            and self._in_head
            and self._template_depth == 0
            and not self._head_text_stack
            and tag not in HEAD_MODE_START_TAGS
        ):
            self._in_head = False
            self._after_head = False
            self._body_started = True

        # In the tree builder's after-head insertion mode, a small set of
        # metadata-bearing tokens are processed using the head element pointer.
        # Other HTML start tags begin the body-effective portion of the document.
        if (
            namespace == "html"
            and self._after_head
            and self._template_depth == 0
            and not self._head_text_stack
            and tag not in AFTER_HEAD_MODE_START_TAGS
        ):
            self._after_head = False
            self._body_started = True

        if (
            namespace == "html"
            and tag == "body"
            and self._template_depth == 0
            and not self._head_text_stack
        ):
            self._body_started = True
            self._in_head = False
            self._after_head = False

        if (
            namespace == "html"
            and tag == "head"
            and not self._head_seen
            and not self._body_started
        ):
            self._head_seen = True
            self._in_head = True
            self._after_head = False

        # Foreign-content self-closing syntax is acknowledged; HTML
        # self-closing syntax on non-void elements is ignored.
        should_push = not (
            namespace != "html" and self_closing
        ) and not (
            namespace == "html" and tag in HTML_VOID_ELEMENTS
        )
        if should_push:
            self._push_element(tag, namespace, attributes)

        if (
            namespace == "html"
            and tag in HEAD_TEXT_TAGS
            and (self._in_head or self._after_head)
            and self._template_depth == 0
        ):
            self._head_text_stack.append(tag)

        if namespace == "html" and tag == "noscript":
            # With scripting enabled, noscript content is raw text.
            self._in_noscript_raw = True

        if (
            namespace == "html"
            and tag == "meta"
            and (self._in_head or self._after_head)
            and self._template_depth == 0
        ):
            name_values = [
                value for value in values.get("name", []) if value is not None
            ]
            scholarly_candidate = any(
                value in SCHOLARLY_META_EXPECTED for value in name_values
            )
            relevant_duplicates = duplicates & {"name", "content"}
            if scholarly_candidate and relevant_duplicates:
                self.errors.append(
                    "scholarly meta contains duplicate attribute(s): "
                    + ", ".join(sorted(relevant_duplicates))
                )
            name = attributes.get("name")
            content = attributes.get("content")
            if name is not None:
                self.meta.setdefault(name, []).append(content or "")

        if (
            namespace == "html"
            and tag == "script"
            and self._template_depth == 0
        ):
            type_values = [
                value for value in values.get("type", []) if value is not None
            ]
            contains_json_ld_type = any(
                value.lower() == "application/ld+json" for value in type_values
            )
            if contains_json_ld_type and "type" in duplicates:
                self.errors.append(
                    "scholarly JSON-LD script contains duplicate type attribute"
                )
            script_type = attributes.get("type") or ""
            if script_type.lower() == "application/ld+json":
                self._in_json_ld = True
                self._json_ld_chunks = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._handle_starttag(tag, attrs, self_closing=False)

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        self._handle_starttag(tag, attrs, self_closing=True)

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self._json_ld_chunks.append(data)
        if (
            (self._in_head or self._after_head)
            and self._template_depth == 0
            and not self._head_text_stack
            and data.strip("\t\n\f\r ")
        ):
            self._in_head = False
            self._after_head = False
            self._body_started = True

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._in_noscript_raw:
            if tag != "noscript":
                return
            self._in_noscript_raw = False
        if tag == "script" and self._in_json_ld:
            self.json_ld_blocks.append(
                "".join(self._json_ld_chunks).strip()
            )
            self._in_json_ld = False
            self._json_ld_chunks = []
        if (
            tag in {"body", "html", "br"}
            and (self._in_head or self._after_head)
            and self._template_depth == 0
            and not self._head_text_stack
        ):
            self._in_head = False
            self._after_head = False
            self._body_started = True
        if self._head_text_stack and tag == self._head_text_stack[-1]:
            self._head_text_stack.pop()

        matched_namespace = self._pop_through_matching_element(tag)

        if (
            tag == "head"
            and matched_namespace == "html"
            and self._in_head
            and self._template_depth == 0
        ):
            self._in_head = False
            self._after_head = True
        if (
            tag == "body"
            and matched_namespace == "html"
            and self._template_depth == 0
        ):
            self._body_started = True
            self._in_head = False
            self._after_head = False


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


def _normalized_schema_url(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return value


def _expand_compact_iri(value: str, prefixes: dict[str, str]) -> str:
    if value != value.strip():
        return value
    stripped = value
    if ":" not in stripped:
        return stripped
    prefix, suffix = stripped.split(":", 1)
    if suffix.startswith("//"):
        return stripped
    base = prefixes.get(prefix)
    if base is None:
        return stripped
    return base + suffix


def _prefix_mapping(
    definition: object,
    prefixes: dict[str, str],
) -> str | None:
    explicit_prefix: bool | None = None
    if isinstance(definition, dict):
        if definition.get("@prefix") is False:
            return None
        if definition.get("@prefix") is True:
            explicit_prefix = True
        definition = definition.get("@id")
    if not isinstance(definition, str):
        return None
    expanded = _expand_compact_iri(definition, prefixes)
    if not expanded.startswith(("http://", "https://")):
        return None
    if explicit_prefix is True or (
        explicit_prefix is None and expanded.endswith(("/", "#"))
    ):
        return expanded
    return None


def _term_maps_to_schema_term(
    value: object,
    term: str,
    vocab_is_schema: bool,
    prefixes: dict[str, str],
) -> bool:
    if isinstance(value, dict):
        if "@reverse" in value:
            return False
        if "@id" not in value:
            return vocab_is_schema
        value = value.get("@id")
    if not isinstance(value, str):
        return False
    stripped = value.strip()
    expanded = _expand_compact_iri(stripped, prefixes)
    if expanded in {f"{base}/{term}" for base in SCHEMA_ORG_BASES}:
        return True
    return vocab_is_schema and stripped == term


def _schema_context_state(
    context: object,
    inherited: SchemaContextState,
) -> SchemaContextState:
    """Track Schema vocabulary, term mappings, prefixes, unsupported contexts, and protection."""
    if context is None:
        return DEFAULT_SCHEMA_CONTEXT_STATE

    (
        vocab_is_schema,
        inherited_overrides,
        inherited_prefixes,
        unsupported,
        inherited_protected,
    ) = inherited
    term_overrides = dict(inherited_overrides)
    prefixes = dict(inherited_prefixes)
    protected_terms = set(inherited_protected)

    if isinstance(context, str):
        is_schema = _normalized_schema_url(context) in SCHEMA_ORG_REMOTE_CONTEXTS
        if is_schema:
            return (
                True, term_overrides, prefixes, unsupported, frozenset(protected_terms)
            )
        return (
            vocab_is_schema, term_overrides, prefixes, True, frozenset(protected_terms)
        )

    if isinstance(context, dict):
        # Resolving arbitrary imported contexts would require network dereference.
        # This verifier is deterministic/offline, so imported contexts fail closed.
        if "@import" in context:
            return (
                vocab_is_schema, term_overrides, prefixes, True, frozenset(protected_terms)
            )

        if "@vocab" in context:
            raw_vocab = context.get("@vocab")
            expanded_vocab = (
                _expand_compact_iri(raw_vocab, prefixes)
                if isinstance(raw_vocab, str)
                else None
            )
            vocab_is_schema = expanded_vocab in SCHEMA_ORG_VOCAB_BASES

        definitions = [
            (term, definition)
            for term, definition in context.items()
            if not term.startswith("@")
        ]

        # JSON-LD rejects a later redefinition of a protected term. This verifier
        # intentionally fails closed for any redefinition of a protected scholarly
        # term rather than attempting to recover from an invalid active context.
        context_protected = context.get("@protected") is True
        for term, definition in definitions:
            if term in SCHOLARLY_SCHEMA_TERMS and term in protected_terms:
                unsupported = True
            if (
                term in SCHOLARLY_SCHEMA_TERMS
                and (
                    context_protected
                    or (
                        isinstance(definition, dict)
                        and definition.get("@protected") is True
                    )
                )
            ):
                protected_terms.add(term)

        # Context definitions may use compact IRIs in later term mappings. Build
        # direct prefix definitions first, iterating so same-context prefixes can
        # depend on an earlier resolved prefix. Redefinition removes stale prefixes.
        for term, _ in definitions:
            prefixes.pop(term, None)
        for _ in range(max(1, len(definitions))):
            changed = False
            for term, definition in definitions:
                mapping = _prefix_mapping(definition, prefixes)
                if mapping is not None and prefixes.get(term) != mapping:
                    prefixes[term] = mapping
                    changed = True
            if not changed:
                break

        for term in SCHOLARLY_SCHEMA_TERMS:
            if term in context:
                term_overrides[term] = _term_maps_to_schema_term(
                    context.get(term), term, vocab_is_schema, prefixes
                )
        return (
            vocab_is_schema,
            term_overrides,
            prefixes,
            unsupported,
            frozenset(protected_terms),
        )

    if isinstance(context, list):
        state = inherited
        for item in context:
            state = _schema_context_state(item, state)
        return state

    return (
        vocab_is_schema, term_overrides, prefixes, True, frozenset(protected_terms)
    )


def _context_propagates(context: object) -> bool:
    """Return whether a local JSON-LD context applies to descendant node objects."""
    if isinstance(context, dict):
        return context.get("@propagate") is not False
    if isinstance(context, list):
        propagate = True
        for item in context:
            if isinstance(item, dict) and "@propagate" in item:
                propagate = item.get("@propagate") is not False
        return propagate
    return True


def _type_context_propagates(context: object) -> bool:
    """Type-scoped contexts stop at the next node unless explicitly propagated."""
    if isinstance(context, dict):
        return context.get("@propagate") is True
    if isinstance(context, list):
        propagate = False
        for item in context:
            if isinstance(item, dict) and "@propagate" in item:
                propagate = item.get("@propagate") is True
        return propagate
    return False


def _property_scoped_contexts(
    context: object,
    inherited: dict[str, object],
) -> dict[str, object]:
    """Track JSON-LD property-scoped contexts in the active local context."""
    if context is None:
        return {}
    if isinstance(context, str):
        return dict(inherited)
    if isinstance(context, dict):
        scopes = dict(inherited)
        for term, definition in context.items():
            if term.startswith("@"):
                continue
            if isinstance(definition, dict) and "@context" in definition:
                scopes[term] = definition.get("@context")
            else:
                scopes.pop(term, None)
        return scopes
    if isinstance(context, list):
        scopes = dict(inherited)
        for item in context:
            scopes = _property_scoped_contexts(item, scopes)
        return scopes
    return {}


def _schema_term_is_valid(state: SchemaContextState, term: str) -> bool:
    vocab_is_schema, term_overrides, _prefixes, unsupported, _protected = state
    if unsupported:
        return False
    return term_overrides.get(term, vocab_is_schema)


def _schema_article_term_is_valid(state: SchemaContextState) -> bool:
    return _schema_term_is_valid(state, "ScholarlyArticle")


def _property_child_state(
    key: str,
    node_schema_state: SchemaContextState,
    child_schema_state: SchemaContextState,
    node_property_scopes: dict[str, object],
    child_property_scopes: dict[str, object],
) -> tuple[SchemaContextState, dict[str, object]]:
    """Return the active state for a property value before visiting it."""
    if key not in node_property_scopes:
        return child_schema_state, child_property_scopes
    scoped_context = node_property_scopes[key]
    if not _context_propagates(scoped_context):
        return DEFAULT_SCHEMA_CONTEXT_STATE, {}
    return (
        _schema_context_state(scoped_context, node_schema_state),
        _property_scoped_contexts(
            scoped_context, child_property_scopes
        ),
    )


def collect_scholarly_articles(
    value: object,
    articles: list[
        tuple[
            dict,
            SchemaContextState,
            SchemaContextState,
            SchemaContextState,
            dict[str, object],
            dict[str, object],
        ]
    ],
    inherited_schema_context: SchemaContextState = DEFAULT_SCHEMA_CONTEXT_STATE,
    inherited_property_scopes: dict[str, object] | None = None,
) -> None:
    property_scopes = (
        {} if inherited_property_scopes is None else dict(inherited_property_scopes)
    )
    if isinstance(value, dict):
        schema_state = inherited_schema_context
        child_schema_state = inherited_schema_context
        node_property_scopes = property_scopes
        child_property_scopes = property_scopes
        if "@context" in value:
            context = value.get("@context")
            schema_state = _schema_context_state(context, inherited_schema_context)
            node_property_scopes = _property_scoped_contexts(
                context, property_scopes
            )
            if _context_propagates(context):
                child_schema_state = schema_state
                child_property_scopes = node_property_scopes
            else:
                child_schema_state = inherited_schema_context
                child_property_scopes = property_scopes
        else:
            child_schema_state = schema_state

        article_type = value.get("@type")
        type_terms = (
            [article_type]
            if isinstance(article_type, str)
            else [term for term in article_type if isinstance(term, str)]
            if isinstance(article_type, list)
            else []
        )
        # The activating @type is expanded before any type-scoped context
        # defined by that term becomes active on the node properties.
        type_validation_state = schema_state
        for type_term in sorted(type_terms):
            if type_term not in node_property_scopes:
                continue
            type_context = node_property_scopes[type_term]
            schema_state = _schema_context_state(type_context, schema_state)
            node_property_scopes = _property_scoped_contexts(
                type_context, node_property_scopes
            )
            if _type_context_propagates(type_context):
                child_schema_state = schema_state
                child_property_scopes = node_property_scopes

        if article_type == "ScholarlyArticle" or (
            isinstance(article_type, list)
            and "ScholarlyArticle" in article_type
        ):
            articles.append(
                (
                    value,
                    type_validation_state,
                    schema_state,
                    child_schema_state,
                    node_property_scopes,
                    child_property_scopes,
                )
            )

        for key, child in value.items():
            if key == "@context":
                continue
            scoped_state, scoped_scopes = _property_child_state(
                key,
                schema_state,
                child_schema_state,
                node_property_scopes,
                child_property_scopes,
            )
            collect_scholarly_articles(
                child, articles, scoped_state, scoped_scopes
            )
    elif isinstance(value, list):
        for child in value:
            collect_scholarly_articles(
                child, articles, inherited_schema_context, property_scopes
            )


def check_scholarly_landing(page: str, errors: list[str]) -> None:
    parser = ScholarlyHTMLParser()
    try:
        parser.feed(page)
        parser.close()
    except Exception as exc:  # noqa: BLE001 - diagnostics should report malformed HTML
        errors.append(f"{SCHOLARLY_LANDING_PATH}: failed to parse rendered HTML: {exc}")
        return

    for parser_error in parser.errors:
        errors.append(f"{SCHOLARLY_LANDING_PATH}: {parser_error}")

    if not parser._head_seen:
        errors.append(f"{SCHOLARLY_LANDING_PATH}: document head was not found")

    for name, expected in SCHOLARLY_META_EXPECTED.items():
        observed = parser.meta.get(name, [])
        if observed != [expected]:
            errors.append(
                f"{SCHOLARLY_LANDING_PATH}: {name} expected exactly one value "
                f"{expected!r}, observed {observed!r}"
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

    articles: list[
        tuple[
            dict,
            SchemaContextState,
            SchemaContextState,
            SchemaContextState,
            dict[str, object],
            dict[str, object],
        ]
    ] = []
    for document in documents:
        collect_scholarly_articles(document, articles)

    matching = [
        (
            article,
            type_state,
            schema_state,
            child_schema_state,
            article_scopes,
            child_scopes,
        )
        for (
            article,
            type_state,
            schema_state,
            child_schema_state,
            article_scopes,
            child_scopes,
        ) in articles
        if article.get("name") == SCHOLARLY_TITLE
    ]
    if len(matching) != 1:
        observed_names = [article.get("name") for article, *_rest in articles]
        errors.append(
            f"{SCHOLARLY_LANDING_PATH}: expected exactly one rendered ScholarlyArticle "
            f"with the exact title; matching={len(matching)}, observed={observed_names!r}"
        )
        return

    (
        article,
        type_state,
        schema_state,
        child_schema_state,
        article_scopes,
        child_scopes,
    ) = matching[0]
    if not _schema_article_term_is_valid(type_state):
        errors.append(
            f"{SCHOLARLY_LANDING_PATH}: matching ScholarlyArticle lacks an applicable "
            "Schema.org JSON-LD context"
        )

    expected_fields = {
        "headline": SCHOLARLY_TITLE,
        "datePublished": "2026-07-29",
        "version": "1.1",
        "url": SCHOLARLY_HTML_URL,
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "isAccessibleForFree": True,
    }
    required_schema_properties = {
        "name",
        *expected_fields.keys(),
        "encoding",
        "sameAs",
        "identifier",
    }
    for field in sorted(required_schema_properties):
        if not _schema_term_is_valid(schema_state, field):
            errors.append(
                f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.{field} is not mapped "
                f"to Schema.org/{field}"
            )

    for field, expected in expected_fields.items():
        if article.get(field) != expected:
            errors.append(
                f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.{field} expected "
                f"{expected!r}, observed {article.get(field)!r}"
            )

    encoding_state, encoding_scopes = _property_child_state(
        "encoding",
        schema_state,
        child_schema_state,
        article_scopes,
        child_scopes,
    )

    encoding = article.get("encoding")
    if not isinstance(encoding, dict):
        errors.append(f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.encoding is missing")
    else:
        if "@context" in encoding:
            encoding_context = encoding.get("@context")
            encoding_state = _schema_context_state(encoding_context, encoding_state)
            encoding_scopes = _property_scoped_contexts(
                encoding_context, encoding_scopes
            )
        encoding_type = encoding.get("@type")
        encoding_type_terms = (
            [encoding_type]
            if isinstance(encoding_type, str)
            else [term for term in encoding_type if isinstance(term, str)]
            if isinstance(encoding_type, list)
            else []
        )
        for type_term in sorted(encoding_type_terms):
            if type_term not in encoding_scopes:
                continue
            type_context = encoding_scopes[type_term]
            encoding_state = _schema_context_state(type_context, encoding_state)
            encoding_scopes = _property_scoped_contexts(
                type_context, encoding_scopes
            )
        for field in ("contentUrl", "encodingFormat"):
            if not _schema_term_is_valid(encoding_state, field):
                errors.append(
                    f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.encoding.{field} "
                    f"is not mapped to Schema.org/{field}"
                )
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

    identifier_state, identifier_scopes = _property_child_state(
        "identifier",
        schema_state,
        child_schema_state,
        article_scopes,
        child_scopes,
    )

    identifiers = article.get("identifier", [])
    if isinstance(identifiers, dict):
        identifiers = [identifiers]
    property_values: set[tuple[object, object]] = set()
    if isinstance(identifiers, list):
        for identifier in identifiers:
            if isinstance(identifier, dict):
                item_state = identifier_state
                item_scopes = identifier_scopes
                if "@context" in identifier:
                    identifier_context = identifier.get("@context")
                    item_state = _schema_context_state(identifier_context, item_state)
                    item_scopes = _property_scoped_contexts(
                        identifier_context, item_scopes
                    )
                identifier_type = identifier.get("@type")
                identifier_type_terms = (
                    [identifier_type]
                    if isinstance(identifier_type, str)
                    else [
                        term for term in identifier_type if isinstance(term, str)
                    ]
                    if isinstance(identifier_type, list)
                    else []
                )
                for type_term in sorted(identifier_type_terms):
                    if type_term not in item_scopes:
                        continue
                    type_context = item_scopes[type_term]
                    item_state = _schema_context_state(type_context, item_state)
                    item_scopes = _property_scoped_contexts(
                        type_context, item_scopes
                    )
                for field in ("propertyID", "value"):
                    if not _schema_term_is_valid(item_state, field):
                        errors.append(
                            f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.identifier.{field} "
                            f"is not mapped to Schema.org/{field}"
                        )
                property_values.add(
                    (identifier.get("propertyID"), identifier.get("value"))
                )

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


def check_static_page(path: str, page: str, errors: list[str]) -> None:
    """Apply the one shared rendered-page contract used by legacy and v2 checks."""
    before = len(errors)
    markers = STATIC_PAGE_MARKERS.get(path, [])
    for marker in markers:
        if marker not in page:
            errors.append(f"{path}: missing current static marker {marker!r}")

    if path == SCHOLARLY_LANDING_PATH:
        check_scholarly_landing(page, errors)

    if len(errors) == before:
        if path == SCHOLARLY_LANDING_PATH:
            print(f"{path}: exact scholarly head metadata and JSON-LD values verified")
        else:
            print(f"{path}: current static markers present")


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

    for path in STATIC_PAGE_MARKERS:
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

        check_static_page(path, page, errors)

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