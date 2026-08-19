---
name: spec-kit-mcp
description: "Integrate spec-kit MCP servers into Hermes and OpenCode."
version: 1.0.0
license: MIT
tags: [spec-kit, mcp, mcp-server, anyicode, lsendel, hermes, opencode]
related_skills: [hermes-agent, opencode]
---

# Spec-Kit MCP Integration

**Trigger**: When the user wants to integrate the `spec-kit-mcp` server into Hermes or OpenCode for spec-driven development workflows.

**Related**: GitHub Spec-Kit (https://github.com/github/spec-kit) — the upstream spec-driven development methodology.

## Background

Two npm packages provide spec-kit MCP servers:
- `@anyicode/spec-kit-mcp` (v1.0.4) — **Pure TypeScript, works on ARM64** (Raspberry Pi, Apple Silicon, etc.)
- `@lsendel/spec-kit-mcp` (v0.1.1) — Rust binary, **linux-x64 only** (will not work on ARM64)

**Always use `@anyicode/spec-kit-mcp` on ARM64 devices.**

## Hermes Integration

Add the MCP server to `~/.hermes/config.yaml` under `mcp_servers`:

```yaml
mcp_servers:
  spec-kit:
    command: "npx"
    args:
      - -y
      - '@anyicode/spec-kit-mcp@latest'
    enabled: true
```

Then restart Hermes Agent. The tools become available as `mcp_spec_kit_*`.

**Better: use the CLI (preferred over manual config editing):**
```bash
hermes mcp add spec-kit --command npx --args -y @anyicode/spec-kit-mcp@latest --connect-timeout 90
```

**Verify connection:**
```bash
hermes mcp list
hermes mcp test spec-kit
```

## OpenCode Integration

Add to `~/.config/opencode/opencode.jsonc`:
```json
{
  "mcp": {
    "spec-kit": {
      "command": "npx",
      "args": ["-y", "@anyicode/spec-kit-mcp@latest"]
    }
  }
}
```

Then verify: `opencode mcp list`

## Available Tools

When connected, the following tools are available:
- `speckit_constitution` — Establish project principles
- `speckit_specify` — Describe what to build
- `speckit_plan` — Create a technical plan
- `speckit_tasks` — Generate task list
- `speckit_implement` — Execute implementation

## Pitfalls

1. **ARM64 incompatibility**: `@lsendel/spec-kit-mcp` requires a Rust binary that only builds for `linux-x64`. On ARM64 (Raspberry Pi, Apple Silicon), it will fail silently (no error, just no output). Use `@anyicode/spec-kit-mcp` instead.

2. **Config format**: `mcp_servers` in `~/.hermes/config.yaml` is a **dict** (server name → config), NOT a list with `name:` keys. A common mistake is writing:
   ```yaml
   mcp_servers:
     - name: spec-kit   # WRONG
       url: http://...
   ```
   The correct format is:
   ```yaml
   mcp_servers:
     spec-kit:          # CORRECT
       command: npx
       args: ["-y", "@anyicode/spec-kit-mcp@latest"]
   ```

3. **stdio vs HTTP**: `spec-kit-mcp` is a **stdio** server (stdin/stdout), not an HTTP server. Do NOT use `url:` — use `command: npx` with args.

4. **connect_timeout**: The first run of `npx @anyicode/spec-kit-mcp` can be slow (downloading the package). Set `--connect-timeout 90` when adding via CLI.

5. **Agent restart required**: MCP tools are discovered at Hermes Agent startup. After adding a server, restart the agent (or start a new session) for tools to appear.

## Spec-Kit CLI Prerequisites

The spec-kit server requires `specify-cli` to be installed:
```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

Without it, some commands may fail with "command not found: specify".

## Verification Script

To test if the server is running and tools are available:
```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test():
    params = StdioServerParameters(
        command="npx", args=["-y", "@anyicode/spec-kit-mcp@latest"]
    )
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print(f"Connected. {len(tools.tools)} tools:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description.splitlines()[0]}")

asyncio.run(test())
```
