# Pitfalls & Fixes — llm‑infra‑sync

## Bun / Node.js
- **Missing `bun`** – add `bun` sentry in `ansible/roles/tools/defaults/main.yml` and install via the tools role.
- **Bun not on PATH** – Bun installs to `~/.bun/bin/bun` — use the full path or add `~/.bun/bin` to `$PATH`.
- **Dashboard errors (`ReactSharedInternals`)** – Ink requires React 18. Install `react@^18.2.0` and `react-dom@^18.2.0` explicitly (`bun add react@18 react-dom@18`).
- **`Expected ">" but found "flexDirection"`** – JSX file must have `.tsx` extension, not `.ts`, for Bun to parse JSX.
- **Key‑generator UI fails with `MODULE_NOT_FOUND`** – run with `bun` not `node` (`bun run key-generator/server.ts`), because imports use `.ts` extensions.

## File system
- **File permissions** – ensure `credential-pool.json` is readable/writable by the user.
- **`credential-pool.json` missing** – create it with `echo '{"version":"1.0.0","providers":{}}' > credential-pool.json`.

## Python / Ansible (PEP 668)
- **`externally-managed-environment` error** – Debian/Raspberry Pi system pip is blocked. Always use a virtualenv:
  ```bash
  python3 -m venv /path/to/venv
  /path/to/venv/bin/pip install -e /path/to/repo
  ```
- **Ansible `pip` module needs `executable:`** – point it at the venv pip, not system pip.
- **Ansible tool sentry for pip‑installed tools** – the sentry command must point to the venv binary, e.g. `'/home/aldo/.local/spec-kit-venv/bin/specify --version'`.

## Key‑generator UI
- **Token protection** – set `KEYGEN_TOKEN` env var; the UI accepts the token via `x-api-token` header OR `?token=` query param.
- **Human‑verification** – the `human` checkbox must be ticked in the form body.

## Ansible integration
- **Tool sentry lifecycle** – adding a new tool requires 4 steps:
  1. Add sentry to `ansible/roles/tools/defaults/main.yml`
  2. Add install task(s) to `ansible/roles/tools/tasks/main.yml`
  3. Add PATH configuration (bashrc / fish config)
  4. (Optional) Add post‑install verification in the relevant role
- **PEP 668 workaround for Ansible** – use `pip` module with `executable:` pointing to a venv, or a `shell` task that manually creates a venv before pip-installing.
