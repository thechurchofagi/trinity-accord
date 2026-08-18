#!/usr/bin/env node
import assert from 'assert';
import fs from 'fs';
import os from 'os';
import path from 'path';
import {
  classifyCarError,
  createCarTrace,
  sanitizeEndpoint,
  sanitizeTraceText,
} from './chronicle-sidechain-car-trace.mjs';

const sanitized = sanitizeEndpoint('https://user:pass@example.test/ipfs/bafy123?format=car&dag-scope=all&token=secret#frag');
assert.equal(sanitized, 'https://example.test/ipfs/bafy123?format=car&dag-scope=all');
assert(!sanitized.includes('secret'));
assert(!sanitized.includes('pass'));

const text = sanitizeTraceText('failed https://example.test/ipfs/bafy?format=car&token=secret token=abc123');
assert(text.includes('format=car'));
assert(!text.includes('secret'));
assert(!text.includes('abc123'));
assert.equal(classifyCarError(new Error('linked block missing')), 'car_incomplete_dag');
assert.equal(classifyCarError(new Error('truncated varint')), 'car_truncated');
assert.equal(classifyCarError(new Error('HTTP 429 Too Many Requests')), 'rate_limit');
assert.equal(classifyCarError(new Error('operation timed out')), 'timeout');

const root = fs.mkdtempSync(path.join(os.tmpdir(), 'chronicle-car-trace-'));
const trace = createCarTrace({ out: root });
trace.phase('cache_audit', 'running');
trace.emit({ event: 'whole_dag_attempt', endpoint: 'https://example.test/ipfs/bafy?format=car&token=secret', root_cid: 'bafy' });
trace.failure('whole_dag_invalid', new Error('linked block missing'), { endpoint: 'https://example.test/ipfs/bafy?format=car&token=secret' });
trace.observeConsole('warn', '[CAR FAILED] cid=bafy token=supersecret');
const rows = fs.readFileSync(trace.file, 'utf8').trim().split('\n').map(JSON.parse);
assert.equal(rows.length, 4);
assert.deepEqual(rows.map(row => row.seq), [1, 2, 3, 4]);
assert(rows.every(row => row.schema === 'trinity-accord/chronicle-sidechain-car-trace/v1'));
assert.equal(rows[2].error_class, 'car_incomplete_dag');
assert(!fs.readFileSync(trace.file, 'utf8').includes('supersecret'));
assert(!fs.readFileSync(trace.file, 'utf8').includes('token=secret'));

fs.rmSync(root, { recursive: true, force: true });
console.log('[TRACE TEST OK] sanitization + classification + JSONL persistence');
