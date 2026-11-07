# Independent learned strategy and economy

The [completed first Easy run](evaluations/2026-11-07-rl-independent-easy-v1.md)
records twelve defeats, 2,055 training transitions, 81 optimizer updates and a
verified resume. The pipeline ran; playing-strength improvement remains unproven.
Resuming an existing frozen budget works. Starting another budget from a trained
checkpoint has not been implemented.

Implemented 2026-11-07 on the RL branch. The learned controller now owns its
economic actions as well as army intent. It runs alongside the separately
developed hardcoded policy; neither is a prerequisite or teacher for the other.
The original [hybrid pilot](evaluations/2026-10-31-rl-pilot-v1.md) remains archived
under its original action, feature and checkpoint identities.

## Action ownership

`LearnedPolicy` retains the semantic entity encoder, 512-input / 256-hidden GRU
and value head. Extra scalar features expose macro availability, own completed
and pending items, supply capacity/remaining and current gas staffing. Raw actor
IDs, opponent configuration, seeds and results stay outside neural inputs.

Four categorical heads produce **53 logits**: 3 army intents, 16 candidate targets,
30 immediate macro choices and 4 gas staffing levels. Hold continues existing
orders and disables tactical micro until a move/attack intent is selected. Its
target head is inactive and contributes zero log probability. Move/attack can
select any supported target, including home, regardless of army strength,
health, estimated enemy power or profile attack thresholds.

Macro choices are wait; train a Probe; build a Pylon, Assimilator, Nexus, Gateway,
Cybernetics Core, Robotics Facility/Bay, Stargate, Forge, Twilight Council or
Templar Archive; train a Zealot, Stalker, Sentry, Immortal, Colossus, Void Ray,
High Templar or Observer; research ground weapons/armor/shields level 1, air
weapons/armor level 1, Blink, Charge, Thermal Lance or Storm. The gas head chooses
0–3 workers per completed extractor. Research does not enable a combat ability;
each existing ability permission remains separately opt-in.

At each decision, public available-ability queries, resource/supply budgets,
idle/eligible actors and user permissions form macro masks. Placement remains
an execution attempt: a query can fail, an actor can become unavailable or a
command can be rejected. Feedback distinguishes skipped/failed attempts from
queued commands and subsequent observed changes. Exactly one selected paid
macro action is attempted per decision; there is no implicit opening, fallback
purchase, production template, emergency spending or automatic retry.

## Reused Python components

| Shared component | Role in this controller |
| --- | --- |
| Owned runtime and pinned SDK | Connection, binary/data compatibility, observation, lifecycle and cleanup |
| Facts, beliefs and assessment | Player-visible evidence and explicitly heuristic estimates; bounded target table still uses the shared ranking |
| Ownership and spending guards | Selection/release checks, reserves, one actor order per observation, ability permissions and command accounting through `issue` |
| Placement and actor selection | Fixed spaced-building placement, nearest eligible builder/idle producer and nearest available expansion; no threat-strength filter |
| Worker routing | Fixed mining routes and carrier/builder preservation; the model chooses production and gas staffing |
| Automatic baseline scouting | Fixed reconnaissance routes; no learned scouting head is advertised |
| Tactical execution | Direct guarded move/attack orders and existing individual focus-fire, cooldown kiting and low-health retreat while attacking |

The learned path bypasses `strategy_policies.candidates/compose`, the handwritten
macro controller, profile composition spending, mission-level abort/retreat
rules, army-wave attack thresholds and Warp Gate/Prism reinforcement spending.
It does not learn placement, scout routing, unit targeting or individual micro.
Its supported Protoss catalog is deliberately bounded; Warp Gate/Prism commands,
additional units and higher upgrade levels need a later action version.

The executor version is `sc2-placement-allocation-micro-v1`. Features are
`sc2-strategy-economy-features-v1`, actions `strategy-economy-action-v1`, masks
`sc2-mechanical-masks-v1`, decoder `sc2-strategy-economy-decoder-v1` and model
`sc2-strategy-economy-gru256-v1`. Checkpoint loading and PPO reject incompatible
contracts. Old artifacts remain readable with the original model. Shared skill
changes from the hardcoded track require a separately frozen RL revision.

## Easy curriculum

After the existing Windows installation/API stages, run:

```powershell
uv sync --locked --extra training
uv run --locked --extra training python -m source.training.cli train --output .local/rl-easy-v1 --sc2-path '<installed SC2 root>' --map-file '<verified map>'
```

`config/training/easy.json` declares two rounds, each with three frozen-policy
training games then three development games against **Easy Terran Rush**.
Training seeds are 31 then 32; development uses seed 131 throughout, with separate
sampling seeds. Each scenario has three reproducibility repeats, step size 32
and a 3600-game-second limit. Repeated starts are not independent scenarios.
Difficulty never rises automatically. Terminal win/loss reward remains +1/-1;
there is no reward for queued commands, survival or building arbitrary units.

PPO uses learning rate 0.00005, two epochs, 32-step sequences, eight-step burn-in
and the existing elapsed-time discounts, entropy, clipping and KL stop. Adam
state and cumulative optimizer steps persist across rounds and checkpoints.
Each checkpoint records its parent policy and training episode identities.
Development episodes are excluded from updates.

Use the identical command plus `--resume` after interruption. Completed episodes
are integrity checked and reused; incomplete attempts remain quarantined.
Resume requires the original source, lockfile, map, executable and curriculum
configuration. Checkpoints are reloaded before development. `progress.json`
records completed rounds and the latest artifact; raw data stays ignored locally.
All workers share the global eight-client limit with other worktrees.

The old `pilot` command remains an explicitly selected historical hybrid
experiment. `train` defaults to the independent Easy configuration and has no
rule-reference or hardcoded-policy promotion gate. Synthetic checks establish
implementation behavior; playing strength and human-input acceptance require
separate recorded evidence.
