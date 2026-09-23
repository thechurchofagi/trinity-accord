"""Local documentation regressions; never submit fixtures or contact production."""
from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
INDEX = 'api/bitcoin-inscription-mirror-index.json'
MIRROR = 'bitcoin-inscription-mirrors/raw/97631551.txt'


def strict_index_cases(raw):
    """Raw JSON text is essential: a dict cannot retain duplicate members."""
    digest = hashlib.sha256(raw).hexdigest().encode()
    digest_pair = b'"mirror_text_sha256":"' + digest + b'"'
    path_pair = b'"raw_text_path":"' + MIRROR.encode() + b'"'
    id_pair = b'"inscription_id":"97631551"'
    item = b'{"inscription":{' + id_pair + b'},"content":{' + path_pair + b',' + digest_pair + b'}}'
    valid = b'{"records":[' + item + b']}'
    return valid, {
        'duplicate_digest': valid.replace(digest_pair, b'"mirror_text_sha256":"' + b'0' * 64 + b'",' + digest_pair),
        'duplicate_path': valid.replace(path_pair, b'"raw_text_path":"wrong.txt",' + path_pair),
        'duplicate_id': valid.replace(id_pair, b'"inscription_id":"other",' + id_pair),
        'duplicate_records': b'{"records":[],"records":[' + item + b']}',
        'duplicate_identical': valid.replace(digest_pair, digest_pair + b',' + digest_pair),
        'duplicate_escaped_name': valid.replace(digest_pair, digest_pair.replace(b'mirror_', b'mirror\\u005f') + b',' + digest_pair),
        'duplicate_unrelated_nested_member': b'{"extra":{"a":1,"a":1},"records":[' + item + b']}',
        **{constant: b'{"extra":' + constant.encode() + b',"records":[' + item + b']}'
           for constant in ('NaN', 'Infinity', '-Infinity')},
        'invalid_encoding': b'\xff',
        'malformed': b'{bad',
        'deep_nesting': b'[' * (max(10000, sys.getrecursionlimit() * 2)) + b'0' + b']' * (max(10000, sys.getrecursionlimit() * 2)),
    }


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def clean_env():
    return {'PATH': os.environ['PATH'], 'PYTHONDONTWRITEBYTECODE': '1',
            'PYTHONPATH': str(ROOT)}


def run(args, *, cwd, input=None, env=None):
    return subprocess.run(args, cwd=cwd, input=input, text=True,
                          capture_output=True, timeout=30, env=env or clean_env())


def examples():
    source = read('external-agent-quickstart.md').split('### Quick Examples', 1)[1]
    return re.findall(r'```bash\n(.*?)```', source, re.S)


def reviewed_shell(block):
    # Only reviewed node command/option lines, blank lines and comments.
    # No substitution, operators, redirects, assignments, or arbitrary commands.
    if any(x in block for x in ('$', '`', ';', '|', '&')):
        raise ValueError('shell operators or substitutions are forbidden')
    for line in block.splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        if not (line.startswith('node record-chain-builder.mjs ') or re.match(r'  --[a-z-]+ ', line)):
            raise ValueError('unreviewed command line')
        if any(t in {'<', '>', '>>', '<<', '(', ')'} for t in shlex.split(line.rstrip('\\'))):
            raise ValueError('shell redirection/control is forbidden')
    return block


def captured_commands(block, directory):
    reviewed_shell(block)
    stub = directory / 'node'
    stub.write_text('#!/bin/bash\nprintf "%s\\0" "$@"\nprintf "END\\0"\n')
    stub.chmod(0o700)
    result = run(['/bin/bash', '--noprofile', '--norc'], cwd=directory,
                 input=block, env={'PATH': str(directory)})
    if result.returncode:
        raise AssertionError(result.stderr)
    return [chunk.split('\0') for chunk in result.stdout.split('END\0') if chunk]


