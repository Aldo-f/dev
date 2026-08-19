# Spec-Kit MCP Integration Reference

## ARM64 Compatibility

| Package | Backend | ARM64 Support | Status |
|---------|---------|---------------|--------|
| `@anyicode/spec-kit-mcp` | Pure TypeScript | ✅ Yes | **Use this on Pi** |
| `@lsendel/spec-kit-mcp` | Rust binary | ❌ linux-x64 only | Will fail silently on ARM64 |

## Connection Test

Run this to verify the server is working:

```bash
hermes mcp test spec-kit
```

Expected output:
```
✓ Connected! Found 5 tool(s) from 'spec-kit':
  - speckit_constitution  Establish project principles
  - speckit_specify       Describe what to build
  - speckit_plan          Create a technical plan
  - speckit_tasks         Generate task list
  - speckit_implement     Execute implementation
```

## Hermes Config Format (Correct vs Wrong)

**Correct** (dict format):
```yaml
mcp_servers:
  spec-kit:
    command: "npx"
    args:
      - -y
      - '@anyicode/spec-kit-mcp@latest'
    enabled: true
```

**Wrong** (list format with name keys):
```yaml
mcp_servers:
  - name: spec-kit     # This is WRONG - won't work
    url: http://...
```

## Tool Naming

Tools are prefixed with `mcp_spec_kit_` in Hermes:
- `mcp_spec_kit_speckit_constitution`
- `mcp_spec_kit_speckit_specify`
- `mcp_spec_kit_speckit_plan`
- `mcp_spec_kit_speckit_tasks`
- `mcp_spec_kit_speckit_implement`

## First-Run Download

The first time you use `npx @anyicode/spec-kit-mcp`, it downloads the package. This can take 30-60 seconds. If you get a timeout, increase `connect_timeout` to 90 or 120.

## Spec-Kit CLI Setup

The spec-kit tools use the `specify` CLI internally. If you get "command not found: specify" errors, install it:

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

## Known Issues

1. **Empty response**: If the server returns no output, check if it's the wrong package (`@lsendel` vs `@anyicode`).
2. **Timeout on first run**: Increase `connect_timeout` or wait longer for npm download.
3. **Tools not appearing**: Restart Hermes after adding the server.
