from pathlib import Path

source_path = Path("scripts/check_deployment_freshness.py")
tests_path = Path("tests/test_scholarly_parser_edge_cases.py")
source = source_path.read_text(encoding="utf-8")
tests = tests_path.read_text(encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


source = replace_once(
    source,
    'SCHEMA_ORG_BASES = {"http://schema.org", "https://schema.org"}\nSCHEMA_ORG_VOCAB_BASES = {"http://schema.org/", "https://schema.org/"}\nSCHEMA_ORG_ARTICLE_IRIS = {\n',
    'SCHEMA_ORG_BASES = {"http://schema.org", "https://schema.org"}\nSCHEMA_ORG_VOCAB_BASES = {"http://schema.org/", "https://schema.org/"}\nSCHEMA_ORG_REMOTE_CONTEXTS = SCHEMA_ORG_BASES | SCHEMA_ORG_VOCAB_BASES\nSCHEMA_ORG_ARTICLE_IRIS = {\n',
    "schema remote context constants",
)

source = replace_once(
    source,
    '    _SVG_HTML_INTEGRATION_POINTS = {"foreignobject", "desc", "title"}\n    _MATHML_TEXT_INTEGRATION_POINTS = {"mi", "mo", "mn", "ms", "mtext"}\n    _MATHML_HTML_ENCODINGS = {"text/html", "application/xhtml+xml"}\n',
    '    _SVG_HTML_INTEGRATION_POINTS = {"foreignobject", "desc", "title"}\n    _MATHML_TEXT_INTEGRATION_POINTS = {"mi", "mo", "mn", "ms", "mtext"}\n    _MATHML_HTML_ENCODINGS = {"text/html", "application/xhtml+xml"}\n    _FOREIGN_HTML_BREAKOUT_TAGS = {\n        "b", "big", "blockquote", "body", "br", "center", "code",\n        "dd", "div", "dl", "dt", "em", "embed", "h1", "h2",\n        "h3", "h4", "h5", "h6", "head", "hr", "i", "img",\n        "li", "listing", "menu", "meta", "nobr", "ol", "p",\n        "pre", "ruby", "s", "small", "span", "strong", "strike",\n        "sub", "sup", "table", "tt", "u", "ul", "var",\n    }\n',
    "foreign breakout tag set",
)

source = replace_once(
    source,
    '        return "html"\n\n    def _push_element(\n',
    '        return "html"\n\n    @classmethod\n    def _is_foreign_html_breakout(\n        cls, tag: str, attributes: dict[str, str | None]\n    ) -> bool:\n        if tag in cls._FOREIGN_HTML_BREAKOUT_TAGS:\n            return True\n        return tag == "font" and any(\n            name in attributes for name in {"color", "face", "size"}\n        )\n\n    def _pop_open_foreign_content(self) -> None:\n        while self._element_stack and self._element_stack[-1][1] != "html":\n            _tag, namespace, _attributes = self._element_stack.pop()\n            if namespace != "html":\n                self._foreign_content_depth = max(\n                    0, self._foreign_content_depth - 1\n                )\n\n    def _push_element(\n',
    "foreign breakout helpers",
)

source = replace_once(
    source,
    '        attributes, duplicates, values = _first_attributes(attrs)\n        namespace = self._namespace_for_start(tag, attributes)\n\n        # A non-head HTML start tag implicitly ends the optional document\n',
    '        attributes, duplicates, values = _first_attributes(attrs)\n        namespace = self._namespace_for_start(tag, attributes)\n        if (\n            namespace != "html"\n            and self._is_foreign_html_breakout(tag, attributes)\n        ):\n            self._pop_open_foreign_content()\n            namespace = self._namespace_for_start(tag, attributes)\n\n        # A non-head HTML start tag implicitly ends the optional document\n',
    "foreign breakout start handling",
)

source = replace_once(
    source,
    'def _normalized_schema_url(value: object) -> str | None:\n    if not isinstance(value, str):\n        return None\n    return value.strip().rstrip("/")\n',
    'def _normalized_schema_url(value: object) -> str | None:\n    if not isinstance(value, str):\n        return None\n    return value\n',
    "exact remote context URL",
)

source = replace_once(
    source,
    'def _expand_compact_iri(value: str, prefixes: dict[str, str]) -> str:\n    stripped = value.strip()\n    if ":" not in stripped:\n        return stripped\n    prefix, suffix = stripped.split(":", 1)\n    base = prefixes.get(prefix)\n    if base is None:\n        return stripped\n    return base + suffix\n',
    'def _expand_compact_iri(value: str, prefixes: dict[str, str]) -> str:\n    if value != value.strip():\n        return value\n    stripped = value\n    if ":" not in stripped:\n        return stripped\n    prefix, suffix = stripped.split(":", 1)\n    if suffix.startswith("//"):\n        return stripped\n    base = prefixes.get(prefix)\n    if base is None:\n        return stripped\n    return base + suffix\n',
    "absolute compact IRI handling",
)

source = replace_once(
    source,
    '    if isinstance(value, dict):\n        if "@id" not in value:\n            return vocab_is_schema\n        value = value.get("@id")\n',
    '    if isinstance(value, dict):\n        if "@reverse" in value:\n            return False\n        if "@id" not in value:\n            return vocab_is_schema\n        value = value.get("@id")\n',
    "reverse property mapping",
)

source = replace_once(
    source,
    '    if isinstance(context, str):\n        is_schema = _normalized_schema_url(context) in SCHEMA_ORG_BASES\n        if is_schema:\n            # Treat the known Schema.org remote context as the vocabulary source.\n            # It replaces earlier relevant term overrides, but remains overridable\n            # by a later local @vocab in a context list.\n            for term in SCHOLARLY_SCHEMA_TERMS:\n                term_overrides.pop(term, None)\n            return (True, term_overrides, prefixes, unsupported)\n        return (vocab_is_schema, term_overrides, prefixes, True)\n',
    '    if isinstance(context, str):\n        is_schema = _normalized_schema_url(context) in SCHEMA_ORG_REMOTE_CONTEXTS\n        if is_schema:\n            return (True, term_overrides, prefixes, unsupported)\n        return (vocab_is_schema, term_overrides, prefixes, True)\n',
    "remote schema context state",
)

source = replace_once(
    source,
    '        if "@vocab" in context:\n            raw_vocab = context.get("@vocab")\n            vocab_is_schema = (\n                isinstance(raw_vocab, str)\n                and raw_vocab.strip() in SCHEMA_ORG_VOCAB_BASES\n            )\n',
    '        if "@vocab" in context:\n            raw_vocab = context.get("@vocab")\n            expanded_vocab = (\n                _expand_compact_iri(raw_vocab, prefixes)\n                if isinstance(raw_vocab, str)\n                else None\n            )\n            vocab_is_schema = expanded_vocab in SCHEMA_ORG_VOCAB_BASES\n',
    "compact @vocab expansion",
)

source = replace_once(
    source,
    '    encoding_state, _encoding_scopes = _property_child_state(\n        "encoding",\n        schema_state,\n        child_schema_state,\n        article_scopes,\n        child_scopes,\n    )\n\n    encoding = article.get("encoding")\n    if not isinstance(encoding, dict):\n        errors.append(f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.encoding is missing")\n    else:\n        if "@context" in encoding:\n            encoding_state = _schema_context_state(\n                encoding.get("@context"), encoding_state\n            )\n        for field in ("contentUrl", "encodingFormat"):\n',
    '    encoding_state, encoding_scopes = _property_child_state(\n        "encoding",\n        schema_state,\n        child_schema_state,\n        article_scopes,\n        child_scopes,\n    )\n\n    encoding = article.get("encoding")\n    if not isinstance(encoding, dict):\n        errors.append(f"{SCHOLARLY_LANDING_PATH}: ScholarlyArticle.encoding is missing")\n    else:\n        if "@context" in encoding:\n            encoding_context = encoding.get("@context")\n            encoding_state = _schema_context_state(encoding_context, encoding_state)\n            encoding_scopes = _property_scoped_contexts(\n                encoding_context, encoding_scopes\n            )\n        encoding_type = encoding.get("@type")\n        encoding_type_terms = (\n            [encoding_type]\n            if isinstance(encoding_type, str)\n            else [term for term in encoding_type if isinstance(term, str)]\n            if isinstance(encoding_type, list)\n            else []\n        )\n        for type_term in sorted(encoding_type_terms):\n            if type_term not in encoding_scopes:\n                continue\n            type_context = encoding_scopes[type_term]\n            encoding_state = _schema_context_state(type_context, encoding_state)\n            encoding_scopes = _property_scoped_contexts(\n                type_context, encoding_scopes\n            )\n        for field in ("contentUrl", "encodingFormat"):\n',
    "encoding type scoped context",
)

additions = r'''


def test_html_breakout_tag_exits_svg_for_jsonld_script() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head></head><body><svg><p>"
        '<script type="application/ld+json">{"ok":true}</script>'
        "</p></svg></body></html>"
    )
    parser.close()
    assert parser.json_ld_blocks == ['{"ok":true}']
    assert parser._foreign_content_depth == 0


def test_reverse_definition_for_required_schema_term_is_rejected() -> None:
    page = _landing({
        "@context": {
            "@vocab": "https://schema.org/",
            "name": {"@reverse": "https://example.invalid/not-name"},
        },
        "@graph": [_valid_article()],
    })
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert any("ScholarlyArticle.name is not mapped to Schema.org/name" in e for e in errors)


def test_encoding_type_scoped_context_is_applied_to_properties() -> None:
    page = _landing({
        "@context": {
            "@vocab": "https://schema.org/",
            "MediaObject": {
                "@id": "https://schema.org/MediaObject",
                "@context": {"contentUrl": "https://example.invalid/not-content-url"},
            },
        },
        "@graph": [_valid_article()],
    })
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert any("ScholarlyArticle.encoding.contentUrl is not mapped" in e for e in errors)


def test_remote_schema_context_urls_are_matched_exactly() -> None:
    for context in (" https://schema.org ", "https://schema.org////"):
        page = _landing({"@context": context, "@graph": [_valid_article()]})
        errors: list[str] = []
        deployment.check_scholarly_landing(page, errors)
        assert any("lacks an applicable Schema.org JSON-LD context" in e for e in errors)


def test_compact_iri_vocab_is_expanded_from_prior_prefix() -> None:
    page = _landing({
        "@context": [
            {"schema": {"@id": "https://schema.org/", "@prefix": True}},
            {"@vocab": "schema:"},
        ],
        "@graph": [_valid_article()],
    })
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert errors == []


def test_remote_schema_context_preserves_prior_term_override() -> None:
    page = _landing({
        "@context": [
            {"name": "https://example.invalid/not-name"},
            "https://schema.org",
        ],
        "@graph": [_valid_article()],
    })
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert any("ScholarlyArticle.name is not mapped to Schema.org/name" in e for e in errors)


def test_absolute_schema_iri_is_not_rewritten_by_https_prefix() -> None:
    page = _landing({
        "@context": {
            "@vocab": "https://schema.org/",
            "https": "https://example.invalid/",
            "name": "https://schema.org/name",
        },
        "@graph": [_valid_article()],
    })
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert errors == []
'''

if "def test_html_breakout_tag_exits_svg_for_jsonld_script()" in tests:
    raise SystemExit("seventh-round tests already present unexpectedly")
tests = tests.rstrip() + additions + "\n"

source_path.write_text(source, encoding="utf-8")
tests_path.write_text(tests, encoding="utf-8")
