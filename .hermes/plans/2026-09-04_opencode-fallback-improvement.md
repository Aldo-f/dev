# Plan: Improve opencode-rate-limit-fallback-multi (fork + publish + auto-config)

Source fork: https://github.com/StoreBoughtKibbles/opencode-rate-limit-fallback-multi (23 commits ahead of original)
Target dir: ~/dev/06-apps-opencode-rate-limit-fallback-multi

## 1. Fork & clone ✅
- Clone https://github.com/StoreBoughtKibbles/opencode-rate-limit-fallback-multi.git into ~/dev/06-apps-opencode-rate-limit-fallback-multi
- Add origin remote pointing to user's fork (e.g., github.com/user/opencode-rate-limit-fallback-multi)

## 2. Auto-config wizard (new feature) - UX: one command
On first install/run, auto-create config:
```bash
opencode-rate-limit-fallback-multi configure
```

**Wizard flow:**
1. Lists available providers from `opencode providers list`
2. Asks: _"Select fallback providers (comma-separated, Enter=use all):"_
3. Shows detected free models: `openrouter/free`, `poolside/laguna-s-2.1:free`, etc.
4. Asks: _"Configure fallback models now? (Y/n):"_
5. Writes `~/.config/opencode/rate-limit-fallback-multi.json` with:
```json
{
  "enabled": true,
  "fallbackModels": ["openrouter/free", "poolside/laguna-s-2.1:free"],
  "patterns": ["rate limit", "usage limit", "too many requests", "quota exceeded", "overloaded", "capacity exceeded"],
  "logging": true
}
```

**Auto-detection:** If no config exists, defaults to `["openrouter/free"]` with logging: true

## 3. Publish package
- Update package.json: correct repo URL, author, name `opencode-rate-limit-fallback-multi`
- Publish to npm
- Ready for: `opencode plugin install opencode-rate-limit-fallback-multi`

## 4. Plugin improvements
- Add `configure()` helper that reads `opencode providers list`
- Generate sensible defaults when no config exists
- Ensure `logging: true` is default
- Support local development mode via file:// URL

## 5. Verification
- `npm pack` produces valid tarball
- `opencode plugin install` resolves from npm
- Local dev: `"plugin": ["file:///path/to/opencode-rate-limit-fallback-multi/index.ts"]`
- Test: `opencode run --model freellm/auto` → fallback to `openrouter/free` on rate limit
- Log file: `~/.local/share/opencode/logs/rate-limit-fallback.log` contains structured entries

## Config format (auto-generated default)
File: `~/.config/opencode/rate-limit-fallback-multi.json`
```json
{"enabled":true,"fallbackModels":["openrouter/free"],"patterns":["rate limit","usage limit","too many requests","quota exceeded","overloaded","capacity exceeded"],"logging":true}
```

## UX for new users
```bash
# Install
opencode plugin install opencode-rate-limit-fallback-multi

# First run - config auto-created, or:
opencode-rate-limit-fallback-multi configure

# View logs
cat ~/.local/share/opencode/logs/rate-limit-fallback.log
```