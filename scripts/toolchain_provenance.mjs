/**
 * Shared toolchain provenance collector for Node.js verification scripts.
 * Schema: trinity-accord.toolchain-provenance.v1
 */
import { execFileSync } from 'node:child_process';
import os from 'node:os';

function toolVersion(cmd, args = ['--version']) {
  try {
    const out = execFileSync(cmd, args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], timeout: 10000 });
    return out.trim().split(/\r?\n/)[0] || null;
  } catch {
    return null;
  }
}

export function collectToolchainProvenance() {
  return {
    schema: 'trinity-accord.toolchain-provenance.v1',
    node_version: process.version,
    platform: process.platform,
    arch: process.arch,
    os_release: os.release(),
    tools: {
      git: toolVersion('git'),
      curl: toolVersion('curl'),
      tar: toolVersion('tar'),
      gzip: toolVersion('gzip'),
      sha256sum: toolVersion('sha256sum'),
      ots: toolVersion('ots'),
      openssl: toolVersion('openssl', ['version']),
    },
    github_actions: {
      GITHUB_ACTIONS: process.env.GITHUB_ACTIONS || null,
      RUNNER_OS: process.env.RUNNER_OS || null,
      ImageOS: process.env.ImageOS || null,
      ImageVersion: process.env.ImageVersion || null,
      GITHUB_WORKFLOW: process.env.GITHUB_WORKFLOW || null,
      GITHUB_RUN_ID: process.env.GITHUB_RUN_ID || null,
      GITHUB_SHA: process.env.GITHUB_SHA || null,
    },
  };
}
