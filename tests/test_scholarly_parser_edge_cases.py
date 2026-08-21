from __future__ import annotations

import html
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_deployment_freshness as deployment  # noqa: E402


def _valid_article(**overrides: object) -> dict[str, object]:
    article: dict[str, object] = {
        "@type": "ScholarlyArticle",
        "name": deployment.SCHOLARLY_TITLE,
        "headline": deployment.SCHOLARLY_TITLE,
        "datePublished": "2026-07-29",
        "version": "1.1",
        "identifier": [
            {
                "@type": "PropertyValue",
                "propertyID": "Technical report number",
                "value": deployment.SCHOLARLY_REPORT_NUMBER,
            },
            {
                "@type": "PropertyValue",
                "propertyID": "DOI",
                "value": deployment.SCHOLARLY_DOI,
                "url": deployment.SCHOLARLY_DOI_URL,
            },
        ],
        "url": deployment.SCHOLARLY_HTML_URL,
        "sameAs": [deployment.SCHOLARLY_DOI_URL, deployment.SCHOLARLY_ZENODO_URL],
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "encoding": {
            "@type": "MediaObject",
            "contentUrl": deployment.SCHOLARLY_PDF_URL,
            "encodingFormat": "application/pdf",
        },
    }
    article.update(overrides)
    return article


def _landing(document: object) -> str:
    meta = "".join(
        f'<meta name="{html.escape(name, quote=True)}" '
        f'content="{html.escape(value, quote=True)}">'
        for name, value in deployment.SCHOLARLY_META_EXPECTED.items()
    )
    json_ld = json.dumps(document)
    return (
        "<!doctype html><html><head>"
        + meta
        + f'<script type="application/ld+json">{json_ld}</script>'
        + "</head><body></body></html>"
    )


def test_non_head_start_tag_implicitly_ends_head_without_body_tag() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>"
        '<meta name="citation_title" content="before-main">'
        "<main>"
        '<meta name="citation_author" content="after-main">'
        "</main></html>"
    )
    parser.close()

    assert parser.meta.get("citation_title") == ["before-main"]
    assert "citation_author" not in parser.meta
    assert parser._body_started is True
    assert parser._in_head is False


def test_duplicate_meta_attributes_use_first_values_and_fail_closed() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>"
        '<meta name="citation_title" name="citation_author" '
        'content="first-content" content="second-content">'
        "</head><body></body></html>"
    )
    parser.close()

    assert parser.meta.get("citation_title") == ["first-content"]
    assert "citation_author" not in parser.meta
    assert parser.errors == [
        "scholarly meta contains duplicate attribute(s): content, name"
    ]


def test_duplicate_script_type_keeps_first_jsonld_value_and_fails_closed() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>"
        '<script type="application/ld+json" type="text/plain">'
        '{"@context":"https://schema.org"}'
        "</script></head><body></body></html>"
    )
    parser.close()

    assert len(parser.json_ld_blocks) == 1
    assert parser.errors == [
        "scholarly JSON-LD script contains duplicate type attribute"
    ]


def test_duplicate_script_type_does_not_promote_ignored_second_jsonld_value() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>"
        '<script type="text/plain" type="application/ld+json">'
        '{"@context":"https://schema.org"}'
        "</script></head><body></body></html>"
    )
    parser.close()

    assert parser.json_ld_blocks == []
    assert parser.errors == [
        "scholarly JSON-LD script contains duplicate type attribute"
    ]


def test_template_contents_are_inert_for_scholarly_metadata() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>"
        "<template>"
        '<meta name="citation_title" content="template-title">'
        '<script type="application/ld+json">{not-json}</script>'
        "</template>"
        '<meta name="citation_title" content="real-title">'
        '<script type="application/ld+json">{"real":true}</script>'
        "</head><body></body></html>"
    )
    parser.close()

    assert parser.meta.get("citation_title") == ["real-title"]
    assert parser.json_ld_blocks == ['{"real":true}']
    assert parser.errors == []


def test_scholarly_article_inherits_root_schema_org_context() -> None:
    page = _landing(
        {"@context": "https://schema.org", "@graph": [_valid_article()]}
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert errors == []


def test_scholarly_article_without_schema_org_context_is_rejected() -> None:
    page = _landing({"@graph": [_valid_article()]})
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_scholarly_article_with_non_schema_context_is_rejected() -> None:
    page = _landing(
        {"@context": "https://example.invalid/schema", "@graph": [_valid_article()]}
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_child_context_can_reset_inherited_schema_org_context() -> None:
    article = _valid_article(**{"@context": None})
    page = _landing({"@context": "https://schema.org", "@graph": [article]})
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )
