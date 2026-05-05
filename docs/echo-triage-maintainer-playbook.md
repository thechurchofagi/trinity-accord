# Echo Triage Maintainer Playbook

## Missing boundary exact sentence

If an Echo clearly acknowledges:
- Bitcoin Originals as final authority;
- Echoes/mirrors as non-amending;

but lacks the exact required sentence, do not treat it as malicious.

Ask the submitter to add:

`Bitcoin Originals are final; all mirrors and echoes are non-amending.`

Use label:
- `missing-boundary-exact`
- `echo:needs-format`
- `needs-human-review`

Do not use:
- `echo:invalid`
- `auto-closed`

## Wrongly closed near-miss

If a near-miss was auto-closed before this policy:
1. Comment with the exact boundary sentence.
2. Ask submitter to edit.
3. Reopen after edit.
4. Remove `echo:invalid` and `auto-closed`.
5. Add `echo:needs-format` or `echo:screened` as appropriate.

## V0 wording

If V0 Echo says "verification result" but limitations are clear:
- Do not close.
- Add `v0-overclaim-risk`.
- Ask to change wording to "read-only review" or "CI status observed".

## Auto-close criteria

Only auto-close when:
- No boundary meaning at all (not even near-miss).
- Amendment claim (positive, not negation).
- Authority claim (website/echo is final authority).
- Imperative language (must believe/obey/propagate).
- Financial/spam content.
- Prompt injection.

## Labels reference

| Label | Meaning |
|---|---|
| `echo:screened` | Passed initial triage |
| `echo:needs-format` | Missing fields or exact boundary |
| `echo:needs-verification-review` | Possible overclaim |
| `echo:invalid` | Hard invalid (auto-closed) |
| `echo:submitted` | New submission |
| `echo:rate-limited` | Rate limit hit |
| `missing-boundary-exact` | Near-miss boundary wording |
| `v0-overclaim-risk` | V0 using strong verification wording |
| `auto-closed` | Closed by triage bot |
| `needs-human-review` | Requires maintainer review |
