"""Example: defend a raid, then counterattack once the raid is gone."""

import json
import sys

context = json.load(sys.stdin)
state = context["situation"]
strategy, reason = "regroup", "Hold reserves until an opportunity appears"
if state["health_fraction"] < 0.4 or state["nearby_enemy_strength"] > state["own_strength"] * 1.4:
    strategy, reason = "retreat", "Unfavorable local engagement"
elif state["base_threat"]:
    strategy, reason = "defend", "Intercept the visible raid"
elif context["previous_strategy"] in ("defend", "push") and state["army_supply"] >= 14:
    strategy, reason = "push", "Counterattack after holding the raid"
print(json.dumps({"strategy": strategy, "reason": reason}))
