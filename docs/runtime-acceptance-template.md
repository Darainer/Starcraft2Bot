# Windows shared-control acceptance record

Status: **NOT TESTED** (replace only after observing the checks below).

- Test date/time:
- Tester (human / agent with desktop access / human-reported to agent):
- Windows version:
- Git commit (`git rev-parse HEAD`):
- Exact startup command:
- Startup mode (launch / attach):
- SC2 installation path:
- Actual `ping.game_version`:
- Actual `ping.base_build`:
- Actual `ping.data_build`:
- Actual `ping.data_version`:
- Python / burnysc2 / pys2clientprotocol / protobuf versions:
- Map path and SHA-256 (from runtime JSON):
- Runtime JSON path:
- Log path:
- Replay path (or reason missing):

Use PASS, FAIL or NOT TESTED. Record what happened, not just expected behavior.

| Check | Result | Observed evidence / failure |
| --- | --- | --- |
| Probe returns selected binary/data identity | NOT TESTED | |
| Local real-time match loads | NOT TESTED | |
| Manual worker select/move/gather while paused | NOT TESTED | |
| Minimap clicks move camera | NOT TESTED | |
| Command-card button trains unit | NOT TESTED | |
| Hotkey trains unit | NOT TESTED | |
| Control group assignment and recall | NOT TESTED | |
| Camera and drag selection work | NOT TESTED | |
| Local chat !assist status replies PAUSED | NOT TESTED | |
| !assist resume enables actual economy actions | NOT TESTED | |
| Human selection/camera retained while bot acts | NOT TESTED | |
| Human army move/attack while economy runs | NOT TESTED | |
| !assist pause stops new automation | NOT TESTED | |
| Match ends / replay saved / expected process cleanup | NOT TESTED | |

Shared-control verdict: NOT VERIFIED.

Optional ability/ownership acceptance: use docs/assistant-live-test.md and record
each enabled feature separately. Do not claim Storm/Feedback/Blink compatibility
from an economy-only test. Record action errors, resources/research and targets.

This record applies only to the tested binary/data identity, map, dependency lock
and source revision. A failed/untested row prevents a full shared-control pass.
Keep the runtime JSON unchanged; it deliberately does not certify manual input.
