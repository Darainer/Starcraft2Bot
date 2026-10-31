# Opponent inference from objective scouting facts

This work prepares a supervised opponent-state estimator. The user is building
the gameplay RL model in a separate session; this session supplies scouting,
factual data and inference interfaces through the SC2 adapter. The Python bot
still has to pass its [hardcoded strength gates](hardcoded-elite-milestone.md).
No gameplay learner is implemented or trained here, and the current data
exporter does not supply a reliable trained opponent-state predictor.

## Diagnosis: information and interpretation

The [frozen Zerg response](zerg-scout-response-experiment.md) won all fifteen
development games, but its generic five-label classifier remains weak. The
[reference diagnosis](experiments/2026-10-31/scouting-evidence-reference-diagnosis.json)
separates observation availability from errors when observations exist.

There are identifiable logic weaknesses. An early Pool supports Rush in the
generic classifier even though it was the useful response trigger in the Timing
games. First pressure is reduced to a time bucket; later evidence does not revise
that opening interpretation. A substantial armored force supports Power even
when a Macro opponent naturally fields one. These five mutually exclusive AI
configuration labels do not describe every component of a changing strategy.

There are also observation gaps. The opening Probe normally makes one trip.
In the reference, Macro's first positively recorded expansion is around 300
seconds, Power's around 315 and Timing's around 270. These are discovery times,
not expansion construction times. Small early army contacts must be distinguished
from a substantial force: diagnostic `fresh_army_contact` means positive observed
supply within 30 seconds, while `fresh_force` requires at least four supply.
An early empty expansion-center check does not prove continued absence.

The earlier 30.8% suitability coverage measures fresh visible-force samples
supporting counter-role scoring. It is not a measurement of how much of the
enemy world is known. The new overlapping diagnostic strata distinguish fresh
army contacts, substantial force, technology, expansions and site-center checks.
For example, Macro label accuracy remains zero even during its fresh-force and
fresh-expansion intervals. More scouting alone will not repair that label logic.

A causal division of error into scouting versus inference still requires paired
replay evidence. Record four times where available: fact became true, first legal
sighting, first stored feature and first useful inference. Current player logs
cannot establish the first time or unseen enemy truth. Do not invent an
information ceiling from conditional classification accuracy.

## Narrow scouting experiment

The existing Zerg spending, combat and response selector remain the reference.
The optional `--scout-revisit` adds one bounded revisit using an existing Probe:

- After the opening trip finishes, depart between 150 and 210 game seconds only
  if the natural inspection is stale, at least sixteen workers exist, and no
  economic emergency, nearby home threat or completed Observer precludes it.
- Inspect the enemy natural only, then return. Turn back after sixty seconds,
  on local threat or damage, or when an Observer becomes available. Selected and
  released workers remain human-owned. Do not purchase an additional scout.
- Track away-from-home worker seconds and confirmed scout losses by tag. Missing
  units are not confirmed deaths, and the worker-time figure is an opportunity
  proxy rather than measured lost income.

Freeze code and compare three Macro and three Timing games with revisit off
against the same six conditions with it on. Both arms use one-second snapshots,
VeryHard, pressure, BelShirVestigeLE, seed 20261025, step size eight and a 3600
game-second bound. Keep separate matrices and verify all starting fingerprints,
binary/map identities, source hashes, outcomes and replays. The option is recorded
in runtime/trial metadata; it does not enter opponent predictor inputs.

Judge useful facts delivered before 180/240/360-second deadlines, observation
age, mining opportunity and confirmed losses alongside wins. Finish each paired
batch before tuning. If the candidate retains both targets and improves useful
information, retain Rush/Power/Air and collect a complete Zerg development block
on the unused seed 2026103101. Reject a poor scouting candidate early and preserve
its data; additional collection can use the frozen winning reference instead.
All blocks retain three repeats per explicit build and the global eight-client
limit. More games under a new seed are development data, not a predeclared holdout.
Software validation before freezing passed locked sync, Ruff lint/format,
configured Mypy, 561 synthetic tests at 89.18% combined coverage, and source/wheel
builds. Protocol/lifecycle tests passed; human interaction remains unverified.

## Archive and input contract

`source.run_assistant` now retains every rotated debug-log file. Reports record
the retention policy and snapshot interval. Existing logs used retention of three
rotations: preserve every surviving file, but deleted historical debug segments
cannot be reconstructed. Existing observations, game data and replays remain
valuable. Snapshots are sampled records, not every API observation or proof of
human control.

