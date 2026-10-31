# Strategy recognition and response baseline — 2026-10-31

This is an offline review of **30 frozen R2 recordings across ten explicit
conditions**, plus the separate six-game extended Zerg Timing comparison.
It does not replay games with a new policy or establish a counterfactual result.
The recorded five-label estimator remains observational. The new multidimensional
belief model is reconstructed causally from each recording's public evidence.

## Results

Values are duration-weighted within each game, averaged across all three repeats,
then equally across the ten conditions. Unknown predictions count as incorrect
in total accuracy; conditional accuracy must not hide abstentions.

| R2 original 1500-second group | Value |
| --- | ---: |
| Strategy-label accuracy over recorded game time | 9.34% |
| Non-Unknown classification coverage | 20.15% |
| Multiclass Brier error, unnormalized sum over five classes | 0.7186 |
| Time with usable current enemy-force/plan evidence | 32.19% |
| Planned counter-role fit, conditional on that evidence | 91.90% |
| Delivered counter-role readiness, conditional on that evidence | 92.03% |
| Target supply with ready producer/prerequisite tech | 88.41% |
| Target army supply within worker-adjusted 200-supply ceiling | 69.18% |

The earlier endpoint metrics remain distinct: final accuracy 10%, final coverage
30%, and accuracy at 360 seconds 40%. A final or fixed-horizon prediction does
not describe the fraction of the game for which the estimate was useful.

| Condition, three repeats each | Recognition accuracy | Evidence coverage | Planned role fit | Delivered readiness | Ready target tech |
| --- | ---: | ---: | ---: | ---: | ---: |
| Terran Air | 8.33% | 20.13% | 84.20% | 100.00% | 98.38% |
| Terran Macro | 15.38% | 29.73% | 85.62% | 96.66% | 97.50% |
| Terran Power | 0.00% | 17.12% | 90.13% | 90.83% | 99.51% |
| Terran Rush | 32.13% | 40.61% | 95.43% | 82.28% | 86.46% |
| Terran Timing | 15.05% | 38.16% | 95.17% | 74.06% | 89.53% |
| Zerg Air | 0.00% | 17.70% | 89.65% | 98.53% | 77.58% |
| Zerg Macro | 0.00% | 37.90% | 95.38% | 97.44% | 94.58% |
| Zerg Power | 9.34% | 40.64% | 96.49% | 94.57% | 96.68% |
| Zerg Rush | 0.00% | 24.80% | 91.57% | 100.00% | 90.89% |
| Zerg Timing | 13.13% | 55.11% | 95.38% | 85.96% | 53.04% |

The extended comparison is a separate group with the same 3600-second limit:

| Zerg Timing | Outcome | Recognition accuracy | Planned role fit | Delivered readiness | Ready target tech | Evidence coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Reference `9fd64a1` | 3 wins, 1515.4s | 0.00% | 92.79% | 91.57% | 99.31% | 37.28% |
| Frozen R2 | 3 defeats, 1205.4s | 13.27% | 95.79% | 86.18% | 52.72% | 56.00% |

R2 scores higher on planned role fit and label accuracy while losing this
matchup. Its delivered readiness and tech availability score lower. This is a
reason to investigate production delivery and fight selection, not evidence
that any one proxy caused the defeat. The reference wins shortly beyond the
old cutoff; extending the limit exposed an existing win rather than strengthening it.

## Published formulas and limits

For successive observations at `t_i` and `t_(i+1)`, weight the decision at `t_i`
by `delta_t`. Do not use the next observation to predict the previous interval.
Stop integration at the last recorded observation. Accuracy is
`sum(delta_t * correct) / sum(delta_t)`; coverage replaces `correct` with
`category != Unknown`. Brier error integrates
`sum_k (p_k - indicator(k == configured_build))^2` in the same way. Configured
build labels enter scoring only; they are imperfect truth about a mixed strategy.

Counter-response scoring requires a current sighting no older than five seconds,
positive observed supply and recorded production targets. Missing evidence is
excluded and its duration is exposed as coverage. Partition that observed supply
into air, armored ground and remaining ground demand `D_r`. Let `D` be its sum,
`P` total target supply, `P_r` target supply with the ontology's corresponding
role, and `A_r` currently ready eligible own supply with that role:

```text
planned_role_fit = sum_r min(P_r / P, D_r / D)
delivered_role_readiness = sum_r min(A_r, D_r) / D
ready_tech_target_fraction = tech-enabled target supply / P
target_budget_feasible = indicator(P <= 200 - configured_max_workers)
```

Ready units exclude selected, released, hallucinated, dead and unfinished units;
automation must be enabled for their contribution to automation readiness.
Conditional spell roles require their individual opt-in, research and energy.
Tech availability requires ready producers and listed prerequisites. Budget
feasibility is a coarse end-state ceiling; it excludes support-unit supply and
does not establish affordability or feasible completion time.

These are **capacity proxies**, with deliberately limited conclusions. One
versatile unit can contribute to several role capacities; the score does not
allocate it to simultaneous fights. Legacy recordings do not provide per-unit
light-ground supply, so the baseline uses generic ground for that residual.
The score omits range, terrain, position, health, upgrades, timing and enemy
reinforcement. It can saturate against a small visible detachment while the
unseen army is overwhelming. A 100% score does not predict victory. Add richer
role allocation, response latency and local combat evidence in later versions,
and require improvement in resolved matches before promoting a tactic.

Axis uncertainty and evidence age are also exported, without claiming calibrated
probabilities. Scenario-mean uncertainty is 95.26% aggression, 87.38% economy,
91.38% air, 57.28% armored ground, 60.14% light ground, 99.18% cloak and 76.16%
enemy army. High uncertainty is appropriate when evidence is missing. The legacy
aggregate's freshest timestamp cannot reconstruct every older contact's real age;
new logs include per-contact timestamps. Player observations alone cannot grade
accuracy of the unseen global army. That evaluation needs separate oracle data.
Scouting losses/opportunity costs are newly instrumented and unavailable in
these older recordings; they are not retrospectively invented.

## Reproduction and identity

Use the validated explicit matrix, not a glob of mixed or aborted logs:

```powershell
uv run --locked python -m source.strategy_review --matrix logs/production-v5-r2-20261031-complete.json --output logs/strategy-review-r2-20261031.json
```

The long comparison uses the two original `*-limit3600-zerg-timing.json` matrices
in their frozen worktrees. Raw reports remain local and ignored by git.
The [gameplay source archives](../experiments/2026-10-31/README.md) and
[original evaluation](2026-10-31-production-v5-r2-complete.md) identify the
recorded revisions. The evaluator exports every repeat, per-metric observation
seconds, condition identities and ontology/evaluator hashes. Conditions include
map, binary ping, seed, duration, step, opponent and initial settings; different
limits are not pooled as repeats.

Ontology canonical JSON SHA256:
`ca5d425b403eeb65d9abed2481eda0b7f31373102e56e17fb936a1b6f97e0d33`.
Evaluator source SHA256:
`59169f8255d944d18b57e6ed1cd0a82a9f92d956123c3c9b5adba35a2370501b`.
The [RL architecture](../rl-architecture.md) uses these diagnostics as separate
estimation, planning and delivery measures; they are not automatically rewards.
