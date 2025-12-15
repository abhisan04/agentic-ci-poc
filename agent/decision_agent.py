import os
import sys

signal = os.getenv("AGENT_SIGNAL", "pass")

print(f"[Agent] Input signal = {signal}")

if signal == "fail":
    print("[Agent] Decision = STOP ❌")
    sys.exit(1)
else:
    print("[Agent] Decision = CONTINUE ✅")
    sys.exit(0)
