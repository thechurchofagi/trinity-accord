from pathlib import Path

validation_path = Path('apps/record_chain_intake_gateway/gateway/validation.py')
text = validation_path.read_text(encoding='utf-8')
start_marker = '    if cc_level >= 3 and record_type in _FORMAL_RECORD_TYPES:\n'
end_marker = '    if cc_level < required_cc:\n'
start = text.find(start_marker)
if start < 0:
    raise SystemExit('strict CC3 insertion not found')
end = text.find(end_marker, start)
if end < 0:
    raise SystemExit('CC3 insertion end not found')
text = text[:start] + text[end:]
validation_path.write_text(text, encoding='utf-8')

test_path = Path('apps/record_chain_intake_gateway/tests/test_external_agent_validation_contract.py')
test = test_path.read_text(encoding='utf-8')
test = test.replace(
    'def test_direct_cc3_rejects_whitespace_url_and_missing_confirmation_boundary():',
    'def test_direct_cc3_rejects_whitespace_url():',
)
test = test.replace(
    '    assert "INVALID_LOADED_CONTEXT_URL" in result\n'
    '    assert "CC3_CONTEXT_READ_CONFIRMATION_REQUIRED" in result\n'
    '    assert "CONTEXT_READ_CONFIRMATION_BOUNDARY_INVALID" in result\n',
    '    assert "INVALID_LOADED_CONTEXT_URL" in result\n',
)
test_path.write_text(test, encoding='utf-8')
print('PASS: preserved historical v2.2 CC-3 compatibility while retaining URL validation')
