# FollowUpReminder: Digest CC Recipients Pattern

## Context
In the FollowUpReminder project (AWV case follow-up), digests were only CC'ing the sender (Aldo). The user requested adding Lena De Smaele and Sandra Arco as CC recipients for digest emails, matching the escalation behavior.

## Implementation Pattern

### 1. Add `digestCc` to Watchlist Config
```javascript
WATCHLIST: [
  {
    address:         'mobiliteit@merelbeke-melle.be',
    escalateTo:      'hannah.gevers@merelbeke-melle.be',
    escalateCc:      ['klantendienst-awv@wegenenverkeer.be;Lena.De.Smaele@merelbeke-melle.be;Sandra.Arco@merelbeke-melle.be'],
    digestCc:        ['Lena.De.Smaele@merelbeke-melle.be', 'Sandra.Arco@merelbeke-melle.be'],  // NEW
    escalateSubject: 'Escalatie: herhaaldelijk onbeantwoorde AWV-meldingen',
  },
]
```

### 2. Update sendDigest to Use Entry Object
```javascript
// Call site - pass full entry object
if (doDigest && pending.length > 0) {
  sendDigest(entry, pending);  // was: sendDigest(entry.address, pending)
}

// Function signature - accepts entry, uses entry.digestCc
function sendDigest(entry, pending) {
  const cc = [CONFIG.MY_EMAIL, ...(entry.digestCc || [])].join(',');
  deliverEmail({
    to: entry.address,
    cc: cc,
    // ...
  });
}
```

## Key Points
- Uses array format for `digestCc` (consistent with future extensibility)
- Falls back to empty array if undefined (`entry.digestCc || []`)
- Maintains sender (CONFIG.MY_EMAIL) in CC by default
- Matches escalation CC pattern for consistency
- Validation passes with `npm run validate`