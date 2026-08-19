---
name: mcp-server-integration
description: "Use when registering an MCP server with Hermes and opencode."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [MCP, opencode, hermes, integration, configuration]
---

# MCP Server Integration (Hermes + opencode)

MCP is a client-agnostic protocol: any server registered via `claude mcp add` also works with Hermes and opencode. This skill covers registering an external MCP server with both, verifying it, and activating it.

## When to Use

- User asks to integrate an MCP server repo/project with opencode and/or Hermes
- Adding a new stdio MCP server (Python `uv run`/`uvx`, Node `npx`, binary) or HTTP server
- MCP server works in Claude Code but you need it in other agents

## Prerequisites

- `uv` (Python servers) or `node` (npx servers) on PATH — install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh` (goes to ~/.local/bin)
- Hermes venv has the `mcp` package: `/home/aldo/.hermes/hermes-agent/venv/bin/python -c "import mcp"` (install with `pip install mcp` if missing; MCP support silently disables without it)

## Procedure

### 1. Verify the server runs standalone

Clone the repo, then run its smoke test first (e.g. `uv run tests/test_guards.py`).

**PEP 723 pinning pitfall**: inline-script dependencies (`# dependencies = ["mcp[cli]>=1.0.0", ...]`) resolve to the LATEST package. Newer `mcp` SDK versions removed `mcp.server.fastmcp` — pin major versions in BOTH server.py and test files:
```
"mcp[cli]>=1.0.0,<2.0.0"
```
After pinning, force re-resolve with `uv run --refresh`.

Windows-style tests will fail on Linux (drive-letter paths, case-insensitive assertions) — check the code is POSIX-correct (`os.path.normcase` is a no-op on Linux = case-sensitive; `Path()` on POSIX treats `C:\...` as one segment) rather than chasing test failures.

### 2. End-to-end MCP client test (before registering anywhere)

Spawn the real server and call tools via the `mcp` client (hermes venv python):

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async with stdio_client(params) as (r, w):
    async with ClientSession(r, w) as s:
        await s.initialize()
        tools = await s.list_tools()
        await s.call_tool("some_tool", {...})
```

Call a DETERMINISTIC tool first (no model needed) to validate plumbing, then a model-backed one.

### 3. Register with Hermes

```bash
hermes mcp add <name> --command uv --args run /abs/path/server.py --connect-timeout 120
```

- Non-TTY shells cancel at the "Enable all N tools?" prompt — pipe the answer: `printf 'Y\n' | hermes mcp add ...`
- Env vars for the subprocess: `--env KEY=VALUE` (Hermes FILTERS the subprocess env: only PATH/HOME/USER/LANG/etc. pass through; API keys must be explicit)
- Writes to `~/.hermes/config.yaml` under `mcp_servers` (dict format: `name: {command, args, url, env, connect_timeout}`)

**Legacy list pitfall**: an old-style `mcp_servers:` block like
```yaml
mcp_servers:
  - name: foo
    url: http://localhost:5000
```
is invisible to `hermes mcp list` AND crashes `hermes mcp add` with `TypeError: list indices must be integers`. Migrate to dict format first:
```yaml
mcp_servers:
  foo:
    url: http://localhost:5000
```
Never hand-edit config.yaml — but a surgical python replace (with backup) is fine when the CLI itself crashes on bad legacy data. Warn the user if they have the file open in an editor (stale buffer can clobber the fix).

### 4. Register with opencode

Merge into the GLOBAL config `~/.config/opencode/opencode.jsonc` (backup first):
```json
"mcp": {
  "<name>": {
    "type": "local",
    "command": ["uv", "run", "/abs/path/server.py"],
    "enabled": true
  }
}
```
For HTTP: `"type": "remote", "url": "..."`. Env vars: `"environment": {"KEY": "VALUE"}`. Read the config with python `json` (it's usually plain JSON despite the .jsonc extension) and write back.

### 5. Verify

- `hermes mcp list` → server shows `all / enabled`
- `opencode mcp list` → `✓ <name> connected`
- Live proof: `opencode run "List the MCP tools named <prefix>_* available to you" --pure` (uses the configured provider)
- Or the E2E client script from step 2

### 6. Activate (Hermes needs a restart — no hot reload)

- WebUI-hosted agent: `sudo systemctl restart app-hermes-webui.service`
- Telegram/other platforms: `systemctl --user restart hermes-gateway.service`
- Tool naming: Hermes = `mcp_<server>_<tool>` (hyphens → underscores); opencode = bare `<tool>` name

Restarting app-hermes-webui kills the current WebUI session mid-turn — do it as a final step and warn the user, or hand them the command.

## Verification

Success = tools visible in `hermes mcp list` AND `opencode mcp list`, and a live tool call returns a real result (not an error).

## Pitfalls

- `hermes mcp add` interactive prompt cancels in non-TTY → pipe `printf 'Y\n'`
- Newer `mcp` SDK dropped `mcp.server.fastmcp` → pin `<2.0.0` in PEP 723 deps
- Legacy list `mcp_servers` format breaks the CLI → migrate to dict
- Hermes strips subprocess env → pass API keys via `--env`
- config.yaml open in an editor → stale buffer clobber risk
- Model-backed tools need the model pulled first (`ollama pull <model>`) — they fail with a clean diagnostic otherwise
