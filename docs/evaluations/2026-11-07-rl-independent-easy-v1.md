# Independent RL: first Easy training run

2026-11-07. **The independent strategy/economy pipeline ran successfully; no
winning checkpoint or playing-strength improvement was demonstrated.** Twelve
autonomous Easy games completed, all defeats. The learner collected 2,055 training
transitions, performed 81 optimizer updates and evaluated two reloaded checkpoints
on separate development starts. Work stopped after recording and publishing this
report.

Gameplay source was frozen at
`3b05de3b7fa7fe721af056c477b383c1250ddf58` throughout the run. Full policy,
checkpoint, rollout, replay, runtime, binary and map hashes are in the
[machine-readable evidence](../experiments/2026-11-07/rl-independent-easy-v1-evidence.json).
Raw artifacts remain under the ignored `.local/rl-easy-independent-v1/` directory.
The earlier [VeryHard hybrid pilot](2026-10-31-rl-pilot-v1.md) remains a separate
experiment with its original identities and results.

## What was built

The RL controller now owns army movement intent, immediate economic actions and
gas staffing. It bypasses the hardcoded director's candidate generation and plan
composition, economic opening/spending priorities, mission-level abort decisions,
army-wave attack thresholds and reinforcement spending. Hardcoded policy work
continues on its own track; this experiment used no teacher or rule reference.

The shared Python infrastructure still provides legal player observations,
heuristic beliefs/assessment, the owned SC2 runtime, selection/release checks,
resource reserves and command accounting. Building placement, actor selection,
worker routing, automatic baseline scouting and individual combat micro remain
fixed execution skills. Their behavior has not been learned. The shared target
table also retains its bounded heuristic ranking.

The two-layer architecture remains: SC2 semantic encoders and action heads
surround a game-independent recurrent core. The model has **710,375 parameters**
and **2,841,500 bytes** of float32 weights. Pooled entity/scalar encodings produce
512 inputs for a 256-hidden-unit GRU. Four categorical heads emit 53 logits:
three army intents, sixteen targets, thirty macro actions and four gas staffing
levels, plus a separate scalar value estimate. See the
[implemented contract](../rl-independent-training.md) for the action catalog and
the exact policy/executor boundary.

The collector preserves original masks and likelihoods, recurrent state, complete
episode boundaries and separate queued-command/observed-change feedback. Adam
state and cumulative optimizer steps persist across rounds. Checkpoints separate
core and adapter weights and are reloaded before evaluation. The default `train`
command uses Easy; the old `pilot` command explicitly retains the historical
hybrid experiment.

## Frozen experiment

All games used BelShirVestigeLE, explicit **Easy Terran Rush**, API step size 32,
and a 3600-game-second limit. Each group had three fixed-seed reproducibility
repeats. Training used game/Python seeds 31 then 32 and sampling seeds 101 then
102. Development used game/Python seed 131 and sampling seed 10101 in both rounds.
Training and development starting-state fingerprints differed; every repeat
within each group matched exactly.

`config/training/easy.json` declared two rounds. Model seed was 17; optimizer
seeds were 23 and 24. PPO used learning rate 0.00005, two epochs, 32-decision
sequences, eight-step burn-in, elapsed-time GAE/discounting, gradient clipping
and a 0.03 approximate-KL early-stop trigger. Terminal rewards were +1/-1/0;
intermediate rewards were zero. No imitation or command-completion reward was used.

| Group | Frozen policy | Wins / games | Outcome | End time per repeat | Transitions |
| --- | --- | ---: | --- | ---: | ---: |
| Round 1 training, seed 31 | Initial P0 | 0 / 3 | 3 defeats | 782.9 s | 822 |
| Round 1 development, seed 131 | Checkpoint P1 | 0 / 3 | 3 defeats | 1534.3 s | 1611 |
| Round 2 training, seed 32 | Checkpoint P1 | 0 / 3 | 3 defeats | 1174.3 s | 1233 |
| Round 2 development, seed 131 | Checkpoint P2 | 0 / 3 | 3 defeats | 1621.4 s | 1704 |

All 12 games ended normally with saved replays. There were no timeouts,
infrastructure failures or intentionally aborted episodes. The **3,315 development
transitions were excluded from updates**. Repeated starts are not independent
scenarios, and these results establish neither generalization nor a win-rate gain.
The longer P2 development survival is not evidence of stronger play by itself.

| Checkpoint | Policy ID prefix | Updates in round | Cumulative updates | KL stop |
| --- | --- | ---: | ---: | --- |
| Initial P0 | `e18e08fb6dc1` | 0 | 0 | — |
| P1 | `1d48e9a93972` | 54 | 54 | No |
| P2 | `6eced0d7b18f` | 27 | 81 | Yes |

The largest recorded approximate KL was 0.01875 in round one and 0.05610 in
round two. The latter triggered the configured stop, preventing further updates
in that round. The trigger is not a guarantee that recorded KL stays below 0.03.
The final checkpoint is `.local/rl-easy-independent-v1/iteration-002/checkpoint/`.

