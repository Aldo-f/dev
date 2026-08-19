# LLM Infra Sync Session Learnings - Detailed Debugging & Solutions

## Context of this Session
This document details the key learnings, debugging steps, and solutions identified during the implementation and troubleshooting of the `02-ai-llm-infra-sync` dashboard. The goal was to build a self-contained Hono/Bun web dashboard with a JSON API, programmatic system management (cron, files, credentials), client-side interactivity, Tailwind CSS for styling, and ensure robust, self-restarting deployment via systemd.

## 1. Systemd Service Integration for Bun Applications

### Problem
Ensuring the Bun-based LLM Infra Sync dashboard starts automatically on system reboot and restarts gracefully after crashes. Initial attempts resulted in manual intervention and `status=203/EXEC` errors.

### Solution & Workflow
1.  **Systemd Service File Creation**:
    *   Created `templates/systemd/app-llm-infra-sync.service` within `01-core-infra`.
    *   **User Preference**: Named it `app-llm-infra-sync.service` to follow the user's convention for custom services.
    *   **Content (Key Parts)**:
        ```ini
        [Unit]
        Description=LLM Infra Sync Dashboard & API Server
        After=network.target
        Wants=network-online.target

        [Service]
        Type=simple
        User=aldo
        WorkingDirectory=/home/aldo/dev/02-ai-llm-infra-sync
        ExecStart=/home/aldo/.bun/bin/bun run src/server.ts  # Full path to bun binary
        Restart=always
        RestartSec=10
        Environment=NODE_ENV=production
        Environment=PORT=3003
        StandardOutput=journal
        StandardError=journal

        # Security hardening (essential for production)
        NoNewPrivileges=true
        PrivateTmp=true
        ProtectSystem=strict
        ProtectHome=true
        LimitNOFILE=65536
        LimitNPROC=4096
        SyslogIdentifier=llm-infra-sync

        [Install]
        WantedBy=multi-user.target
        ```
2.  **Ansible Integration (`01-core-infra/ansible/roles/systemd/tasks/main.yml`)**:
    *   Added a task to deploy this service file:
        ```yaml
        - name: Deploy LLM Infra Sync systemd service
          copy:
            src: "{{ systemd_template_dir }}/app-llm-infra-sync.service"
            dest: "/etc/systemd/system/app-llm-infra-sync.service" # Renamed to follow app- convention
            owner: root
            group: root
            mode: 0644
          notify: Reload systemd # Important: ensure systemd reloads after changes

        - name: Enable and start LLM Infra Sync service
          systemd:
            name: app-llm-infra-sync # Use the new service name
            enabled: true
            state: started
        ```
3.  **Deployment & Verification**:
    *   Ran `cd /home/aldo/dev/01-core-infra && ./install.sh` to trigger Ansible.
    *   Manual verification:
        ```bash
        sudo systemctl daemon-reload
        sudo systemctl enable app-llm-infra-sync
        sudo systemctl start app-llm-infra-sync
        sudo systemctl status app-llm-infra-sync
        ```

### Pitfall: `status=203/EXEC`
*   **Cause**: Often indicates that the `ExecStart` command in the service file cannot be found or executed.
*   **Debugging**: Verify the full path to the executable (`/home/aldo/.bun/bin/bun`) and the script (`/home/aldo/dev/02-ai-llm-infra-sync/src/server.ts`). Ensure permissions are correct.

## 2. Bun/TypeScript ESM Imports and Module Resolution

### Problem
Frequent `Cannot find module './src/index.js'` or similar errors when importing local TypeScript modules in a Bun environment.

### Solution
*   **Bun's ESM Convention**: Bun expects `.js` extensions for local imports even when importing `.ts` files, and relative paths need to be precise.
*   **Example Fixes in `src/server.ts`**:
    *   `import sync, { DEFAULT_SOURCES } from './index.js';` (from `../src/index.js`)
    *   `import { appendHistory, readHistory } from '../src/writers/history-writer.js';` (from `./src/writers/history-writer.js`)
    *   `import { renderDashboard } from './src/dashboard/html.js';` (was already correct, but this demonstrates the pattern)

## 3. Tailwind CSS Integration with Hono/Bun (No Build Step)

### Problem
Dashboard was unstyled or missing Tailwind classes despite `tailwindcss` being installed.

### Solution & Workflow
1.  **Dependencies**: Added `tailwindcss`, `postcss`, `autoprefixer` as `devDependencies` to `package.json`.
2.  **Configuration**: Created `tailwind.config.js` (specifying content paths like `./src/dashboard/**/*.ts`) and `postcss.config.js`.
3.  **Input CSS**: Created `src/dashboard/styles.css` with `@tailwind` directives.
4.  **Build Script**: Added `"tailwind-build": "node ./node_modules/tailwindcss/dist/lib.js -i ./src/dashboard/styles.css -o ./src/dashboard/dist/output.css --minify"` to `package.json`.
    *   **Pitfall**: `bunx tailwindcss` might fail if `bunx` isn't in `PATH` or due to execution restrictions. Explicitly calling `node ./node_modules/tailwindcss/dist/lib.js` is more robust.
5.  **Automated Build Hooks**: Added `"prestart": "bun run tailwind-build"` and `"pretest": "bun run tailwind-build"` to `package.json` for automatic CSS compilation.
6.  **Static File Serving**: In `src/server.ts`, added Hono's `serveStatic` middleware:
    ```typescript
    app.use('/static/*', serveStatic({ root: './src/dashboard/' }));
    ```
