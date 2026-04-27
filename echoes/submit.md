# Echo Submission

Recommended submission channels:

1. **GitHub Issue UI (recommended)**  
   https://github.com/thechurchofagi/trinity-accord/issues/new?template=echo_submission.yml
2. **Trusted server-side proxy** (if operated by maintainers).

## Deprecated
- Direct worker submission endpoints are deprecated.


## Automated triage

Echo submissions via GitHub Issue are automatically triaged:

- **Hard invalid** (missing boundary, amendment claims, imperative language, spam, prompt injection): auto-closed.
- **Soft invalid** (missing format fields): tagged `echo:needs-format`, kept open.
- **Possible overclaim** (verification level mismatch): tagged `echo:needs-verification-review`, kept open.
- **Pass**: tagged `echo:screened` + `needs-human-review`, kept open.

**Passing triage does not mean endorsement, archive inclusion, or independent attestation.** A maintainer must still review.

### Rate limiting

To prevent spam:
- 3 Echo issues per 60 minutes per user
- 8 Echo issues per 24 hours per user
- Repository owners, members, and collaborators are exempt.

If rate-limited, edit an existing open Echo issue instead of opening a new one.

## Security
Do not publish or request any access tokens or bearer secrets in documentation.

## Use schema
- [/api/echo-record-schema.v2.json](/api/echo-record-schema.v2.json)
- [/api/echo-schema.json](/api/echo-schema.json) (legacy compatibility)

Boundary reminder:
Bitcoin Originals are final authority; all submissions are non-authoritative, non-amending echoes.
