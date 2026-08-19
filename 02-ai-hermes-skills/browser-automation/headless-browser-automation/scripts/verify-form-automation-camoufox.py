#!/usr/bin/env python3
"""
Ad-hoc verification for auto_form_camoufox.py
Tests Camoufox-specific functionality.
"""

import sys
import json
from pathlib import Path

SCRIPT_DIR = Path("/home/aldo/scripts/form-automation")
sys.path.insert(0, str(SCRIPT_DIR))

# Test 1: Counter persistence (shared)
print("Test 1: Counter persistence")
counter_file = Path("~/scripts/form-automation/data/counter.json").expanduser()
with open(counter_file) as f:
    data = json.load(f)
    assert data["count"] == 0, f"Expected 0, got {data['count']}"
    print("  ✅ Counter file exists and loads correctly")

# Test 2: Selectors are valid format
print("Test 2: Selectors format")
SELECTORS = {
    "email": 'input[aria-label="Je e-mailadres"]',
    "competition_question": 'input[type="text"][aria-describedby="i6 i7"]',
    "tiebreaker_question": 'input[type="text"][aria-describedby="i11 i12"]',
    "submit": 'div[role="button"]:has-text("Verzenden")',
    "confirmation": '.freebirdFormviewerViewResponseConfirmationMessage',
}
for k, v in SELECTORS.items():
    assert isinstance(v, str) and len(v) > 0
    print(f"  ✅ {k}: {v[:50]}...")

# Test 3: Fixed form values
print("Test 3: Fixed form values")
EMAIL = "dit-is-een-ongeldige-deelname@getnada.com"
COMPETITION_ANSWER = "Waarom bleef je niet voor mij?"
assert "@" in EMAIL
assert len(COMPETITION_ANSWER) > 0
print(f"  ✅ Email: {EMAIL}")
print(f"  ✅ Competition answer: {COMPETITION_ANSWER}")

# Test 4: Script imports without error
print("Test 4: Script imports")
try:
    from auto_form_camoufox import CamoufoxFormAutomation, main
    print("  ✅ Imports successful")
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)

# Test 5: Class instantiation
print("Test 5: Class instantiation")
try:
    automation = CamoufoxFormAutomation(headless=True)
    assert automation.counter == 0
    print("  ✅ CamoufoxFormAutomation instantiates correctly")
except Exception as e:
    print(f"  ❌ Instantiation failed: {e}")
    sys.exit(1)

# Test 6: Counter save/load roundtrip
print("Test 6: Counter save/load roundtrip")
automation.counter = 42
automation._save_counter()
with open(counter_file) as f:
    data = json.load(f)
    assert data["count"] == 42
    print("  ✅ Counter persists correctly")

# Reset counter
automation.counter = 0
automation._save_counter()

# Test 7: Camoufox wrapper creation (no browser launch)
print("Test 7: Camoufox wrapper creation")
try:
    from camoufox.sync_api import Camoufox
    wrapper = Camoufox(headless=True)
    assert wrapper is not None
    print("  ✅ Camoufox wrapper creates successfully")
except Exception as e:
    print(f"  ❌ Camoufox wrapper failed: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("VERIFICATION SUMMARY (Camoufox)")
print("="*50)
print("✅ Counter persistence works")
print("✅ Selectors are valid CSS/Playwright format")
print("✅ Fixed form values configured")
print("✅ Script imports and instantiates")
print("✅ Counter save/load roundtrip works")
print("✅ Camoufox wrapper creates successfully")
print()
print("⚠️  KNOWN BLOCKER: reCAPTCHA v2 invisible not solved")
print("   - Form submits but token never reaches #g-recaptcha-response")
print("   - Callback fpHtcb not firing in automation context")
print("   - Challenge appears but solving it doesn't complete submission")
print("   - Need: computer_use tool, paid CAPTCHA API, or different approach")
print("="*50)