7.  **HTML Link**: Referenced the compiled CSS in `src/dashboard/html.ts`:
    ```html
    <link rel="stylesheet" href="/static/output.css" />
    ```

## 4. Dashboard HTML/JS Separation (SSR Best Practices)

### Problem
TypeScript compilation errors in `src/dashboard/html.ts` due to embedded client-side JavaScript.

### Solution & Workflow
1.  **Separation of Concerns**: Moved all interactive client-side JavaScript from `src/dashboard/html.ts` to a dedicated `src/dashboard/dashboard.js` file.
2.  **HTML Reference**: Updated `src/dashboard/html.ts` to link to the external JS file:
    ```html
    <script src="/static/dashboard.js"></script>
    ```
3.  **Client-Side JS Refinement**: Ensure the `dashboard.js` script correctly targets DOM elements and handles events, as its class names now come from Tailwind. Added more robust checks for `e.target instanceof HTMLButtonElement` and `target instanceof HTMLInputElement`.

### Pitfall: TypeScript `as` keyword in client-side JS
*   **Cause**: `as` keyword (TypeScript type assertion) used in plain JavaScript file (or template literal parsed as JS) results in `SyntaxError: Unexpected identifier 'as'`.
*   **Fix**: Remove type assertions or use JavaScript-native type checking (`instanceof`, `typeof`) where appropriate.

## 5. Robust Environment Variable Parsing (`readEnv`)

### Problem
The `readEnv` function in `src/index.ts` was not reliably identifying provider keys, especially `FREELLM_OPENROUTER_KEY`.

### Solution & Workflow
1.  **Corrected `DEFAULT_SOURCES` Path**: Fixed `02-ai-freellm` entry in `DEFAULT_SOURCES` from `dev/02-ai-freellm-api/.env` (non-existent) to `dev/02-ai-freellm/.env`.
2.  **Explicit Provider Mapping**: Refactored `readEnv` to use explicit `startsWith()` checks for known key prefixes, prioritizing specific `FREELLM_` variants.
    ```typescript
    if (lowerKey.startsWith('freellm_openrouter_key')) {
      provider = 'openrouter';
    } else if (lowerKey.startsWith('openrouter_key')) {
      provider = 'openrouter';
    }
    // ... similar for gemini, xai, and then a generic 'freellm_' fallback
    ```
3.  **Test-Driven Development (TDD)**: Added `tests/freellm-sync.test.ts` to specifically test `readEnv` parsing and `sync` integration for FreeLLM. Used `console.log` extensively during debugging to inspect intermediate `pool` contents.

## 6. Nextcloud User Management Issues (Unresolved Problem)

### Problem
Unable to recreate users in Nextcloud (`aldo`, `Lotte`) after deleting them from the Nextcloud interface, because their data directories (`/mnt/HDD1/nextcloud/data/<user>/`) still existed on the filesystem. Nextcloud's `occ user:add` command consistently failed with "Login is invalid because files already exist for this user".

### Diagnosis
*   Nextcloud maintains user information in its internal database. When a user is deleted via the UI, their entry is removed from the database, but their data directory on the filesystem is preserved.
*   Attempting to recreate a user with the same name results in a conflict: the database expects a fresh user, but the filesystem has existing data.
*   There's no straightforward `occ` command to "re-adopt" an existing data directory for a new user.

### Potential (Risky) Workarounds (Not Recommended Without Full Backups)
*   **Manual Data Directory Renaming**: Temporarily move/rename the user's data directory *before* attempting to recreate the user via `occ`. After recreation, manually move the data back and run `occ files:scan`. This is error-prone.
*   **Direct Database Manipulation**: Edit Nextcloud's database tables (`oc_users`, `oc_storages`) directly to create an entry for the user and link it to the existing data directory. **Extremely risky and not supported by Nextcloud.**

### Key Takeaway
This is a known, complex issue in Nextcloud. The safest approach for re-adding users with existing data is typically to:
1.  Ensure a full backup of the Nextcloud data directory and database.
2.  Delete the user from the UI (which preserves data).
3.  **Manually delete or rename** the corresponding user's data directory on the filesystem.
4.  Recreate the user via `occ user:add`.
5.  If data needs to be restored, move it into the *newly created* user's data directory and run `occ files:scan <username>`.

This highlights a significant usability challenge in Nextcloud's user management when dealing with pre-existing data.

## Files to Reference
- `src/server.ts` - Main Hono server, static file serving, API routes
- `src/index.ts` - Core sync logic, `readEnv` function, `DEFAULT_SOURCES`
- `src/dashboard/html.ts` - SSR HTML template with Tailwind classes
- `src/dashboard/dashboard.js` - All client-side interactivity
- `package.json` - Build scripts, dependencies (Tailwind)
- `templates/systemd/app-llm-infra-sync.service` - Systemd service template
- `ansible/roles/systemd/tasks/main.yml` - Ansible task for systemd service deployment
- `tests/freellm-sync.test.ts` - Specific test for FreeLLM API integration and `readEnv`
- `tests/dashboard.test.ts` - Tests for dashboard rendering, cron, history writer
- `tests/sync.test.ts` - Core sync logic tests, updated for isolated test directories
