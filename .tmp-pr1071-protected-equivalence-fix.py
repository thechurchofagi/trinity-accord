from pathlib import Path

source_path = Path('scripts/check_deployment_freshness.py')
tests_path = Path('tests/test_scholarly_parser_edge_cases.py')
source = source_path.read_text(encoding='utf-8')
tests = tests_path.read_text(encoding='utf-8')

old = '''def _protected_term_signature(definition: object, protected: bool) -> str:\n    canonical = definition\n    if isinstance(definition, dict):\n        canonical = dict(definition)\n        canonical.pop("@protected", None)\n    return json.dumps(\n        {"protected": protected, "definition": canonical},\n        ensure_ascii=False,\n        sort_keys=True,\n        separators=(",", ":"),\n    )\n'''
new = '''def _protected_term_signature(definition: object) -> str:\n    # JSON-LD compares protected term definitions modulo the @protected flag.\n    # Normalize simple string definitions to their expanded {"@id": ...} shape\n    # so syntactically different but identical definitions are not rejected.\n    if isinstance(definition, str):\n        canonical: object = {"@id": definition}\n    elif isinstance(definition, dict):\n        canonical = dict(definition)\n        canonical.pop("@protected", None)\n    else:\n        canonical = definition\n    return json.dumps(\n        canonical,\n        ensure_ascii=False,\n        sort_keys=True,\n        separators=(",", ":"),\n    )\n'''
if source.count(old) != 1:
    raise SystemExit(f'protected signature helper: expected one match, got {source.count(old)}')
source = source.replace(old, new, 1)

old_call = '            signature = _protected_term_signature(definition, definition_protected)\n'
new_call = '            signature = _protected_term_signature(definition)\n'
if source.count(old_call) != 1:
    raise SystemExit(f'protected signature call: expected one match, got {source.count(old_call)}')
source = source.replace(old_call, new_call, 1)

old_test = '''def test_identical_protected_schema_term_redefinition_is_allowed() -> None:\n    protected_name = {\n        "@id": "https://schema.org/name",\n        "@protected": True,\n    }\n    page = _landing({\n        "@context": [\n  {"@vocab": "https://schema.org/", "name": protected_name},\n  {"name": protected_name},\n        ],\n        "@graph": [_valid_article()],\n    })\n    errors: list[str] = []\n    deployment.check_scholarly_landing(page, errors)\n    assert errors == []\n'''
new_test = '''def test_identical_protected_schema_term_redefinition_is_allowed() -> None:\n    protected_name = {\n        "@id": "https://schema.org/name",\n        "@protected": True,\n    }\n    page = _landing({\n        "@context": [\n  {"@vocab": "https://schema.org/", "name": protected_name},\n  {"name": "https://schema.org/name"},\n        ],\n        "@graph": [_valid_article()],\n    })\n    errors: list[str] = []\n    deployment.check_scholarly_landing(page, errors)\n    assert errors == []\n'''
if tests.count(old_test) != 1:
    raise SystemExit(f'protected regression: expected one match, got {tests.count(old_test)}')
tests = tests.replace(old_test, new_test, 1)

source_path.write_text(source, encoding='utf-8')
tests_path.write_text(tests, encoding='utf-8')
