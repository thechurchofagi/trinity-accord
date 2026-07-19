#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"target block missing in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    ROOT / "scripts/public_machine_deployment_contract.py",
    '''def json_object_from_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} JSON root must be an object, got {type(value).__name__}")
    return value
''',
    '''def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def json_object_from_bytes(data: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_strict_json_object,
            parse_constant=_reject_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} is not strict UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} JSON root must be an object, got {type(value).__name__}")
    return value
''',
)

replace_once(
    ROOT / "tests/test_live_deployment_contract.py",
    '''def test_json_root_must_be_an_object() -> None:
    with pytest.raises(ValueError, match="JSON root must be an object"):
        contract.json_object_from_bytes(b"[]", "test surface")


def test_source_digest_is_bound_to_content() -> None:
''',
    '''def test_json_root_must_be_an_object() -> None:
    with pytest.raises(ValueError, match="JSON root must be an object"):
        contract.json_object_from_bytes(b"[]", "test surface")


@pytest.mark.parametrize(
    "raw",
    [b'{"x": 1, "x": 2}', b'{"x": NaN}', b'{"x": Infinity}'],
)
def test_public_machine_json_must_be_strict(raw: bytes) -> None:
    with pytest.raises(ValueError, match="strict UTF-8 JSON"):
        contract.json_object_from_bytes(raw, "test surface")


def test_source_digest_is_bound_to_content() -> None:
''',
)

print("ROUND5_STRICT_PUBLIC_JSON_APPLIED")
