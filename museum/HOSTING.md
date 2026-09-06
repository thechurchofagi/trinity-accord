# Museum hosting

GitHub `thechurchofagi/trinity-accord`, directory `museum/`, is the only maintained
source. The Alibaba Cloud Hong Kong host at `47.76.142.75` serves an exact copy
of `museum/dist/`; do not edit exhibition files on the server.

## Automatic publication

The host checks GitHub every five minutes (plus up to 15 seconds jitter). It
selects the latest successful **Museum edition** push workflow on `main`, pins
its commit SHA, and downloads only the static export. Unchanged files are
reused locally. All manifest sizes and SHA-256 digests must match before an
atomic symlink switch. A loopback HTTP check rolls back a bad switch. Failed
downloads leave the current release running. No GitHub token or SSH key is
needed on either side. A failed museum workflow does not deploy.

This uses the existing independent museum checks, not the main site's complete
record-chain deployment checks. Commit changed runtime bundles and regenerate
the export inventory using the museum's existing build instructions.

Install from a reviewed checkout as root:

```sh
bash museum/scripts/install_host_sync.sh
```

The timer executes the root-owned sync program as the unprivileged
`museumdeploy` user, with write access confined to `/srv/trinity-museum`.
Fetched repository code is never executed. Changes to the sync program itself
require an explicit reinstall from a reviewed checkout.

```sh
systemctl status trinity-museum-sync.timer
journalctl -u trinity-museum-sync.service -n 20 --no-pager
systemctl start trinity-museum-sync.service
cat /srv/trinity-museum/current/deployment.json
```

The initial manually installed v1.13.1 snapshot may not have a deployment receipt
until the first changed export. The bootstrap snapshot is retained; automated
releases retain the current and previous version. Rollback: stop the timer,
point `current` to the retained release using atomic rename, and check local HTTP.
Certificate renewal is handled separately by `certbot-renew.timer`.

## Address cutover

Canonical address: `https://museum.trinityaccord.org/` (served directly at the root). The A record `museum` → `47.76.142.75` is configured in the
authoritative DNS zone for `trinityaccord.org`. Its nameservers are
`a.share-dns.com` and `b.share-dns.net`; it is not the Alibaba `asi.org.cn` zone.

The canonical host has a Let's Encrypt certificate with automatic renewal.
The `museum.asi.org.cn` alias redirects to it. GitHub Pages entry HTML also
redirects while preserving the path, query and fragment. The same HTML runs
on the canonical host without redirecting; there is no separate museum codebase.
For any future move, verify HTTPS and resources before changing redirects.
Do not move `www.trinityaccord.org` or the main site as part of this cutover.

## Root-path serving

The public HTTPS virtual host serves `/srv/trinity-museum/current/museum`
as its document root, with `index index.html` and ordinary `try_files`.
Keep `/deployment.json` rooted at `/srv/trinity-museum/current`, and retain
`/museum/` as a compatibility alias to the same museum directory. Do not
redirect the root back to `/museum/`. Legacy HTML normalizes its displayed
URL before relative resources load, preserving query parameters and fragments.
Using History API normalization also avoids loops in browsers that cached the
former redirect from `/` to `/museum/`.

The private health virtual host and sync program keep their original directory
layout. Changing the public mapping does not change automatic publication.
Back up the existing public virtual-host configuration, apply the root mapping,
run `nginx -t`, reload, and verify HTTPS HTML, JS, media, old paths and receipts.
Do not replace TLS or unrelated virtual-host configuration.
