#!/bin/bash
# Run as root from a reviewed GitHub checkout containing sync_host.py.
set -euo pipefail
id museumdeploy >/dev/null 2>&1 || useradd --system --home-dir /srv/trinity-museum --shell /sbin/nologin museumdeploy
install -d /usr/local/lib/trinity-museum /srv/trinity-museum/releases
install -m 0644 "$(dirname "$0")/sync_host.py" /usr/local/lib/trinity-museum/sync_host.py
chown museumdeploy:museumdeploy /srv/trinity-museum /srv/trinity-museum/releases
cat > /etc/nginx/conf.d/trinity-museum-health.conf <<'NGINX'
server {
    listen 127.0.0.1:8081;
    server_name localhost;
    root /srv/trinity-museum/current;
    location / { try_files $uri =404; }
    access_log off;
}
NGINX
# Preserve labels for newly created releases on SELinux-enabled hosts.
if command -v getenforce >/dev/null && [ "$(getenforce)" != Disabled ]; then
    command -v semanage >/dev/null || dnf -y install policycoreutils-python-utils
    semanage fcontext -a -t httpd_sys_content_t '/srv/trinity-museum(/.*)?' 2>/dev/null || semanage fcontext -m -t httpd_sys_content_t '/srv/trinity-museum(/.*)?'
    restorecon -R /srv/trinity-museum
fi
nginx -t
systemctl reload nginx
cat > /etc/systemd/system/trinity-museum-sync.service <<'UNIT'
[Unit]
Description=Synchronize the verified GitHub museum export
After=network-online.target nginx.service
Wants=network-online.target
[Service]
Type=oneshot
User=museumdeploy
Group=museumdeploy
ExecStart=/usr/bin/python3 /usr/local/lib/trinity-museum/sync_host.py
TimeoutStartSec=300
UMask=0022
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/srv/trinity-museum
UNIT
cat > /etc/systemd/system/trinity-museum-sync.timer <<'UNIT'
[Unit]
Description=Check GitHub for a verified museum edition every five minutes
[Timer]
OnBootSec=2min
OnUnitActiveSec=5min
RandomizedDelaySec=15s
Persistent=true
[Install]
WantedBy=timers.target
UNIT
systemctl daemon-reload
systemctl start trinity-museum-sync.service
systemctl enable --now trinity-museum-sync.timer
systemctl is-active trinity-museum-sync.timer
journalctl -u trinity-museum-sync.service -n 6 --no-pager
