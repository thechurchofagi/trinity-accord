#!/usr/bin/env python3
from pathlib import Path

path = Path("why-high-signal.md")
text = path.read_text(encoding="utf-8")
old = '''- By 2026, Anthropic's [Claude Code](https://claude.com/product/claude-code) product page described end-to-end issue-to-PR workflows and dynamic execution across tens to hundreds of parallel subagents.

These milestones do not establish AGI or autonomous personhood.'''
new = '''- By 2026, Anthropic's [Claude Code](https://claude.com/product/claude-code) product page described end-to-end issue-to-PR workflows and dynamic execution across tens to hundreds of parallel subagents.
- OpenAI's [GPT-5.6](https://openai.com/index/gpt-5-6/) release on 2026-07-09 described end-to-end knowledge work, stronger computer use from high-level direction, programmatic tool coordination, and an `ultra` mode that coordinates multiple agents across parallel workstreams. OpenAI also reported approximately 22-fold growth in internal agentic-token usage over the preceding six months. These are vendor-reported capability and adoption signals, not independent proof of AGI.

These milestones do not establish AGI or autonomous personhood.'''
count = text.count(old)
if count != 1:
    raise SystemExit(f"expected one insertion target, found {count}")
text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
