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

    def commit(self, *, mirror=True):
        for path, data in ((INDEX, json.dumps(self.index).encode()), (MIRROR, self.raw)):
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


if __name__ == '__main__':
    unittest.main()
