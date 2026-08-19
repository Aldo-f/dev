---
name: jest-setup
description: "Configure Jest setup files correctly, avoid ES exports."
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Jest Setup (Class-Level Skill)

## When to use
Apply this skill whenever configuring Jest `setupFilesAfterEnv` or `setupFiles` for a project that runs in a CommonJS environment (default for most Node.js projects). It resolves errors like:
```
SyntaxError: Unexpected token 'export'
```
which occur when an ES6 `export` statement is present in a setup file that Jest treats as CommonJS.

## Core Pitfall
- **Never include `export` statements in Jest setup files** (`setupFilesAfterEnv`, `setupFiles`). Jest loads these files with CommonJS semantics. Having `export {}` or any `export` causes a syntax error and aborts the test run.
- Use plain `require` statements and assign globals directly. If you need to expose helpers, attach them to `global` rather than exporting.

## Additional notes for ESM projects
- If your project is an ES module (`type: "module"` in `package.json`), keep the Jest setup file as CommonJS by naming it with a `.cjs` extension and referencing it in `jest.config.cjs`.
- Ensure `jest.config.js` (or `jest.config.cjs`) uses `module.exports = { … }` for CommonJS or `export default { … }` for ESM, but the `setupFilesAfterEnv` entry must point to the CommonJS file.
- Do not add `export` statements in the setup file even when the rest of the codebase uses ESM.
- **Never include `export` statements in Jest setup files** (`setupFilesAfterEnv`, `setupFiles`). Jest loads these files with CommonJS semantics. Having `export {}` or any `export` causes a syntax error and aborts the test run.
- Use plain `require` statements and assign globals directly. If you need to expose helpers, attach them to `global` rather than exporting.

### Example of a correct CommonJS setup file
```js
// jest.setup.js (CommonJS)
require('fake-indexeddb/auto');
const { TextEncoder, TextDecoder } = require('util');
const { webcrypto } = require('crypto');

if (typeof global.TextEncoder === 'undefined') {
  global.TextEncoder = TextEncoder;
}
if (typeof global.TextDecoder === 'undefined') {
  global.TextDecoder = TextDecoder;
}
if (typeof global.crypto === 'undefined' || !global.crypto.subtle) {
  Object.defineProperty(global, 'crypto', { value: webcrypto, writable: true, configurable: true });
}
// No `export` statements!
```

## How to configure Jest
In `jest.config.js` (or `jest.config.cjs` for clarity):
```js
/** @type {import('jest').Config} */
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['./jest.setup.js'], // path to the CommonJS file above
  // other config …
};
```
If your project uses ES modules (`type: "module"` in `package.json`), you can still keep the Jest setup file as CommonJS by naming it with a `.cjs` extension and referencing it accordingly.

## Verification checklist
- [ ] The setup file ends **without any `export` statements**.
- [ ] Jest runs `npm test` (or `pnpm test`) without a syntax error.
- [ ] Global polyfills (e.g., `fetch`, `TextEncoder`) are available in test files.
- [ ] All existing tests pass after adding the setup file.

## References
- Playwright docs (if using Playwright with Jest): https://playwright.dev/docs/test-configuration
