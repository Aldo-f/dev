# Key‑generator UI guide

## Starting the UI
```bash
# Protect the UI with a token (recommended)
KEYGEN_TOKEN=secret bun run key-generator/server.ts
```
The UI listens on **port 3004** (configurable via `PORT` env var) and presents a simple HTML form to add a new API key. The form includes:
- Provider dropdown (OpenRouter, Gemini, xAI)
- Label (key identifier)
- API Key textarea
- Human‑verification checkbox (must be ticked)

## Authentication
The UI is protected by `KEYGEN_TOKEN` if set. The token can be passed:
- Via `x-api-token` header
- Via `?token=` query parameter (for browser access): `http://localhost:3004/keys/new?token=secret`

## Adding a key via the UI
1. Open `http://localhost:3004/keys/new` in a browser.
2. Fill the form and tick "I am human".
3. Click **Create**.

## Adding a key via curl
```bash
curl -X POST http://localhost:3004/keys/create \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'provider=openrouter&label=my-key&key=sk-or-abc123&human=on'
```

## What happens on submit
1. The server writes the key to all relevant source files (Hermes, OpenCode, Omniroute, Freellmapi `.env`).
2. It triggers an immediate background sync. The new key will appear in the central pool and all downstream sources.

## Security notes
- The UI writes directly to files; protect it with a secret token in production.
- The `human` checkbox is a confirmation gate, not a CAPTCHA — it prevents accidental submissions.
- For stronger human verification, add a reCAPTCHA widget by embedding the Google reCAPTCHA script in the form.