## Observed behavior and unresolved problems

The initial training policy reached 27 workers but no completed army. P1's
development games reached 47 workers and 30 army supply; P2 reached 50 workers
and 28 army supply. P1's second training batch, with a different sampling seed,
again produced no completed army. These are observed state maxima, not proof that
training improved economic or combat decisions.

Failed economic execution attempts were frequent. Across the three first-round
training repeats, Gateway attempts recorded 114 execution failures and six
queued commands; the second training batch recorded 141 failures and no queued
Gateway commands. These counts include repeated identical trajectories. Generic
`execution_failed` feedback does not distinguish every placement/pathing cause.
The sampled runtime records also contain rejected Nexus and Assimilator commands,
including `CouldntReachTarget` and `CantBuildOnThat` results. The evidence retains
the raw error codes and queued/failed action counts.

This leaves both weak learned decisions and execution/placement availability as
unresolved bottlenecks. A queued command is not evidence of a completed building.
The small budget and sparse terminal reward do not establish whether additional
training alone would resolve these failures. No gameplay adjustment was made
during the frozen run, and difficulty was not increased.

## Verification and resource measurements

Native Windows checks passed: `uv sync --locked`, Ruff lint and format checks,
mypy, **652 tests with 87.90% combined coverage**, and `uv build`. GitHub's
[quality and test jobs](https://github.com/Darainer/Starcraft2Bot/actions/runs/42375754574)
also passed for the frozen implementation.

All episodes had zero initial recurrent memory, matching loop-zero fingerprints
within their groups and passing 59-command startup compatibility audits. The
saved weights exactly reproduced stored logits and values at the first, middle
and last decision of every episode: **36 recomputed decisions, maximum error 0**.
The episode loader's integrity/continuity checks also passed during a real resume.

Running the same frozen command with `--resume` completed in 106.35 seconds. It
created no new episodes, SC2 processes or API connections; rollout/checkpoint
artifact hashes stayed unchanged, and the update count remained 81. Original
first-pass benchmark records were retained before that resume check. The archived
hybrid checkpoint and a 549-transition original episode were also loaded
successfully with their original contract and policy identity.

With one Torch CPU thread and no SC2 client running during the benchmark, the
largest sampled states had 58 entities in round one and 80 in round two. Their
p95 forward times were 1.80 ms and 1.91 ms respectively. These include tensor
encoding and inference, excluding game stepping and action sampling. The trainer
held approximately 0.98 GB and 1.66 GB RSS at those measurement points because it
retained full episode data. This is not a peak-memory bound or a minimum-PC claim.

## Native runtime and shared-control record

The runner used the approved Full Access session and the normal Windows account;
`whoami` confirmed it was not the restricted sandbox account. Existing manual
installation/initialization was reused, followed by Setup and Start preflight.
Games ran through the owned, non-real-time training runtime on Windows
11 build 26200, Python 3.12.10, burnysc2 7.3.0, pys2clientprotocol 1.0.2,
protobuf 7.36.2 and Torch 2.15.0+cpu.

Actual ping in every match: game version `5.0.17.98310`, base/data build `98310`,
data version `9C1F3D3D30CA252E33FC67CA05CBE1EA`. Binary/map SHA-256 identities and
per-episode runtime/replay hashes are recorded in the linked evidence. No shared
executor updates from the parallel hardcoded branch were merged into this run.

| Acceptance check | Result | Evidence |
| --- | --- | --- |
| Probe returns selected binary/data identity | PASS | Preflight and all match pings agree |
| Owned non-real-time Easy matches complete | PASS | 12 results and 12 replays |
| Expected process cleanup | PASS | All owned clients closed; none remained after the run |
| Local real-time shared match loads | NOT TESTED | This run used autonomous non-real-time matches |
| Manual worker selection/movement/gathering while paused | NOT TESTED | No human-input trial |
| Minimap, camera, drag selection and control groups | NOT TESTED | No human-input trial |
| Command-card buttons and training hotkeys | NOT TESTED | No human-input trial |
| Chat pause/resume and human orders alongside automation | NOT TESTED | No shared-control trial |
| Individual combat-ability effects | NOT TESTED | Abilities remain individually opt-in |

Shared-control verdict: **NOT VERIFIED**. Synthetic ownership tests, API success
and autonomous outcomes do not establish that human controls work.

## State when work stopped

The independent implementation and outcome record are available in
[PR #4](https://github.com/Darainer/Starcraft2Bot/pull/4); the hardcoded policy
remains separately developed. This run does not promote RL into normal play.
Resuming the original frozen budget is implemented and verified. Extending a
completed budget or starting a new budget from a trained checkpoint is still
missing; checkpoint continuation was not implemented. More Easy training,
execution diagnostics and broader evaluation remain future work. No further
training was started after this run.
