# Scout-driven Zerg response experiment

The candidate combines the R2 baseline that won Zerg Macro with the early
Robotics investment that won Zerg Timing. It does not select an entire historical
revision or read the configured computer build. Terran and Protoss retain the
baseline spending path. This is an experimental branch, separate from the
accepted hardcoded baseline.

## Opposition and historical evidence

All three R2 Macro victories and all three RoboticsV2 Timing victories were
audited against both the runtime report and saved game-info computer player:
each used **VeryHard**, protocol difficulty 7. Blizzard's
[official difficulty enum](https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto)
places only CheatVision, CheatMoney and CheatInsane above it. This meets the
highest non-cheating built-in difficulty benchmark; it does not establish elite
community-bot or human strength. That remains a separate milestone gate.
The [six-game audit](experiments/2026-10-31/zerg-winners-difficulty-audit.json)
retains runtime/game-info difficulty, fingerprints, bounds and binary identity.

| Frozen source | Macro | Timing | Interpretation |
| --- | --- | --- | --- |
| R2 | 3 victories, 1055.4 s each | 3 defeats, 1205.4 s each at the extended bound | Economic/combat baseline |
| RoboticsV2 | 3 defeats, 840.4 s each | 3 victories, 1050.4 s each | Earlier first Robotics investment helps Timing but hurts Macro |

R2 Macro used the original 1500-second bound and finished before it. Its outcome
is resolved; the new candidate uses 3600 seconds. R2 Timing and RoboticsV2 Timing
were evaluated at 3600 seconds. Original censored results remain separate.
See the [R2 report](evaluations/2026-10-31-production-v5-r2-complete.md),
[extended R2 Timing report](evaluations/2026-10-31-production-v5-r2-20261031-limit3600-zerg-timing.md),
and [RoboticsV2 report](evaluations/2026-10-31-robotics-fund-v2-20261031-complete.md).

## Observable selection

The existing Probe saw a Pool at approximately 45.4 seconds in every audited
Timing run, with build progress about 0.10. This is the first positive sighting,
not completion or an inferred construction start. Macro had no sampled Pool
sighting through 240 seconds. Incomplete scouting is not evidence that a Pool
does not exist, and does not establish a Macro strategy.

The selector uses only positive, timestamped observations:

- Fresh Roach/Ravager contacts totaling at least 4 supply select early Robotics
  through 360 seconds, with individual contact freshness of 45 seconds.
- A Warren first seen by 210 seconds can support early Robotics through 240
  seconds; its last observation expires after 90 seconds.
- A Pool first seen by 90 seconds supports a weaker, bounded early Robotics
  investment through 240 seconds; the last observation expires after 180 seconds.
- A positively observed expansion by 150 seconds overrides the weak Pool signal
  while fresh. Strong Roach/Warren evidence can still justify the counter.
- Unknown or expired evidence retains baseline spending, with high uncertainty.

The response only prioritizes an attainable first Robotics Facility after six
completed fighting supply. Existing emergency defense, resource reserves,
income, construction, reachable builder and human ownership guards remain in
force. The director records its response, evidence and expiry in each plan;
expired or superseded plans are rejected. Automatic strategy, attack control
and adaptive composition must be enabled. Explicit user strategies keep control.

These thresholds and uncertainty values are development heuristics, not
calibrated probabilities. First sightings depend on scout routes. Early expansion
was not positively seen in the six audited winning games, so its override is
initially covered by synthetic tests rather than a live success claim. The
selector does not add scout commands or spend additional scout units.

## Frozen trial procedure

First run Macro and Timing, three repeats each, on one committed source revision.
Use pressure, explicit VeryHard builds, BelShirVestigeLE, game/Python seed
20261025, step size 8, and 3600 game seconds. Verify loop-zero fingerprints,
binary/data/map identities, saved replays and frozen source hashes. Only broaden
to Rush, Power and Air if the candidate retains both targeted winning outcomes.
Finish a batch before tuning. Fixed-seed repeats measure reproducibility; wider
map, spawn and seed holdouts are required before a generalization claim.

