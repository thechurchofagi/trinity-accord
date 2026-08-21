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


def test_non_whitespace_character_token_implicitly_ends_head() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head>body-effective text"
        '<meta name="citation_title" content="after-text">'
        "</html>"
    )
    parser.close()

    assert "citation_title" not in parser.meta
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


def test_self_closing_template_slash_does_not_end_html_template() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head><template/>"
        '<meta name="citation_title" content="still-template">'
        '<script type="application/ld+json">{"still":"template"}</script>'
        "</head><body></body></html>"
    )
    parser.close()

    assert "citation_title" not in parser.meta
    assert parser.json_ld_blocks == []
    assert parser._template_depth == 1


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


def test_explicit_scholarly_article_term_override_is_honored() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://schema.org/",
                "ScholarlyArticle": "https://example.invalid/Fake",
            },
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_explicit_schema_org_scholarly_article_term_is_accepted() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://schema.org/",
                "ScholarlyArticle": "https://schema.org/ScholarlyArticle",
            },
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert errors == []


def test_propagate_false_does_not_apply_context_to_graph_descendants() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://schema.org/",
                "@propagate": False,
            },
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )

def test_noscript_raw_text_does_not_close_template() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head><template><noscript></template></noscript>"
        '<meta name="citation_title" content="still-template">'
        '<script type="application/ld+json">{"still":"template"}</script>'
        "</head><body></body></html>"
    )
    parser.close()

    assert "citation_title" not in parser.meta
    assert parser.json_ld_blocks == []
    assert parser._template_depth == 1


def test_schema_org_vocab_requires_trailing_slash() -> None:
    page = _landing(
        {"@context": {"@vocab": "https://schema.org"}, "@graph": [_valid_article()]}
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_property_scoped_context_override_is_applied_before_child_nodes() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://schema.org/",
                "items": {
                    "@id": "https://example.invalid/items",
                    "@context": {
                        "ScholarlyArticle": "https://example.invalid/Fake"
                    },
                },
            },
            "items": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )

def test_special_end_tags_implicitly_end_head() -> None:
    for tag in ("html", "br"):
        parser = deployment.ScholarlyHTMLParser()
        parser.feed(
            "<!doctype html><html><head>"
            f"</{tag}>"
            '<meta name="citation_title" content="body-effective">'
        )
        parser.close()

        assert "citation_title" not in parser.meta
        assert parser._body_started is True
        assert parser._in_head is False


def test_explicit_schema_article_iri_with_trailing_slash_is_rejected() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://example.invalid/",
                "ScholarlyArticle": "https://schema.org/ScholarlyArticle/",
            },
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_later_vocab_overrides_remote_schema_context() -> None:
    page = _landing(
        {
            "@context": [
                "https://schema.org",
                {"@vocab": "https://example.invalid/"},
            ],
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )

def test_type_scoped_context_applies_before_descendant_traversal() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://schema.org/",
                "Outer": {
                    "@id": "https://example.invalid/Outer",
                    "@context": {
                        "@propagate": True,
                        "ScholarlyArticle": "https://example.invalid/Fake",
                    },
                },
            },
            "@type": "Outer",
            "items": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_imported_context_fails_closed() -> None:
    page = _landing(
        {
            "@context": {
                "@import": "https://example.invalid/context.jsonld",
                "@vocab": "https://schema.org/",
            },
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error for error in errors
    )


def test_compact_iri_article_mapping_is_accepted() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://schema.org/",
                "schema": "https://schema.org/",
                "ScholarlyArticle": "schema:ScholarlyArticle",
            },
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert errors == []


def test_self_closing_template_in_svg_does_not_open_html_template() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head></head><body>"
        "<svg><template/></svg>"
        '<script type="application/ld+json">{"ok":true}</script>'
        "</body></html>"
    )
    parser.close()

    assert parser._foreign_content_depth == 0
    assert parser._template_depth == 0
    assert parser.json_ld_blocks == ['{"ok":true}']


def test_required_schema_property_remap_is_rejected() -> None:
    page = _landing(
        {
            "@context": {
                "@vocab": "https://schema.org/",
                "name": "https://example.invalid/not-name",
            },
            "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "ScholarlyArticle.name is not mapped to Schema.org/name" in error
        for error in errors
    )

def test_foreign_template_end_does_not_close_outer_html_template() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head><template>"
        "<svg><template/></svg>"
        '<meta name="citation_title" content="still-inert">'
        '<script type="application/ld+json">{"still":"inert"}</script>'
        "</template></head><body></body></html>"
    )
    parser.close()

    assert "citation_title" not in parser.meta
    assert parser.json_ld_blocks == []
    assert parser._template_depth == 0
    assert parser._foreign_content_depth == 0


def test_non_propagating_article_context_does_not_leak_to_nested_nodes() -> None:
    article = _valid_article(
        **{
  "@context": {
      "@vocab": "https://schema.org/",
      "@propagate": False,
  }
        }
    )
    page = _landing({"@graph": [article]})
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "ScholarlyArticle.encoding.contentUrl is not mapped"
        in error
        for error in errors
    )
    assert any(
        "ScholarlyArticle.identifier.propertyID is not mapped"
        in error
        for error in errors
    )


