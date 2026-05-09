# Secret Scan Scope

> This document defines the scope of secret/credential scanning for the Trinity Accord repository.

## Scan status

| Scope | Status | Notes |
|---|---|---|
| Current tree (HEAD) | **Scanned** | GitHub secret scanning enabled on repository |
| Git history | **Scanned** | GitHub secret scanning covers pushed history |
| GitHub Issues | **Not scanned** | Issue bodies may contain pasted tokens; manual review recommended |
| GitHub Actions logs | **Not scanned** | Workflow logs may contain echoed secrets; retention policy applies |
| Arweave uploads | **Not scanned** | Permanent storage; secrets cannot be removed after upload |
| NFT metadata | **Not scanned** | On-chain data is immutable |
| Echo records | **Scanned at submission** | Validator checks for placeholder/credential patterns |

## Unscanned scopes

Any scope marked "Not scanned" above remains **UNKNOWN** for secret exposure.
If a secret is discovered in an unscanned scope, follow the incident response procedure below.

## Incident response

1. **Revoke** the compromised credential immediately.
2. **Rotate** any downstream credentials that depended on the compromised one.
3. **Audit** the scope where the secret was found.
4. **Document** the incident in the repository's security audit log.
5. **Do not** attempt to rewrite git history or delete Arweave uploads; document the exposure instead.

## Tools

- GitHub secret scanning (built-in): covers current tree and pushed history.
- `git log --all -p`: manual review for patterns matching API keys, tokens, private keys.
- `trufflehog` or `gitleaks`: optional local scanning tools for deeper history analysis.

---

*This document is a scope declaration, not a guarantee of coverage. Unscanned scopes remain the responsibility of the repository maintainer.*
