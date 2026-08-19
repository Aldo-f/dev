# Session 2026-07-29: Hermes WebUI not starting after reboot

## Problem
After a reboot, the Hermes WebUI was not accessible at http://192.168.0.5:8787/. The user expected the service `app-hermes-webui.service` to be running.

## Investigation
1. No systemd unit named app-hermes-webui.service existed. The existing unit was named app-hermes-ui.service and was missing the HERMES_WEBUI_HOST=0.0.0.0 environment variable, causing the UI to bind only to 127.0.0.1 (localhost) and not be reachable on the LAN.

## Steps Taken
1. Checked service status: `systemctl status app-hermes-webui.service` → unit not found.
2. Listed hermes-related services: `systemctl list-units --type=service | grep -i hermes` → showed app-hermes-ui.service active but bound to 127.0.0.1:8787.
3. Stopped and disabled the incorrect service:
   - `sudo systemctl stop app-hermes-ui.service`
   - `sudo systemctl disable app-hermes-ui.service`
4. Created correct systemd unit at /etc/systemd/system/app-hermes-webui.service with:
   - WorkingDirectory=/home/aldo/dev/02-ai-hermes-webui
   - ExecStart=/home/aldo/.hermes/hermes-agent/venv/bin/python /home/aldo/dev/02-ai-hermes-webui/server.py
   - Environment=HERMES_HOME=/home/aldo/.hermes
   - Environment=HERMES_WEBUI_HOST=0.0.0.0
5. Reloaded systemd: `sudo systemctl daemon-reload`
6. Enabled and started the new service:
   - `sudo systemctl enable app-hermes-webui.service`
   - `sudo systemctl start app-hermes-webui.service`
7. Verified status and logs:
   - `sudo systemctl status app-hermes-webui.service` → active (running)
   - Journal showed binding to 0.0.0.0:8787 with warning about no password set (expected for LAN access confirmed LAN host:8787/health` returned 200.

## Outcome
The Hermes WebUI is now running on port 8787, accessible from any device on the 192.168.0.0/24 network, and will start automatically on boot.

## Note
The service logs a warning about no password set. For production use, set HERMES_WEBUI_PASSWORD or use the WebUI Settings → Authentication to set a password.