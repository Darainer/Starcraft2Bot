"""Example: only launch a large, healthy force; favor base defense."""

import json
import sys

context = json.load(sys.stdin)
state = context["situation"]
strategy, reason = "regroup", "Gather a healthy army"
if state["health_fraction"] < 0.6:
    strategy, reason = "retreat", "Wait for shields to recover"
elif state["base_threat"]:
    strategy, reason = "defend", "Defend threatened bases"
elif state["army_supply"] >= 50 and state["health_fraction"] >= 0.8:
    strategy, reason = "push", "Large healthy force ready"
print(json.dumps({"strategy": strategy, "reason": reason}))
