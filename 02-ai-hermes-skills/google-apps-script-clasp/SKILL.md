---
name: google-apps-script-clasp
description: Deploy Google Apps Script with clasp CLI.
---

# Google Apps Script Deployment with clasp

Deploy and manage Google Apps Script projects using the clasp CLI.

## Quick Commands

```bash
# Authenticate globally (creates ~/.clasprc.json)
clasp login

# Push code to Google
clasp push --force

# View logs
clasp tail-logs --simplified

# Create version
clasp version "description"

# Deploy
clasp deploy --versionNumber N --description "name"
```

## Common Issues

### "Unable to run script function"
Requires browser authorization. Open in browser:
```bash
open "https://script.google.com/d/{scriptId}/edit"
```
Run `setup()` manually first to authorize permissions.

### Gemini quota exceeded
Falls back to FreeLLMAPI automatically. Check logs for `[AI] FreeLLMAPI success`.

### Error: Could not locate target object
Add try-catch around `label.getName()` calls:
```javascript
try {
  const name = label.getName();
  // ...
} catch (e) {
  log(`[WARN] Label error: ${e.message}`);
  return false;
}
```

## Irritation Ladder Pattern

### Reminder Count Tracking (Thread‑Based)
Do **NOT** use `PropertiesService` to keep track of reminder counts (as users might send manual emails outside the script, leading to incorrect counts). Instead, count the actual number of sent reminder replies within the thread:
```javascript
function getReminderCountFromThread(thread) {
  const messages = thread.getMessages();
  let count = 0;
  for (let i = 0; i < messages.length; i++) {
    const msg = messages[i];
    const from = msg.getFrom();
    const subject = msg.getSubject();
    if (from === CONFIG.MY_EMAIL && subject.startsWith('Re: ')) {
      count++;
    }
  }
  return count;
}
```

Tone based on reminder count AND days since first message:
- 0 reminders & <30 days: Friendly/Professional
- 1-2 reminders OR 30-60 days: Firm/Vigilant  
- 3+ reminders OR 60+ days: Urgent/Safety Concern

## Email Format Rules
- **No "we" pronouns**: Always use **"ik"** (I) as the sender is an individual, not an organization.
- No bold text (`**text**`)
- No markdown formatting
- No numbered lists with bold items
- Natural, professional language
- Include dossier number (e.g. `KM-YYYY-XXXXX`) and exact issue/location context if present in snippet

## Utility: dryRunWithMax()
To prevent flooding inboxes during testing, implement `dryRunWithMax()` with a robust numeric guard:
```javascript
function dryRunWithMax(maxReminders) {
  const prevDry = CONFIG.DRY_RUN;
  const prevDrafts = CONFIG.CREATE_DRAFTS;

  CONFIG.DRY_RUN = false;
  CONFIG.CREATE_DRAFTS = true;

  // Default to 3 if not a valid number (NaN/undefined). 0 allows unlimited.
  let limit;
  if (maxReminders === undefined) {
    limit = 3;
  } else {
    const num = Number(maxReminders);
    limit = Number.isFinite(num) ? num : 3;
  }
  const prevMax = CONFIG.MAX_REMINDERS;
  CONFIG.MAX_REMINDERS = limit;

  checkReminders();

  CONFIG.DRY_RUN = prevDry;
  CONFIG.CREATE_DRAFTS = prevDrafts;
  CONFIG.MAX_REMINDERS = prevMax;
}
```
In `checkReminders()`, check this limit globally to stop processing early.

## AI Waterfall Settings
- Primary: **`gemini-2.5-flash`** (latest free model)
- Secondary fallback: **FreeLLMAPI**
- Third fallback: **OpenRouter** (always default to `openrouter/free` instead of transient specific models)

## FollowUpReminder Patterns
- **Digest CC recipients**: See `references/followup-digest-cc-pattern.md` for adding CC recipients to digests (matching escalation behavior).
- **AI fallback for digests**: See `references/followup-ai-fallback-pattern.md` for replacing AI-dependent `composeBody()` with deterministic `buildFallbackDigest()` to avoid hallucinated salutations.