The exporter copies originals into a new local archive without deleting source
files. It includes runtime reports, snapshots, console/debug rotations, game-info,
game-data, available frozen-source manifests and replays, with content hashes.
Short archive filenames avoid native Windows path limits; manifests retain the
original basenames as well as content hashes. A partial export remains marked
`building` and must not be used as a completed training corpus.
It refuses active recordings and output overwrites. Failed/interrupted runs are
retained; runs lacking valid completion/world provenance are excluded from
training. Archives and datasets remain ignored by Git; commit only code and
sanitized derived reports. The first reference archive contains fifteen games,
2673 sampled fact rows and 150 surviving files, about 832 MB.

```powershell
uv run --locked python -m source.opponent_dataset `
  --matrix logs/example-completed-matrix.json `
  --output .local/datasets/example-new-corpus
```

Each `facts/<episode>.jsonl` contains only causal facts:

- Visible enemy contacts and timestamped player-view memories, deduplicated by
  tag internally and aggregated by type without exposing tags as input features.
- Per-contact age, observed counts/supply, technology first-recorded sightings
  and observed build progress with its own timestamps.
- Positive expansion sightings and timestamped site-center inspections. Stale
  empty checks stay stale; absence of vision stays unknown.
- Our observed army/workers/resources and the ratio of recently observed enemy
  supply to our own army, explicitly a partial observation rather than total
  enemy relative strength.

Fact schema v2 also records our public starting base, publicly possible enemy
starts and playable bounds. Site inspections carry distances to those public
locations and a separate enemy-side freshness flag. Ordinary visibility of an
unoccupied site near our home must not count as enemy expansion scouting.
Multiple possible enemy starts remain candidates; the exporter never reads an
actual hidden spawn or AI configuration as input.
The [version-2 input example](examples/sc2-observed-facts-v2.json) is a legal
recorded prefix with stale technology sightings and unknown current enemy force.
Zero recently observed supply must not be interpreted as zero total enemy supply.
The [first version-2 corpus summary](experiments/2026-10-31/observed-facts-v2-first-corpus.json)
binds the extractor hashes and archive manifest: 27 matches, 12929 fact records,
299 surviving artifacts and about 3.28 GB of original content. The local complete
corpus is `.local/datasets/facts-v2-dev-27`; it still contains one world split
group. This is useful for adapter development, not an independent reliability test.

The projector excludes raw fog snapshots, radar blips, known hallucinations,
future timestamps, strategy labels, belief scores, director actions and outcomes.
Prefix-equivalence tests verify that adding future records does not change past
inputs. Schema and extractor hashes accompany the corpus. Its mechanics-specific
facts belong to the SC2 adapter in the approved
[two-layer architecture](game-agnostic-architecture.md).

`labels.json` is separate. Configured AI build is marked as a **weak episode
label**, not dynamic intent truth. It may support a coarse auxiliary recognition
task; it cannot supervise accurate hidden army counts or economic commitment by
itself. `diagnostics.json` is evaluation-only and is never a predictor input.

## Supervision and training sequence

1. Retain the original replay and exact engine/data identity. Extract a legal
   participant-view stream with fog enabled. In a separate offline pass, extract
   verified same-loop full-state targets. The oracle stream, future records,
   configured builds and results never enter input construction. This replay
   oracle pass is planned, not implemented by the current log exporter.
2. Supervise objective current-state heads first: enemy worker/base/unit counts,
   army supply and tech presence, plus uncertainty. Define rush/economy commitment
   as versioned derived targets with explicit time windows and ambiguity masks.
   Keep current-state estimates and future 30/60-second forecasts in separate
   targets. Do not label an unobserved quantity zero.
3. Compare last-seen memory and prerequisite rules against calibrated statistical
   baselines before training a recurrent sequence estimator. Use the shared
   semantic reasoning layer with SC2-specific fact encoding and output heads.
   Keep predictions in shadow mode until their downstream value is verified.
4. Group whole world starts together: map, binary/data, game seed, opponent race
   and starting spawn. All repeats, configured builds, bot revisions and scouting
   variants of that world stay in one split. The fifteen current games form
   **one split group**. One additional seed produces only two groups, still
   insufficient for independent train/validation/test splits. Obtain more seeds,
   maps and opponent policies; reserve untouched groups before training.
