"""Example: attack at 6 minutes with 20 army supply; protect home first."""

import json
import sys

context = json.load(sys.stdin)
state = context["situation"]
observation = (context.get("observation") or {}).get("observation", {})
seconds = observation.get("game_loop", 0) / 22.4
strategy, reason = "regroup", "Assemble for the six-minute timing"
if state["health_fraction"] < 0.35:
    strategy, reason = "retreat", "Preserve the damaged army"
elif state["base_threat"]:
    strategy, reason = "defend", "Protect the bases before the timing"
elif seconds >= 360 and state["army_supply"] >= 20:
    strategy, reason = "push", "Six-minute army timing reached"
print(json.dumps({"strategy": strategy, "reason": reason}))