def test_jsonld_script_inside_svg_foreignobject_is_html_content() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head></head><body>"
        "<svg><foreignObject>"
        '<script type="application/ld+json">{"ok":true}</script>'
        "</foreignObject></svg>"
        "</body></html>"
    )
    parser.close()

    assert parser.json_ld_blocks == ['{"ok":true}']
    assert parser._foreign_content_depth == 0


def test_explicit_prefix_false_disables_compact_iri_prefix() -> None:
    page = _landing(
        {
  "@context": {
      "@vocab": "https://schema.org/",
      "schema": {
          "@id": "https://schema.org/",
          "@prefix": False,
      },
      "ScholarlyArticle": "schema:ScholarlyArticle",
  },
  "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error
        for error in errors
    )


def test_type_scoped_context_does_not_rewrite_activating_type() -> None:
    page = _landing(
        {
  "@context": {
      "@vocab": "https://schema.org/",
      "ScholarlyArticle": {
          "@id": "https://example.invalid/Fake",
          "@context": {
              "ScholarlyArticle": (
                  "https://schema.org/ScholarlyArticle"
              )
          },
      },
  },
  "@graph": [_valid_article()],
        }
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)

    assert any(
        "lacks an applicable Schema.org JSON-LD context" in error
        for error in errors
    )


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


def test_non_html_whitespace_character_token_implicitly_ends_head() -> None:
    for text in ("\u00a0", "\v"):
        parser = deployment.ScholarlyHTMLParser()
        parser.feed(
  "<!doctype html><html><head>"
  + text
  + '<meta name="citation_title" content="after-non-html-space">'
  + "</html>"
        )
        parser.close()

        assert "citation_title" not in parser.meta
        assert parser._body_started is True
        assert parser._in_head is False


def test_after_head_meta_is_processed_as_head_metadata() -> None:
    parser = deployment.ScholarlyHTMLParser()
    parser.feed(
        "<!doctype html><html><head></head>"
        '<meta name="citation_title" content="after-head">'
        "<body></body></html>"
    )
    parser.close()

    assert parser.meta.get("citation_title") == ["after-head"]
    assert parser.errors == []


def test_identifier_type_scoped_context_is_applied_to_properties() -> None:
    page = _landing({
        "@context": {
  "@vocab": "https://schema.org/",
  "PropertyValue": {
      "@id": "https://schema.org/PropertyValue",
      "@context": {
          "propertyID": "https://example.invalid/not-property-id"
      },
  },
        },
        "@graph": [_valid_article()],
    })
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert any(
        "ScholarlyArticle.identifier.propertyID is not mapped" in error
        for error in errors
    )


def test_protected_schema_term_redefinition_fails_closed() -> None:
    page = _landing({
        "@context": [
  {
      "@vocab": "https://schema.org/",
      "name": {
          "@id": "https://example.invalid/not-name",
          "@protected": True,
      },
  },
  {"name": "https://schema.org/name"},
        ],
        "@graph": [_valid_article()],
    })
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert errors


def test_explicit_schema_term_mapping_with_surrounding_whitespace_fails_closed() -> None:
    page = _landing({
        "@context": {
  "@vocab": "https://schema.org/",
  "name": " https://schema.org/name ",
        },
        "@graph": [_valid_article()],
    })
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert any(
        "ScholarlyArticle.name is not mapped to Schema.org/name" in error
        for error in errors
    )


def test_unencoded_annotation_xml_svg_foreignobject_exposes_html_jsonld() -> None:
    meta = "".join(
        f'<meta name="{html.escape(name, quote=True)}" '
        f'content="{html.escape(value, quote=True)}">'
        for name, value in deployment.SCHOLARLY_META_EXPECTED.items()
    )
    document = {
        "@context": "https://schema.org",
        "@graph": [_valid_article()],
    }
    json_ld = json.dumps(document)
    page = (
        "<!doctype html><html><head>" + meta + "</head><body>"
        "<math><annotation-xml><svg><foreignObject>"
        f'<script type="application/ld+json">{json_ld}</script>'
        "</foreignObject></svg></annotation-xml></math>"
        "</body></html>"
    )
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert errors == []


def test_identical_protected_schema_term_redefinition_is_allowed() -> None:
    protected_name = {
        "@id": "https://schema.org/name",
        "@protected": True,
    }
    page = _landing({
        "@context": [
  {"@vocab": "https://schema.org/", "name": protected_name},
  {"name": protected_name},
        ],
        "@graph": [_valid_article()],
    })
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert errors == []


def test_schema_term_mapping_can_resolve_through_term_alias() -> None:
    page = _landing({
        "@context": {
  "@vocab": "https://schema.org/",
  "schemaName": "https://schema.org/name",
  "name": "schemaName",
        },
        "@graph": [_valid_article()],
    })
    errors: list[str] = []
    deployment.check_scholarly_landing(page, errors)
    assert errors == []
