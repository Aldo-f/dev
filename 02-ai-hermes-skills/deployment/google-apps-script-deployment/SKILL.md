---
name: google-apps-script-deployment
description: Deploy Google Apps Script via clasp with OAuth setup.
version: 1.0.0
tags: [google-apps-script, deployment, clasp, oauth]
---

## Prerequisites

- Node.js and npm installed
- clasp CLI installed globally: `sudo npm install -g @google/clasp`
- Google Cloud project with Apps Script API enabled

## OAuth Configuration

1. Go to Google Cloud Console → **APIs & Services** → **Credentials**.
2. Create **OAuth 2.0 Desktop App** client ID.
3. Add authorized redirect URIs:
   - ✅ `http://192.168.0.5` (your server IP)
   - ❌ Remove `localhost` entries (causes deployment failures on headless servers)
4. Download credentials JSON and place it in `~/.clasprc.json` (clasp handles this automatically via `clasp login`).

## Authentication

```bash
# Authenticate clasp (opens browser)
clasp login

# Verify authentication
clasp whoami
```

## Deployment Workflow

1. Validate scripts:
   ```bash
   npm run validate
   ```

2. Push FollowUpReminder:
   ```bash
   npm run push:followup
   # OR: cd FollowUpReminder && clasp push --force
   ```

2. Push LabelReminder:
   ```bash
   npm run push:label
   # OR: cd LabelReminder && clasp push --force
   ```

## Pitfalls

- **Redirect URI mismatch**: Using `localhost` instead of `http://192.168.0.5` will cause OAuth failures.
- **Missing clasp global install**: `sudo npm install -g @google/clasp` required before use.
- **Authentication timeout**: Re-authenticate with `clasp login` if you see "No credentials found".
- **Background execution**: Deployment must be run in a terminal; headless script execution may fail without a PTY.
- **Headless Setup**: Use `clasp login` globally, NOT per-project. The browser login URL is accessible from any machine on the network.
- **Function signature changes**: When modifying function signatures, update BOTH the definition AND all call sites. Use `grep -n "functionName" Code.gs` to find both.
- **Directory naming**: Use `06-apps-<name>` for user-facing apps (group 06), not `02-ai-<name>` (group 02 is for AI services). The prefix determines deploy target.
- **File corruption risk**: When modifying `.gs` files, use `git checkout` to restore if the file becomes truncated or corrupted.
- **Push order**: Update `.clasp.json` `filePushOrder` when adding new `.gs` files, or they won't be deployed.
- **State-based vs History-based Counters**: Tracking reminder counts via stateful databases (e.g. `PropertiesService`) is fragile because manual user replies bypass the script. Instead, parse actual thread history—counting existing "Re:" emails sent by your address in the thread.
- **Prone to "We" instead of "Ik"**: When generating emails for an individual, explicitly instruct the AI to write using "ik" (I) rather than "we" (we).
- **Draft Truncation / Incompleteness**: Ensure model output is not truncated mid-sentence. Add specific prompt constraints asking for complete email bodies and avoid markdown/bold formatting which may look corrupted in raw email clients. Always include clear context about the original issue (e.g. location, issue description) so the recipient knows what is being referenced.
- **NaN/Undefined Guards**: Command-line runners like `clasp run` can pass parameters as `NaN` or unexpected types. Always use robust type guards (e.g. `Number.isFinite(num)`) instead of simple truthiness when setting default execution parameters.
- **Unused Scopes Cause Auth Warnings**: `appsscript.json` with unused/over-privileged scopes (e.g. `https://www.googleapis.com/auth/keep.readonly` when Keep isn't used) triggers "Some requested scopes cannot be shown" warnings. Prune scopes to only those actually used by the script.
- **clasp run Requires Custom OAuth for Gmail Scopes**: `clasp run` uses clasp's own OAuth client which lacks Gmail scopes. For functions that call Gmail APIs, you must either: (a) create a custom OAuth Desktop App client with Gmail scopes and run `clasp login --creds /path/to/credentials.json`, or (b) test via the web editor instead. The web editor uses the script's own OAuth context which has the required scopes.
- **Global Limit vs Per-Label Limit Bug**: When enforcing a maximum reminder count across multiple labels, use a single global counter (`totalSent`) that increments inside the thread loop, NOT a per-label counter that gets added again after the label loop (which double-counts). Check the global limit before processing each thread and break out of all label processing when reached.
- **Dry Run Default Parameter Bug**: When `clasp run dryRunWithMax` is called without arguments, the parameter arrives as `NaN` (not `undefined`). Use `typeof maxReminders === 'number' && Number.isFinite(maxReminders) && maxReminders >= 1 ? maxReminders : 3` to properly default to 3.

## Dynamic Tone/Irritation Ladder Pattern

When generating reminder emails that need increasing assertiveness over time:

1. **Add `elapsedDays` parameter** to the text generation function
2. **Implement tone thresholds**:
   - 1-14 days: Friendly/Professional (🟢)
   - 15-28 days: Firm/Urgent (🟡)
   - 29+ days: Very Urgent/Safety Concern (🔴)
3. **Extract dossier numbers** from message body using regex (e.g., `KM-\d{4}-\d{5}`)
4. **Create comprehensive test files** with 24 examples (one per day) to verify tone progression

Example implementation in `Code.gs`:
```javascript
function generateReminderText(originalSubject, originalSnippet, senderName, lang, elapsedDays) {
  let tone = 'kort, vriendelijk en professioneel';
  if (elapsedDays > 28) {
    tone = 'zeer dringend, vastberaden en bezorgd over de veiligheid';
  } else if (elapsedDays > 14) {
    tone = 'zakelijk, vastberaden en wijzend op het veiligheidsrisico';
  }
  // ... build prompt with tone
}
```

## Support Files

- `references/google-apps-script-manual-setup.md`: Detailed step-by-step OAuth configuration guide.
- `scripts/validate-google-auth.sh`: Validates clasp authentication status.
- `templates/test-irritation-ladder.gs`: Template for creating 24-tone test files showing irritation ladder progression.
- `templates/test-irritation-ladder.gs`: Template for creating 24-tone test files.