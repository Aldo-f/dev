# FollowUpReminder: AI Fallback Pattern for Digests

## Context
The `sendDigest` function was using `composeBody()` which calls `rewriteProse()` → AI waterfall (Gemini → FreeLLMAPI → OpenRouter). The AI was hallucinating incorrect salutations:
- "Geachte medewerker van AWV" (wrong - recipients are municipality staff, not AWV)
- "Beste medewerkers van AWV" (wrong, same issue)
- Producing broken/duplicate output (restarting with another salutation mid-email)

## Fix: Use Deterministic Fallback Template

### Before (AI-dependent, broken):
```javascript
function sendDigest(entry, pending) {
  const overview = buildGroupedOverview(pending);
  const body = composeBody(
    'Geachte,\n\nHierbij een overzicht...',
    overview,
    'Mag ik u verzoeken...\n\nMet vriendelijke groeten,\nAldo Fieuw'
  );
  // ...
}
```

### After (deterministic, correct):
```javascript
function sendDigest(entry, pending) {
  const body = buildFallbackDigest(pending);
  // ...
}
```

### The Fallback Template (`buildFallbackDigest`):
```javascript
function buildFallbackDigest(pending) {
  return [
    'Geachte,',
    '',
    'Hierbij een overzicht van de meldingen die ik via AWV aan uw dienst doorzond',
    'en waarop ik tot op heden nog geen reactie of statusupdate ontving:',
    '',
    buildGroupedOverview(pending),
    '',
    'Mag ik u verzoeken de openstaande dossiers op te volgen',
    'en mij per dossier op de hoogte te stellen van de huidige status?',
    '',
    'Met vriendelijke groeten,',
    'Aldo Fieuw',
  ].join('\n');
}
```

## Key Points
- **No AI involved** — consistent, correct output every time
- **Correct salutation**: "Geachte," (neutral, addresses municipality staff properly)
- **Uses existing `buildGroupedOverview`** for the grouped-by-date listing
- **Proper closing**: references open dossiers, polite request, standard sign-off
- Escalation emails (`sendEscalation`) correctly use their own template (`buildEscalationBody`) which addresses the service head directly — no change needed there

## When to Use This Pattern
- Any user-facing email where AI hallucinations have caused issues
- When deterministic, legally/operationally safe output is required
- When the template is simple enough that AI adds no value

## Validation
Run `npm run validate` to ensure syntax and function checks pass.