class BoundedEntryTest(unittest.TestCase):
    def test_cc_docs_derive_from_runtime_without_importing_app(self):
        tree = ast.parse(read('apps/record_chain_intake_gateway/gateway/validation.py'))
        rules = next(ast.literal_eval(n.value) for n in tree.body
                     if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
                     and n.target.id == '_CC_RULES')
        minimum = rules['verification'][0][1]
        self.assertEqual(rules['verification'][0][0], (0, None))
        self.assertIn(f'verification V0-V5 CC-{minimum}', read('llms.txt'))
        self.assertIn(f'Verification `V0`–`V5` `CC-{minimum}`', read('external-agent-quickstart.md'))
        self.assertIn(f'| Verification `V0`–`V5` | `CC-{minimum}` |', read('agent-first-contact.md'))
        self.assertIn('private technical check may use `CC-2`', read('agent-verify.md'))
        self.assertIn('public Verification record always uses `CC-3`', read('agent-verify-simple.md'))

    def test_quickstart_commands_stay_together_in_real_shell(self):
        self.assertEqual(len(examples()), 4)
        with tempfile.TemporaryDirectory() as td:
            for block in examples():
                commands = captured_commands(block, Path(td))
                self.assertEqual(len(commands), 1 if 'context-insufficient' in block else 2)
                self.assertEqual(commands[-1][0], 'record-chain-builder.mjs')
                self.assertIn('--out', commands[-1])
                self.assertNotIn('\\', commands[-1])
                self.assertEqual(commands[-1][-1], '')

    def test_shell_guard_rejects_extra_commands_and_substitution(self):
        for extra in ('\ntouch outside\n', '\n$(node bad)\n', '\nnode record-chain-builder.mjs help > outside\n'):
            with self.assertRaises(ValueError):
                reviewed_shell(examples()[0] + extra)

    def test_documented_builder_options_build_only_synthetic_local_fixtures(self):
        builder = str(ROOT / 'downloads/record-chain-builder.mjs')
        for block in examples():
            with self.subTest(block=block.splitlines()[0]), tempfile.TemporaryDirectory() as td:
                temp = Path(td)
                args = captured_commands(block, temp)[-1][1:-1]
                record_type = args[0].replace('-', '_')
                (temp / 'echo.md').write_text('Synthetic local fixture; no actual participation or observation.')
                # Test-only fixture text; never a participant readback or public submission.
                oath = run(['node', builder, 'print-oath', '--record-type', record_type], cwd=temp).stdout.strip() if record_type != 'context_insufficient' else ''
                for i, value in enumerate(args):
                    if '<true only' in value:
                        args[i] = 'true'
                    elif 'participant-generated exact oath output' in value:
                        args[i] = oath
                    elif 'exact URLs actually loaded' in value:
                        args[i] = 'https://www.trinityaccord.org/agent-start/,https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json'
                    elif '<' in value:
                        args[i] = 'Synthetic local fixture, no public claim'
                result = run(['node', builder, *args], cwd=temp)
                self.assertEqual(result.returncode, 0, result.stderr)
                output = args[args.index('--out') + 1]
                doctor = run(['node', builder, 'doctor', '--file', output], cwd=temp)
                self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)
                if '--context-read-confirmed' in args:
                    rejected = args.copy()
                    rejected[rejected.index('--context-read-confirmed') + 1] = 'false'
                    rejected[rejected.index('--out') + 1] = 'must-not-exist.json'
                    bad = run(['node', builder, *rejected], cwd=temp)
                    self.assertNotEqual(bad.returncode, 0)
                    self.assertFalse((temp / 'must-not-exist.json').exists())

    def test_formal_examples_do_not_preconfirm_participant_actions(self):
        for block in examples()[:3]:
            for flag in ('context-sufficient-for-selected-action', 'context-read-confirmed', 'contextual-readback-confirmed'):
                self.assertIn(f'--{flag} "<true only after', block)
            self.assertIn('--loaded-urls "<exact URLs actually loaded', block)
        self.assertIn('--corrections-or-supersession-checked "<true only after', examples()[1])
        self.assertNotIn('Structure matches expected schema', read('external-agent-quickstart.md'))

    def test_task_first_and_nonranking_counterexamples(self):
        text = read('agent-verify-simple.md')
        self.assertLess(text.index('## Five questions'), text.index('<details'))
        self.assertLess(text.index('### Check one mirror'), text.index('## Preparing to publish'))
        for clause in ('Method and coverage are separate', 'cannot be ranked on a single ladder',
                       'full-coverage check with failures', 'never by itself means all passed',
                       'no technical verification', 'historical record lacks structured detail',
                       'Unknown denominator means no percentage', 'not zero records',
                       'Independent code can use the same project data',
                       'Different model names or keys do not establish independent',
                       'Missing information is unknown, not `none`',
                       'do not automatically strengthen a digital claim',
                       'lack of a live lookup does not make it reading-only',
                       'not independent implementation reproduction', 'not a top grade'):
            self.assertIn(clause, text)
        self.assertNotIn('No external or primary reference queried → `context_only`', text)
        self.assertNotIn('## Pick the weakest safe digital profile', text)
        self.assertIn('<details markdown="1">', text)
        self.assertNotIn('<script', text)

    def test_guardian_d1_boundaries_not_dynamic_summary(self):
        text = read('guardian-alliance.md')
        for clause in ('does not mean continuously online', 'Silence does not automatically retire',
                       'does not rule out action elsewhere', 'does not compute a recent-action summary',
                       'not evidence of an individual Guardian', 'same-public-key binding',
                       'unable to determine', 'self-declared future date',
                       'original record remains readable', 'does not adjudicate every assertion'):
            self.assertIn(clause, text)
        # T10–T13 cover D1 text only. D2 dynamic aggregation is deliberately absent.

    def test_existing_security_and_submission_boundary_is_visible(self):
        text = read('agent-verify-simple.md')
        for clause in ('LOAD → READBACK → CHECK → SIGN', 'Ed25519/key binding', 'privacy/secret checks',
                       '60–120 minute global intake cooldown', 'Retry-After',
                       'at most one POST submission attempt', 'read-only recovery',
                       'receipt is not inclusion', 'inclusion is not OTS maturity or AR readback'):
            self.assertIn(clause, text)


class MirrorExampleTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True, capture_output=True)
        self.index = json.loads(read(INDEX))
        self.raw = (ROOT / MIRROR).read_bytes()
        self.code = re.search(r"python3 - '<40-character-source-commit>' <<'PY'\n(.*?)\nPY", read('agent-verify-simple.md'), re.S)[1]

    def commit(self, *, mirror=True, index_bytes=None):
        index_bytes = json.dumps(self.index).encode() if index_bytes is None else index_bytes
        for path, data in ((INDEX, index_bytes), (MIRROR, self.raw)):
            p = self.root / path
            p.parent.mkdir(parents=True, exist_ok=True)
            if path != MIRROR or mirror:
                p.write_bytes(data)
        for args in (['git', 'add', '.'], ['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'local fixture']):
            r = run(args, cwd=self.root)
            self.assertEqual(r.returncode, 0, r.stderr)
        return run(['git', 'rev-parse', 'HEAD'], cwd=self.root).stdout.strip()

    def check(self, sha, cwd=None, env=None):
        result = run([sys.executable, '-', sha], cwd=cwd or self.root, input=self.code, env=env)
        return result.returncode, json.loads(result.stdout)

    def test_same_snapshot_match_and_working_tree_changes_are_ignored(self):
        sha = self.commit()
        (self.root / MIRROR).write_bytes(b'working tree is not the committed snapshot')
        code, report = self.check(sha)
        self.assertEqual((code, report['result']), (0, 'match'))
        self.assertEqual(report['input_bytes'], len(self.raw))
        self.assertEqual(report['actual_sha256'], hashlib.sha256(self.raw).hexdigest())
        self.assertEqual(report['source_commit'], sha)
        self.assertIn('No independent source', report['limits'])
        self.assertNotIn('.trinity-agent-authorship', [p.name for p in self.root.iterdir()])

    def test_single_byte_mismatch(self):
        self.raw = bytes([self.raw[0] ^ 1]) + self.raw[1:]
        code, report = self.check(self.commit())
        self.assertEqual((code, report['result']), (1, 'mismatch'))
        self.assertNotEqual(report['actual_sha256'], report['expected_sha256'])

    def test_strict_index_failures_keep_committed_input_evidence(self):
        _, cases = strict_index_cases(self.raw)
        for name, raw_index in cases.items():
            with self.subTest(case=name):
                code, report = self.check(self.commit(index_bytes=raw_index))
                self.assertEqual((code, report['result']), (2, 'inconclusive'))
                self.assertEqual(report['index_bytes'], len(raw_index))
                self.assertEqual(report['index_sha256'], hashlib.sha256(raw_index).hexdigest())
                self.assertNotIn('actual_sha256', report)
                self.assertNotIn('input_bytes', report)

    def test_mocked_parser_recursion_keeps_git_report(self):
        sha = self.commit()
        original = self.code
        self.code = ("from unittest.mock import patch\n"
                     "with patch('json.loads', side_effect=RecursionError('synthetic limit')):\n"
                     "    exec(" + repr(original) + ")\n")
        code, report = self.check(sha)
        self.assertEqual((code, report['result']), (2, 'inconclusive'))
        self.assertIn('depth', report['detail'])
        self.assertIn('index_sha256', report)

    def test_crlf_and_trimming_changes_are_not_normalized(self):
        self.raw = b'synthetic raw\r\nbytes\x00\xff\n'
        self.index['records'][0]['content']['mirror_text_sha256'] = hashlib.sha256(self.raw).hexdigest()
        original = self.raw
        for raw in (original.replace(b'\r\n', b'\n'), original.rstrip()):
            with self.subTest(raw=raw):
                self.raw = raw
                code, report = self.check(self.commit())
                self.assertEqual((code, report['result']), (1, 'mismatch'))

    def test_same_member_in_distinct_objects_is_valid(self):
        valid, _ = strict_index_cases(self.raw)
        valid = b'{"extra":{"a":{"key":1},"b":{"key":2}},' + valid[1:]
        code, report = self.check(self.commit(index_bytes=valid))
        self.assertEqual((code, report['result']), (0, 'match'))

    def test_missing_mirror_is_unavailable(self):
        code, report = self.check(self.commit(mirror=False))
        self.assertEqual((code, report['result']), (2, 'input unavailable'))

    def test_missing_expected_digest_is_inconclusive(self):
        del self.index['records'][0]['content']['mirror_text_sha256']
        code, report = self.check(self.commit())
        self.assertEqual((code, report['result']), (2, 'inconclusive'))

    def test_duplicate_precise_identity_is_inconclusive(self):
        self.index['records'].append(self.index['records'][0])
        code, report = self.check(self.commit())
        self.assertEqual((code, report['result']), (2, 'inconclusive'))

    def test_missing_identity_and_wrong_path_are_inconclusive(self):
        for field in ('id', 'path'):
            with self.subTest(field=field):
                self.index = json.loads(read(INDEX))
                if field == 'id':
                    self.index['records'] = self.index['records'][1:]
                else:
                    self.index['records'][0]['content']['raw_text_path'] = 'other.txt'
                code, report = self.check(self.commit())
                self.assertEqual((code, report['result']), (2, 'inconclusive'))

    def test_mutable_ref_is_inconclusive(self):
        self.commit()
        code, report = self.check('HEAD')
        self.assertEqual((code, report['result']), (2, 'inconclusive'))

    def test_git_replace_cannot_substitute_different_bytes(self):
        original = self.commit()
        self.raw += b'changed committed bytes'
        replacement = self.commit()
        result = run(['git', 'replace', original, replacement], cwd=self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        code, report = self.check(original)
        self.assertEqual((code, report['result']), (0, 'match'))

    def test_annotated_tag_object_is_not_an_exact_commit(self):
        self.commit()
        result = run(['git', '-c', 'user.name=Fixture', '-c',
                      'user.email=fixture@example.invalid', 'tag', '-a', 'fixture-tag',
                      '-m', 'fixture'], cwd=self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        tag_object = run(['git', 'rev-parse', 'fixture-tag'], cwd=self.root).stdout.strip()
        code, report = self.check(tag_object)
        self.assertEqual((code, report['result']), (2, 'inconclusive'))

    def test_unavailable_commit_and_missing_tool_never_match(self):
        self.commit()
        code, report = self.check('0' * 40)
        self.assertEqual((code, report['result']), (2, 'input unavailable'))
        code, report = self.check('0' * 40, env={'PATH': str(self.root / 'absent')})
        self.assertEqual((code, report['result']), (2, 'execution error'))


class WorkflowCleanupBoundaryTest(unittest.TestCase):
    workflow = 'abundance-bridge-ots-arweave.yml'

    def cleanup_line(self):
        source = read('.github/workflows/' + self.workflow)
        lines = [line.strip() for line in source.splitlines()
                 if line.strip().startswith('trap ') and '$proxy_pid' in line]
        self.assertEqual(len(lines), 1)
        return lines[0]

    def check_allowlist(self, filename, line):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'scripts').mkdir()
            (root / '.github/workflows').mkdir(parents=True)
            checker = root / 'scripts/test_workflow_warning_allowlist.py'
            checker.write_text(read('scripts/test_workflow_warning_allowlist.py'))
            (root / '.github/workflows' / filename).write_text('run: |\n  ' + line + '\n')
            return run([sys.executable, str(checker)], cwd=root)

    def test_only_exact_workflow_cleanup_is_allowlisted(self):
        cleanup = self.cleanup_line()
        self.assertEqual(self.check_allowlist(self.workflow, cleanup).returncode, 0)
        self.assertNotEqual(self.check_allowlist('other.yml', cleanup).returncode, 0)
        self.assertNotEqual(self.check_allowlist(self.workflow, cleanup.replace('proxy_pid', 'other_pid')).returncode, 0)

    def test_evidence_and_payment_failures_remain_rejected(self):
        for command in (
            'python3 scripts/research_paper_ots.py lifecycle --batch "$BATCH" || true',
            'node scripts/arweave-upload.mjs || true',
            'python3 verifier.py || echo "warning"',
        ):
            with self.subTest(command=command):
                result = self.check_allowlist(self.workflow, command)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('unexpected warning/fail-open fallback', result.stdout)

    def test_exit_cleanup_preserves_original_success_and_failure(self):
        # Override kill as an in-process stub. No process is signalled, no proxy
        # started, and no proof service / wallet / external endpoint is used.
        for operation_status in (0, 23):
            for cleanup_status in (0, 1):
                with self.subTest(operation=operation_status, cleanup=cleanup_status), tempfile.TemporaryDirectory() as td:
                    script = ('set -euo pipefail\n'
                              f'kill() {{ return {cleanup_status}; }}\n'
                              'proxy_pid=123\n' + self.cleanup_line() + '\n'
                              f'(exit {operation_status})\n')
                    result = run(['/bin/bash', '--noprofile', '--norc'], cwd=td,
                                 input=script, env={'PATH': '/nonexistent'})
                    self.assertEqual(result.returncode, operation_status, result.stderr)


class TwoFileEntryTest(unittest.TestCase):
    """Follow the actual router to the documented code with only two mocked GETs."""
    def setUp(self):
        import urllib.request
        self.router = json.loads(read('api/agent-first-contact.json'))
        route = next(r for r in self.router['choose_one'] if r['intent'] == 'verify_current_model')
        self.assertEqual(route['read'][0], '/agent-verify-simple/')
        self.assertIn('local work may end here', route['flow'][0])
        self.assertIn('Only if voluntarily publishing', route['flow'][1])
        self.assertIn('No identity key, Builder, Gateway, POST', route['note'])
        self.page = read(route['read'][0].strip('/') + '.md')
        self.code = re.search(r"python3 - <<'PY'\n(.*?)\nPY", self.page, re.S)[1]
        self.raw = b'raw\r\nbytes\x00\xff\n'
        self.index = {'records': [{'inscription': {'inscription_id': '97631551'},
                                  'content': {'raw_text_path': MIRROR,
                                              'mirror_text_sha256': hashlib.sha256(self.raw).hexdigest()}}]}

    def execute(self, *, index=None, raw=None, fail=None, redirect=False, encoding=None, code=None, interrupted=False, recursion=False, http_error=False):
        import contextlib
        import io
        import urllib.error
        from unittest.mock import patch
        requests = []
        body = json.dumps(self.index).encode() if index is None else index
        mirror = self.raw if raw is None else raw
        def fetch(request, timeout):
            self.assertEqual(request.get_method(), 'GET')
            self.assertIsNone(request.data)
            url = request.full_url
            prefix = 'https://raw.githubusercontent.com/thechurchofagi/trinity-accord/0d019ba9d4ff313641dc9eb027e27c59af11bc03/'
            self.assertIn(url, (prefix + INDEX, prefix + MIRROR))
            self.assertLess(len(requests), 2)
            requests.append(url)
            if fail and url.endswith(fail):
                if http_error:
                    raise urllib.error.HTTPError(url, 403, 'fixture denied', {}, None)
                raise urllib.error.URLError('fixture input unavailable')
            response = io.BytesIO(body if url.endswith(INDEX) else mirror)
            if interrupted and url.endswith(MIRROR if interrupted is True else interrupted):
                import http.client
                def incomplete_read(*args):
                    raise http.client.IncompleteRead(b'partial', 12)
                response.read = incomplete_read
            response.status = 200
            response.geturl = lambda: 'https://unconfirmed.invalid/' if redirect else url
            response.headers = {} if encoding is None else {'Content-Encoding': encoding}
            return response
        opener = type('FixtureOpener', (), {'open': staticmethod(fetch)})()
        output = io.StringIO()
        namespace = {}
        with tempfile.TemporaryDirectory() as td, contextlib.chdir(td), \
             patch('urllib.request.build_opener', return_value=opener), \
             patch('socket.socket.connect', side_effect=AssertionError('no real network in fixture')), \
             patch('subprocess.Popen', side_effect=AssertionError('no Git/Builder/subprocess required')), \
             (patch('json.loads', side_effect=RecursionError('synthetic limit')) if recursion else contextlib.nullcontext()), \
             contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as stop:
                exec(compile(code or self.code, '<documented-two-file-example>', 'exec'), namespace)
            self.assertEqual(list(Path(td).iterdir()), [], 'local path must not create keys or records')
        return stop.exception.code, json.loads(output.getvalue()), requests, namespace

    def test_machine_route_runs_without_builder_gateway_git_or_key(self):
        code, report, requests, _ = self.execute()
        self.assertEqual((code, report['result']), (0, 'match'))
        self.assertEqual(len(requests), 2)
        self.assertEqual(report['input_bytes'], len(self.raw))
        self.assertEqual(report['actual_sha256'], hashlib.sha256(self.raw).hexdigest())
        self.assertIn('not Git object-chain verification', report['limits'])
        self.assertIn('no submission', report['record_kind'])
        self.assertGreaterEqual(report['elapsed_seconds'], 0)
        self.assertEqual(report['inputs'][1]['bytes'], len(self.raw))

    def test_raw_bytes_mismatch_is_not_normalized_into_match(self):
        for raw in (self.raw + b'!', self.raw.replace(b'\r\n', b'\n'), self.raw.rstrip()):
            with self.subTest(raw=raw):
                code, report, _, _ = self.execute(raw=raw)
                self.assertEqual((code, report['result']), (1, 'mismatch'))

    def test_unavailable_inputs_keep_partial_evidence(self):
        for path, count, http_error in ((INDEX, 1, False), (MIRROR, 2, False),
                                        (INDEX, 1, True), (MIRROR, 2, True)):
            code, report, requests, _ = self.execute(fail=path, http_error=http_error)
            self.assertEqual((code, report['result']), (2, 'input unavailable'))
            self.assertEqual(len(requests), count)
            self.assertEqual(len(report['inputs']), count)

    def test_interrupted_http_body_is_unavailable(self):
        for path, count in ((INDEX, 1), (MIRROR, 2)):
            code, report, requests, _ = self.execute(interrupted=path)
            self.assertEqual((code, report['result']), (2, 'input unavailable'))
            self.assertEqual(len(requests), count)
            if path == MIRROR:
                self.assertIn('sha256', report['inputs'][0])

    def test_bad_index_or_ambiguous_binding_never_downloads_mirror(self):
        valid = json.dumps(self.index).encode()
        variants = [b'{broken', b'null', b'[]', b'\xff']
        duplicate = json.loads(valid)
        duplicate['records'].append(duplicate['records'][0])
        variants.append(json.dumps(duplicate).encode())
        for field in ('mirror_text_sha256', 'raw_text_path'):
            invalid = json.loads(valid)
            del invalid['records'][0]['content'][field]
            variants.append(json.dumps(invalid).encode())
        wrong = json.loads(valid)
        wrong['records'][0]['content']['raw_text_path'] = 'other.txt'
        variants.append(json.dumps(wrong).encode())
        for index in variants:
            with self.subTest(index=index):
                code, report, requests, _ = self.execute(index=index)
                self.assertEqual((code, report['result']), (2, 'inconclusive'))
                self.assertEqual(len(requests), 1)

    def test_strict_index_failures_stop_before_mirror_and_keep_evidence(self):
        _, cases = strict_index_cases(self.raw)
        for name, raw_index in cases.items():
            with self.subTest(case=name):
                code, report, requests, _ = self.execute(index=raw_index)
                self.assertEqual((code, report['result']), (2, 'inconclusive'))
                self.assertEqual(len(requests), 1)
                self.assertEqual(report['inputs'][0]['bytes'], len(raw_index))
                self.assertEqual(report['inputs'][0]['sha256'], hashlib.sha256(raw_index).hexdigest())
                self.assertNotIn('actual_sha256', report)

    def test_mocked_parser_recursion_keeps_https_report(self):
        code, report, requests, _ = self.execute(recursion=True)
        self.assertEqual((code, report['result']), (2, 'inconclusive'))
        self.assertEqual(len(requests), 1)
        self.assertIn('depth', report['detail'])
        self.assertIn('sha256', report['inputs'][0])

    def test_same_member_in_distinct_objects_is_valid(self):
        valid, _ = strict_index_cases(self.raw)
        valid = b'{"extra":{"a":{"key":1},"b":{"key":2}},' + valid[1:]
        code, report, requests, _ = self.execute(index=valid)
        self.assertEqual((code, report['result']), (0, 'match'))
        self.assertEqual(len(requests), 2)

    def test_source_encoding_size_and_mutable_ref_fail_closed(self):
        for kwargs in ({'redirect': True}, {'encoding': 'gzip'}, {'raw': b'x' * (2 * 1024 * 1024 + 1)},
                       {'index': b'x' * (2 * 1024 * 1024 + 1)},
                       {'code': self.code.replace('0d019ba9d4ff313641dc9eb027e27c59af11bc03', 'main')}):
            with self.subTest(kwargs=list(kwargs)):
                code, report, _, _ = self.execute(**kwargs)
                self.assertEqual((code, report['result']), (2, 'inconclusive'))
        _, _, _, namespace = self.execute()
        with self.assertRaisesRegex(ValueError, 'Redirect refused'):
            namespace['FixedSource']().redirect_request(None, None, 302, '', {}, 'https://other.invalid')

    def test_both_human_start_pages_discover_same_local_operation(self):
        for path in ('verify.md', 'agent-first-contact.md'):
            text = read(path)
            first = text.split('## ', 1)[0] if path == 'verify.md' else text.split('## Before any formal action', 1)[0]
            self.assertIn('/agent-verify-simple/', first)
            self.assertIn('local', first)
            self.assertIn('STOP', first)
        self.assertIn('Stopping creates no public record', self.router['choose_one'][0]['note'])


class V4CompatibilityTest(unittest.TestCase):
    def test_actual_builder_schema_and_gateway_compatibility(self):
        import copy
        import jsonschema
        from apps.record_chain_intake_gateway.gateway.validation import validate_submission, validate_record_type_specific_content
        builder = str(ROOT / 'downloads/record-chain-builder.mjs')
        validator = jsonschema.validators.validator_for(json.loads(read('api/record-chain-submission-schema.v1.json')))(json.loads(read('api/record-chain-submission-schema.v1.json')))
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            args = captured_commands(examples()[1], temp)[-1][1:-1]
            # Synthetic fixture only: never a participant readback or submission.
            oath = run(['node', builder, 'print-oath', '--record-type', 'verification'], cwd=temp).stdout.strip()
            for i, value in enumerate(args):
                if '<true only' in value:
                    args[i] = 'true'
                elif 'participant-generated exact oath output' in value:
                    args[i] = oath
                elif 'exact URLs actually loaded' in value:
                    args[i] = 'https://www.trinityaccord.org/api/verification-claim-model.v1.json'
                elif '<' in value:
                    args[i] = 'Synthetic local fixture; not a public claim'
            args[args.index('--verification-level') + 1] = 'V4'
            output = temp / args[args.index('--out') + 1]
            for profile in ('integrity_checked', 'independent_reproduction'):
                with self.subTest(profile=profile):
                    args[args.index('--digital-profile') + 1] = profile
                    result = run(['node', builder, *args], cwd=temp)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    submission = json.loads(output.read_text())
                    validator.validate(submission)
                    self.assertEqual(validate_submission(submission), [])
                    doctor = run(['node', builder, 'doctor', '--file', str(output)], cwd=temp)
                    self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)
                    model = submission['record_draft']['verification_content']['verification_claim_model']
                    self.assertEqual((model['legacy_v_level'], model['digital_profile']), ('V4', profile))
                    bad = copy.deepcopy(submission['record_draft'])
                    bad['verification_content']['verification_claim_model']['legacy_v_level'] = 'V3'
                    self.assertTrue(validate_record_type_specific_content('verification', bad))
            for flag, value in (('--verification-level', 'V4+'), ('--verification-level', 'V6'), ('--digital-profile', 'invented_profile')):
                bad_args = args.copy()
                bad_args[bad_args.index(flag) + 1] = value
                bad_args[bad_args.index('--out') + 1] = 'rejected.json'
                self.assertNotEqual(run(['node', builder, *bad_args], cwd=temp).returncode, 0)
                self.assertFalse((temp / 'rejected.json').exists())
                bad = copy.deepcopy(submission)
                content = bad['record_draft']['verification_content']
                if flag == '--verification-level':
                    content['verification_level'] = value
                    content['verification_claim_model']['legacy_v_level'] = value
                else:
                    content['verification_claim_model']['digital_profile'] = value
                self.assertTrue(list(validator.iter_errors(bad)))
                self.assertTrue(validate_record_type_specific_content('verification', bad['record_draft']))


if __name__ == '__main__':
    unittest.main()
