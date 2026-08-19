# LabelReminder — Bugs & Fixes Reference

## NaN Default Parameter Bug (dryRunWithMax)

### Problem
When calling `clasp run dryRunWithMax` without arguments, the parameter arrives as `NaN` (not `undefined`). The original check:
```javascript
CONFIG.MAX_REMINDERS = maxReminders !== undefined ? maxReminders : 3;
```
Since `NaN !== undefined` is `true`, `CONFIG.MAX_REMINDERS` became `NaN`. Then `NaN > 0` evaluates to `false`, causing the limit check to pass silently → **ALL drafts created**.

### Fix
Use robust type guard:
```javascript
const limit = (typeof maxReminders === 'number' && Number.isFinite(maxReminders) && maxReminders >= 1)
  ? maxReminders
  : 3;
CONFIG.MAX_REMINDERS = limit;
```

### Pattern for all CLI-entry functions
```javascript
function myFunction(param) {
  const safeParam = (typeof param === 'number' && Number.isFinite(param) && param >= 1)
    ? param
    : DEFAULT_VALUE;
  // use safeParam
}
```

---

## Global Limit vs Per-Label Double-Count Bug

### Problem
In `checkReminders()`, the global counter `totalSent` was incremented in TWO places:
1. Inside `active.forEach(thread)`: `totalSent++`
2. After label loop: `totalSent += labelSent`

This caused double-counting. With 3 reminders in label 1: `totalSent` = 6 after label 1 loop → limit (3) reached → stops processing.

### Fix
Remove the post-loop addition:
```javascript
log(`[DONE] ${label.getName()}: ${labelSent} herinnering(en)`);
// totalSent already incremented inside active.forEach, do not double-add here
```

### Correct pattern
```javascript
let totalSent = 0;
labels.forEach(label => {
  let labelSent = 0;
  active.forEach(thread => {
    if (CONFIG.MAX_REMINDERS > 0 && totalSent >= CONFIG.MAX_REMINDERS) {
      log(`[LIMIT] Global max reminders (${CONFIG.MAX_REMINDERS}) reached, stopping.`);
      return;
    }
    // ... process thread ...
    labelSent++;
    totalSent++;  // SINGLE increment point
  });
  log(`[DONE] ${label.getName()}: ${labelSent} herinnering(en)`);
  // NO totalSent += labelSent here!
});
log(`[SUMMARY] Totaal: ${totalSent} herinnering(en) verwerkt`);
```

---

## Unused Scopes Auth Warning

### Problem
`appsscript.json` contained unused scopes (e.g. `https://www.googleapis.com/auth/keep.readonly`) causing "Some requested scopes cannot be shown" warning.

### Fix
Prune `appsscript.json` to only scopes actually used:
```json
{
  "oauthScopes": [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/script.external_request"
  ]
}
```

---

## clasp run Permission Issue

### Problem
`clasp run dryRunWithMax` fails with "Unable to run script function. Please make sure you have permission to run the script function."

### Root Cause
`clasp run` executes via the **Apps Script Execution API** using clasp's own OAuth client (from `~/.clasprc.json`). This client lacks Gmail scopes.

### Workarounds
1. **Test via web editor** (uses script's OAuth context with proper scopes) — RECOMMENDED
2. **Create custom OAuth Desktop App** with Gmail scopes, then:
   ```bash
   clasp login --creds /path/to/credentials.json
   clasp run dryRunWithMax
   ```

---

## Irritation Ladder Tone Pattern

### Implementation
```javascript
function getToneFromContext(reminderCount, firstMessageDate) {
  const elapsedDays = (new Date() - firstMessageDate) / 86400000;
  
  if (reminderCount >= 3 || elapsedDays > 28) {
    return 'zeer dringend, vastberaden en uitdrukkelijk bezorgd over de veiligheid. De situatie is al lang onopgelost en vormt een ernstig risico. Gebruik "ik" (niet "we") omdat jij als individu schrijft.';
  } else if (reminderCount >= 1 || elapsedDays > 14) {
    return 'zakelijk, vastberaden en wijzend op het veiligheidsrisico. Dit is geen eerste herinnering meer. Gebruik "ik" (niet "we") omdat jij als individu schrijft.';
  } else {
    return 'korte, vriendelijke herinneringsmail. Vraag beleefd of ze al de tijd hebben gehad om te antwoorden. Toon begrip, geen urgentie. Houd het kort en professioneel. Gebruik "ik" (niet "we") omdat jij als individu schrijft.';
  }
}
```

---

## Reminder Count from Thread History (not PropertiesService)

### Pattern
```javascript
function getReminderCountFromThread(thread) {
  const messages = thread.getMessages();
  let count = 0;
  const myEmail = CONFIG.MY_EMAIL;
  
  for (const msg of messages) {
    const from = msg.getFrom();
    const subject = msg.getSubject() || '';
    if (from.includes(myEmail) && subject.startsWith('Re:')) {
      count++;
    }
  }
  return count;
}
```

### Why
- Works regardless of how emails were sent (script, manual, other automation)
- No state to maintain or sync
- Self-healing: manual replies automatically counted

---

## Body Logging for Verification

### Pattern
```javascript
log(`[${CONFIG.CREATE_DRAFTS ? 'DRAFT' : 'SENT'}] (${method}) → ${recipient} | ${subject}`);
log(`Body: ${body.replace(/\n/g, ' ').substring(0, 150)}...`);
```

Allows reviewing generated email content in logs without opening Gmail.