No RL implementation or training is part of this experiment. The response
selector belongs to the StarCraft-specific adapter in the approved
[two-layer design](game-agnostic-architecture.md).

Software validation before freezing: locked sync, Ruff lint/format, the configured
Mypy scope, 526 synthetic tests with 88.72% combined coverage, and wheel/source
build all passed. Synthetic tests cover missing/stale evidence, first versus last
sightings, positive expansion overrides, per-contact aging, ignored configured
build labels, director serialization/expiry, user controls and actual spending
with ownership guards. Human interaction remains unverified.

## Offline replay and live trial status

Candidate `b3aff99` is frozen in the
[source manifest](experiments/2026-10-31/zerg-scout-selector-v1-manifest.json).
The [historical observation replay](experiments/2026-10-31/zerg-selector-historical-replay.json)
covers all fifteen R2 Zerg recordings and the three RoboticsV2 Timing recordings.
At the 180-second horizon it selects early Robotics for both sets of Timing
recordings and retains baseline spending in the other four R2 build conditions.
This is six development trajectory groups, with three reproducibility repeats
each, not eighteen independent opponents or new match outcomes.

The older R2 logs predate per-contact scouting telemetry. For them, the replay
reconstructs Pool/Warren timestamps and armed non-worker contacts only from
contemporaneous **Visible Enemy** raw units, using the saved game-data supply.
It retains contacts for 45 seconds and removes recorded deaths. Snapshots,
aggregate memory timestamps and configured build labels are excluded. Sampling
can miss transient contacts or shift sighting times relative to the live loop.
RoboticsV2 uses its recorded per-contact telemetry directly. Input snapshot and
game-data hashes are retained in the artifact.

The replay also exposes an important retention risk: Macro's observed Roaches
trigger the force response around 305.4 seconds and Power's around 315.4 seconds.
Neither is claimed to be a Timing classification. First Robotics has not yet
completed in Macro at that point, so this later switch can still change spending.
Only actual Macro/Timing trials can establish whether this combination retains
both wins; the source remains frozen rather than assuming replay selection is a
counterfactual victory.

Tools and Configure completed in the frozen checkout. Two subsequent API-only
preflights exited before connection with `536936448` (`0x20010000`), despite
verified Full Access under the interactive user account. Those attempts started
no matches and remain infrastructure failures, not defeats or timeouts. A normal
Battle.net client without an API port was open and left untouched. The user
subsequently closed it; zero clients were verified, and unchanged preflight then
succeeded on 5.0.17.98310 / data `9C1F3D3D30CA252E33FC67CA05CBE1EA`.
The normal client's causal involvement is not isolated. No gameplay or launch-code
change was made. Human control remains unverified.

The frozen targeted gate completed with **six victories**. Every repeat matched
its loop-zero fingerprint, exact map/binary identity and frozen source; replays
are nonempty and retained locally. Runtime and saved game-info both confirm
VeryHard computer difficulty. See the
[six-game verification](experiments/2026-10-31/zerg-scout-selector-v1-20261031-targeted-outcomes.json).

| Build | Candidate result | First Robotics / Immortal completed | Response evidence |
| --- | --- | --- | --- |
| [Macro](evaluations/2026-10-31-zerg-scout-selector-v1-20261031-zerg-macro.md) | 3 victories, 1145.4 s each | 360.4 / 410.4 s | Baseline opening; observed Roach force at 305.4 s |
| [Timing](evaluations/2026-10-31-zerg-scout-selector-v1-20261031-zerg-timing.md) | 3 victories, 1050.4 s each | 195.4 / 265.4 s | Early Pool at 45.4 s; later Roach-force confirmation |

Macro retains victory while taking 90 more sampled game seconds than R2;
Timing matches the earlier unconditional RoboticsV2 winner. These games resolved
before either the old or extended bound. The selector has therefore combined the
two targeted winning outcomes on the development scenario, rather than merely
extending a timeout. Rush, Power and Air retention is now running on the same
frozen source, with three repeats each and at most eight actual SC2 clients.
No global promotion or broader strength claim has been made.
