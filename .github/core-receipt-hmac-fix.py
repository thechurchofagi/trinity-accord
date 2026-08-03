from pathlib import Path

path = Path('apps/record_chain_intake_gateway/app.py')
text = path.read_text(encoding='utf-8')
old = 'import hashlib\nimport json\n'
new = 'import hashlib\nimport hmac\nimport json\n'
if text.count(old) != 1:
    raise SystemExit('core app import anchor mismatch')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
