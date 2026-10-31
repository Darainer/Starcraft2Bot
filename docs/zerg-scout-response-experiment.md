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
extending a timeout.

## Completed Zerg development suite

The unchanged candidate completed **15 victories / 0 defeats / 0 timeouts** across
all five Zerg builds at the 3600-second bound. Concurrency peaked at eight actual
SC2 clients. Every game verified its original loop-zero start, all 44 frozen
source/config hashes, map/binary identity, actual VeryHard computer difficulty
and a saved nonempty replay. All owned clients exited after the suite.

| Build | Candidate | Sampled finish time, every repeat | R2 development reference |
| --- | --- | --- | --- |
| Rush | 3 victories | 685.4 s | 3 victories, 685.4 s |
| Timing | 3 victories | 1050.4 s | 3 defeats, 1205.4 s at 3600 s bound |
| Power | 3 victories | 1070.4 s | 3 victories, 1070.4 s |
| Macro | 3 victories | 1145.4 s | 3 victories, 1055.4 s |
| Air | 3 victories | 480.4 s | 3 victories, 480.4 s |

R2's resolved wins above came from its original 1500-second suite; all candidate
wins also finish before that bound. R2 Timing uses the matched extended run.
These are retained resolved outcomes, not claims that a larger time limit made
the policy stronger. The three repeats reproduce one map/seed condition per
build. They are five development conditions, not fifteen independent scenarios.

The [complete evaluation](evaluations/2026-10-31-zerg-scout-selector-v1-20261031-complete.md)
contains trade, movement and recognition diagnostics. The
[verified outcome artifact](experiments/2026-10-31/zerg-scout-selector-v1-20261031-zerg-suite-outcomes.json)
retains all repeat fingerprints and replay hashes. The
[decision evidence](experiments/2026-10-31/zerg-scout-selector-v1-20261031-decision-evidence.json)
records response switches, observation horizons and actual tech completion.
Rush and Air keep the baseline opening; Power's observed Roaches select a
response around 315.4 seconds, with its first Robotics still completing at 340.4
seconds. The candidate passes this Zerg development gate. Terran/Protoss coverage,
map/seed holdouts and established community bots remain separate requirements;
there is no global baseline promotion or completed elite milestone claim.

## Recognition and build suitability metrics

The [strategy-metric artifact](experiments/2026-10-31/zerg-scout-selector-v1-20261031-strategy-metrics.json)
uses the existing `source.strategy_review` evaluator, with its ontology and
evaluator hashes. Each match is time-weighted, then repeats and build conditions
are averaged. Missing force evidence is excluded from suitability denominators
and reported as coverage.

| Diagnostic | Scenario mean | Interpretation |
| --- | --- | --- |
| Existing five-label strategy accuracy | 5.5% | Unknown counts as incorrect; configured build is the evaluation reference only |
| Existing classifier commitment coverage | 19.6% | Fraction of recorded time assigned a non-Unknown label |
| Existing multiclass Brier score | 0.803 | Uncalibrated forecasts; uniform five-class forecast scores 0.800 |
| Planned counter-role fit | 93.5% | Ontology role capacity against freshly visible force |
| Delivered counter-role readiness | 96.2% | Available completed controlled units versus that observed force |
| Ready-tech target fraction | 90.7% | Planned supply with currently available prerequisites/producers |
| Response evidence coverage | 30.8% | Recorded time with fresh visible-force evidence supporting suitability scoring |

The generic classifier remains weak despite the wins. The new selector does not
consume its labels or claim to identify the configured build. It chooses a
bounded investment under uncertain opening evidence, then updates from observed
forces. Role fit/readiness are capacity proxies, not combat simulation, whole-map
army truth or calibrated win probabilities. Timing's delivered readiness is lower
than the suite mean at 89.4%, so counter delivery remains a useful improvement
target even in its winning games. Early expansion overrides still lack a live
positive early-expansion case in this development suite.

Next strength work should retain this frozen Zerg component while integrating
and testing the separately successful Terran components behind explicit race
guards. Recognition work should improve dimension-specific evidence and scouting
coverage, validate action suitability separately from label accuracy, and use
untouched maps/seeds before claiming generalization. The hardcoded and community
acceptance gates still precede RL implementation or training.
