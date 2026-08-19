# Headless Camoufox Debugging Log (2026-08-06 Session)

## Log Excerpt from Failed Run
```
2026-08-06 08:01:27,390 | INFO | Starting batch of 1 submissions

Starting batch of 1 submissions (current counter: 85)
Using Camoufox with anti-detection...

2026-08-06 08:01:27,391 | INFO | Starting Camoufox browser...
2026-08-06 08:01:27,391 | INFO | Buster extension already present at /home/aldo/scripts/form-automation/tmp/buster_firefox
2026-08-06 08:01:31,507 | INFO | Camoufox browser started with Buster extension

--- Submission 1/1 (counter: 85) ---
2026-08-06 08:01:34,513 | INFO | Form loaded
2026-08-06 08:01:40,485 | INFO | Submit clicked
2026-08-06 08:01:48,788 | INFO | Challenge detected
2026-08-06 08:01:48,843 | INFO | Clicking captcha plugin trigger button in frame
2026-08-06 08:01:52,776 | INFO | Running shadow DOM evaluate in bframe (attempt 1/20)...
2026-08-06 08:01:52,783 | INFO | Shadow DOM evaluate result: {'found': True, 'x': 102, 'y': 232, 'w': 48, 'h': 48}
2026-08-06 08:01:52,791 | INFO | Clicking Buster solver button at absolute position (721.0, 257.0)
2026-08-06 08:01:56,216 | INFO | Clicked Buster solver button in shadow DOM
2026-08-06 08:02:25,434 | INFO | Challenge solved but no confirmation yet, attempting submit again...
2026-08-06 08:02:42,648 | ERROR | Submission failed at counter 85
2026-08-06 08:02:43,016 | INFO | Browser closed
```

## Debugging Findings
- ✅ Buster extension loads correctly in headless Camoufox
- ✅ Shadow DOM evaluation successfully finds the solver button position
- ❌ CAPTCHA solved but final submission still fails (server-side validation)
- 🎯 Suspect: Form validation occurs **after** CAPTCHA completion
- 🎯 Suspect: Selector drift — DOM may change post-CAPTCHA (stale references)

## Recommendations for Next Test
1. Force explicit `--load-extension=` path for Buster
2. Add `time.sleep(2)` after `wait_for_challenge_solved()` 
3. Wait for confirmation selector (`div[aria-label='Submit success']`) before re-click
4. Verify selectors reload from `config.yaml` post-CAPTCHA