"""Test-shell hygiene: drop bracketed-IPv6 no_proxy entries so the
x402 SDK's httpx client doesn't die parsing them (see app/main.py —
the same scrub runs in production code; tests boot the app in
shells whose proxy config is not what the suite is testing)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

for _var in ("no_proxy", "NO_PROXY"):
    _val = os.environ.get(_var)
    if _val:
        _kept = [e for e in _val.split(",") if "[" not in e and "]" not in e]
        os.environ[_var] = ",".join(_kept)

# App settings are read at import time, so test env must be set HERE
# (conftest loads before any test module imports the app) — setting
# it inside a test module loses to whichever module imports first.
os.environ.setdefault("X402_PAY_TO", "0x097f9685D1e0752bF8B02d61E5Ce9be7eA0FBA7F")
os.environ.setdefault("STALL_DB_PATH", "/tmp/stall-template-test.db")
