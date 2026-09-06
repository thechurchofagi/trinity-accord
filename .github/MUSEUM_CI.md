# Museum-only CI and Pages publication

The canonical museum is https://www.trinityaccord.org/museum/, published from
`museum/dist/` by GitHub Pages. The main site's evidence requirements remain
unchanged for changes outside `museum/`.

## Automatic scope

`scripts/museum_change_scope.py` checks the complete Git diff, including both
sides of renames. Only a nonempty change consisting entirely of ordinary files
under `museum/` qualifies. Mixed changes, missing comparison commits, symlinks,
submodules, manual runs and unknown events use the full route.

Required CI job names still report a result. The classifier must succeed before
any exemption applies; an unavailable comparison selects full checks. Unrelated
evidence, Gateway, current-system and Python compatibility steps are omitted on
the museum route. Museum inventory, provenance, local references, JavaScript
syntax and secret scans remain. Repository Integrity runs on pull requests and
main pushes, avoiding its former duplicate feature-branch push run.

The preservation DOI writer is skipped for museum-only pushes because it requires
full repository integrity. Museum Edition Release still validates and archives
each immutable museum edition. Main-site changes retain the DOI writer and its
existing integrity prerequisite.

## Publication

The deployment classifier also compares against the last successful **main push**
of Deploy Pages. This prevents an earlier unpublished main-site edit from being
carried through a museum-only exemption. A failed Actions API lookup or missing
baseline selects full verification. Manual deployments always use full checks.

Both routes keep current-main/exact-SHA binding, Jekyll build, main artifact
contracts, the complete museum export validator, exact museum copy, source
receipt, and the existing Pages deployment/retry handoffs.

For isolated museum publication, `scripts/smoke_live_museum.py` verifies the exact
canonical release manifest, the `/museum/` entrypoint, all files up to 256 KiB,
and every changed large asset against the checked-in sizes and SHA-256 hashes.
Unchanged large media is bound to the prior successful publication. If its old
inventory cannot be loaded, every current file is checked. Four concurrent
requests and four bounded per-file attempts handle transient CDN failures without
restarting successful checks. Redirects, missing files and changed bytes fail.

The follow-up production workflow uses the same scope rule. Deployment receipts
state `verification_scope=museum` or `full`; museum receipts explicitly say that
unrelated main-site live contracts were not rerun. They do not claim full main-site
verification from a museum-only result.

## Checks for this mechanism

```sh
python3 -m unittest tests.test_museum_ci_scope tests.test_museum_workflow_contract -v
python3 scripts/test_deploy_pages_workflow_contract.py
python3 scripts/test_workflow_permissions.py
```

Changing the classifier, tests or workflows is itself outside `museum/`, so such
changes must pass the full CI route before the exemptions can take effect.