5. Report count/supply error, technology precision/recall, Brier/calibration,
   abstention coverage, evidence age and recognition lead before response
   deadlines. Separate visible and hidden-unit accuracy, and publish failures.
   Fit calibration only on validation groups. Confidence must fall on stale or
   unfamiliar evidence. A classifier benchmark cannot establish stronger play:
   require frozen closed-loop retention with costs before activating predictions.

Compare enemy-fact-only predictors with predictors that also receive our own
state. Our production reflects our existing response policy, so own-state
shortcuts can appear successful without learning robust enemy inference. Retain
different bot policies in the corpus, keep matched world groups together, and
test across policies before relying on such correlations.

For attribution, compare predictors on the **same visible prefixes** to test
logic. Compare fixed predictors across matched scout policies to test information
delivery. Same-time oracle inputs supply a further upper-information diagnostic;
future/full-replay inputs would answer a different question and cause leakage.

## Research basis

[Hostetler et al.](https://proceedings.mlr.press/r10/hostetler12a.html) explicitly
model limited, costly reconnaissance. This motivates recording the observation
process and costs, rather than treating missing features as negative evidence.
[Synnaeve and Bessière](https://arxiv.org/abs/1111.3735) learn build-tree models from
replays and noisy observations, supporting technology-path targets.
[Defogger](https://arxiv.org/html/1812.00054) evaluates objective hidden-state tasks
and memory baselines; its full-bot results also show that prediction noise can
hurt tactical decisions. These are Brood War methods, not validated SC2 timing
coefficients. Blizzard's
[replay protocol](https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto)
provides participant perspective and fog controls; verify their actual behavior
on the recorded binary before accepting an oracle-label extraction.

## First paired scouting result and next experiment

Frozen source `2be052b` completed all twelve matched games. All loop-zero starts,
48 source/config hashes, binary/map identity, actual VeryHard computer difficulty
and replays passed verification. See the
[paired outcome artifact](experiments/2026-10-31/scouting-paired-v1-outcomes.json),
[reference evaluation](evaluations/2026-10-31-scouting-evidence-reference-targets.md)
and [revisit evaluation](evaluations/2026-10-31-scouting-evidence-revisit-targets.md).

| Arm | Macro sampled finishes | Timing sampled finishes | Target wins |
| --- | --- | --- | --- |
| Reference, revisit off | 982.5 / 1149.6 / 1149.6 s | 1050.0 / 1050.0 / 1050.0 s | 6/6 |
| Revisit v1 | 872.1 / 872.1 / 872.1 s | 639.6 / 639.6 / 648.2 s | 6/6 |

The [reference diagnostics](experiments/2026-10-31/scouting-evidence-v1-reference-diagnosis.json)
and [revisit diagnostics](experiments/2026-10-31/scouting-evidence-v1-revisit-diagnosis.json)
are derived from separate hashed archives. All twelve games and original files
are retained. Revisit v1 wins faster in these recordings, but does not satisfy
the early information objective: before 240 seconds, Macro still has no observed
army or non-base technology, and Timing's first army contact remains about 193.9
seconds in both arms. Macro's first expansion discovery improves only from about
295.7 to 285.0 seconds; Timing changes from about 268.9 to 271.1 seconds.

The additional Probe turns back at about 158.6 seconds after seeing an enemy
Drone roughly eight units away, despite retaining 20 health and 20 shields. It
does not reach the enemy natural. Additional worker opportunity is about 13.9
seconds in Macro and 7.5 seconds in Timing, with no confirmed worker-scout deaths.
These are cheap attempts with low early information value. The generic Macro
classifier still never labels the Macro opponent correctly. Faster wins must not
be reported as better inference. Macro's earlier first Robotics completion also
precedes its first positive counter-response signal: changed worker allocation
and spending affect the trajectory independently of recognition.

After finishing the complete paired batch, the next candidate narrows only the
**revisit** worker-threat radius from eight to three units. Army threats keep the
eight-unit escape margin; damage, timeout, Observer handoff, home-defense and
ownership guards stay in force. The original opening Scout is unchanged. Tests
cover passing workers, close workers, army threats and the original opening
margin. This hypothesis must earn actual enemy-side inspections and retain wins
before broader evaluation. In parallel, the frozen reference collects all five
Zerg builds on unused seed 2026103101, so data collection does not depend on
promoting an unproven scouting change.
