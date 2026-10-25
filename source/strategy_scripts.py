"""Run a local strategy script with JSON input/output and a bounded wait."""

import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

from source.assistant_control import STRATEGIES


def run_strategy_script(path, context):
    script = Path(path).resolve(strict=True)
    if script.suffix != ".py":
        raise ValueError("Strategy script must be a Python file")
    digest = hashlib.sha256(script.read_bytes()).hexdigest()
    result = subprocess.run(
        [sys.executable, "-I", str(script)],
        input=json.dumps(context),
        text=True,
        capture_output=True,
        timeout=1,
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    plan = json.loads(result.stdout)
    if not isinstance(plan, dict) or set(plan) - {"strategy", "reason", "target"}:
        raise ValueError("Script must return a plan object with strategy, reason and optional target")
    if plan.get("strategy") not in STRATEGIES[1:]:
        raise ValueError("Script must select defend, regroup, push or retreat")
    if not isinstance(plan.get("reason"), str) or len(plan["reason"]) > 500:
        raise ValueError("Script reason must be a string of at most 500 characters")
    if "target" in plan:
        target = plan["target"]
        if (
            not isinstance(target, list)
            or len(target) != 2
            or any(type(v) not in (int, float) or not math.isfinite(v) for v in target)
        ):
            raise ValueError("Script target must contain two finite coordinates")
    return {**plan, "script_sha256": digest, "script": str(script)}
