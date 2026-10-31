# Local recurrent PPO pilot

The user authorized implementing and running the remaining RL prototype on
2026-10-31. This extends the [foundation](rl-implementation.md) with a small
neural policy, richer player-view inputs, complete episode collection, an owned
Windows environment and a bounded PPO pilot. Imitation is omitted because the
rule bot has not earned expert-teacher acceptance. This research pilot does not
promote a controller into normal human play or certify playing strength.

## Model and inputs

`StarCraftPolicy` has 645,972 parameters (2,583,888 bytes of float32 weights).
The SC2 adapter encodes semantic entity features into 64 dimensions, pools each
of controlled/contact/candidate sets with mean and maximum into 128 dimensions,
and encodes scalar features into 128 dimensions. The concatenated 512-feature
representation feeds a shared 256-unit GRU cell. SC2 heads produce seven
objective logits, sixteen candidate-conditioned target logits, seven production
logits, four scouting logits and a scalar value estimate. Candidate scoring uses
each candidate's encoded features with the recurrent output; full handles are
alignment metadata and never numerical input features.

Live inputs include public unit capabilities/positions/health, selected/released
eligibility, own queues and income, current intent, observed changes and issued
command counts. Population costs come from full live unit metadata, preserving
morph costs as distinct from a unit's total population footprint. Opponent orders
and queues are excluded. Missing features have explicit support/known masks,
uncertainty and ages. Entity sets cap at 128 per force group and record overflow.
Income scales by 1000, queue depth by 5, movement speed by 6, damage per second
by 100 and weapon range by 15; location offsets use 200 map units. These fixed
scales and schema identities are recorded, rather than learned from evaluation.
Competing COA estimates remain unsupported pending an evidence-backed model.

## Environment and records

`LocalEnvironment.reset/step/close` exchanges observations and sampled actions
with a worker thread running the existing owned-client runtime. Policies retain
the director's current two-second/event-driven cadence; existing tactical/macro
executors retain actor ownership, reserve, ability and command guards. Training
startups are serialized across worktrees and count all native SC2 processes
against the eight-client global limit. This mode never attaches to an unrelated
game. Closure signals only its own worker and lets the owned runtime clean up.

The runtime retains the last actual API observation because BurnySC2 invokes
`on_end` before preparing its final state. SDK-private preparation remains in
`source/runtime.py`. A time-limit transition uses the actual final observation
and its value, with no terminal loss. Real game-result draws remain distinct.
Missing observations, inference deadlines, disconnects and bot exceptions fail
collection and quarantine the whole episode.

Complete manifests retain source/dependency/checkpoint/schema identities,
map/executable hashes, exact ping/data, explicit opponent configuration, seeds,
settings, step/time conventions, splits and verified loop-zero fingerprints.
Gzipped decision records retain original likelihoods/masks, execution masks,
recurrent boundaries, issued intents and subsequently observed changes. Observed
movement/completion is recorded without claiming a queued intent caused it.
All rollout, checkpoint, replay and log artifacts stay in ignored local storage.
The loader checks integrity and rejects incomplete, mixed or quarantined episodes.

## Learner and declared experiment

The first optimizer is Adam with recurrent clipped PPO, value regression,
categorical entropy and gradient clipping. Sampling and training use the same
conditional masks. Sequence chunks stay inside episodes, initialize from recorded
memory and use up to eight prior observations for burn-in. Discount and GAE decay
use elapsed game seconds. Weights stay frozen for all collection repeats and
change only between complete batches; checkpoints separate core and adapter.

The checked-in `config/training/pilot.json` declares pressure versus VeryHard
Terran Rush, seed 31, three reproducibility repeats, step size 32 and a 3600-second
bound. Model seed is 17, sampling seed 101 and optimizer seed 23. One batch of
three initial-policy episodes supplies training data; up to two PPO epochs use
32-decision chunks, eight-step burn-in, learning rate 0.0003, discount time constant
1800 seconds and eligibility time constant 600 seconds. Approximate KL above
0.03 stops further updates. Terminal rewards are +1/-1/0, intermediate rewards 0.

The frozen trained checkpoint then plays three matched development games, and
the current frozen rule controller plays three reference games. All nine starts
must have the same loop-zero fingerprint. This is one development condition,
with repeated starts rather than independent scenarios or held-out evidence.
The initial training games are the untrained-policy comparison, so any measured
gain remains an in-sample result. A poor candidate gets no broader matrix.

## Commands and acceptance

Follow [the Windows runbook](windows-install-and-play.md) through setup and the
API probe first. Existing completed installation/manual initialization can be
reused. Human-input acceptance remains separate and must not be inferred from
these autonomous games. Install the optional CPU learner on Python 3.11+:

```powershell
uv sync --locked --extra training
uv run --locked --extra training python -m source.training.cli pilot --output .local/rl-pilot --sc2-path '<installed SC2 root>' --map-file '<verified map>'
```

Source must be committed and clean before collection. The normal assistant does
not import PyTorch. The root runtime still supports Python 3.10; training requires
3.11+. Windows and x86-64 Linux training resolve CPU wheels from the explicit
official PyTorch index. The Linux SC2 environment remains a separate future gate.

The pilot writes outcome/optimizer/checkpoint identities and measured CPU timings
to `pilot-results.json`. Benchmarks use actual recorded states and report median,
95th/99th percentile latency, entity counts, Torch thread count, process memory
and concurrent SC2 client counts. Weight size is not total Python/Torch memory.
They do not establish a minimum PC specification or a parallel-game speedup.

Synthetic validation: 640 tests passed with 88.33% combined statement/branch
coverage before the first live pilot. Real rollout results are recorded separately
after completion. Human shared-control validation remains pending.
