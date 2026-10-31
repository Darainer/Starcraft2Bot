# Opponent beliefs, scouting value and director evaluation

Requested 2026-10-31. Separate uncertainty about aggression/economic commitment,
technology, enemy army supply and relative strength. Scouting should answer a
specific decision question while accounting for the scout's replacement cost,
lost mining time, route exposure and previous losses.

## Review findings

The frozen R2 five-label estimator is observational (`control_enabled=False`).
That director receives composition targets and tactical facts, but not that belief.
Its production plan forwards the assessment's scouting overlay. Consequently,
an improving win count does not establish that the director predicts strategy.
On R2's ten fixed development conditions, final label accuracy is 10%, coverage
30%, and accuracy at 360 seconds is 40%. All three repeats remain available;
those conditions are not independent training examples.

The longer Zerg Timing test matters: at 3600 seconds, reference `9fd64a1` wins
3/3 around 1515.4s, whereas R2 loses 3/3 around 1205.4s. The old 1500-second cap
hid a reference win. Paired starts match exactly at the new limit; their hash
differs from the old hash only because the fingerprint includes the time limit.
This is a regression target, despite R2's 21/30 shorter-bound development wins.

R2 scouting also conflates an interrupted worker scout returning home with
a completed inspection. Observers prioritize expansion patrols ahead of unanswered
technology questions. Composition memory uses its freshest unit's timestamp for
the aggregate, which can make older sightings look fresher than they are. These
were implementation gaps; no hidden opponent build label may repair them.

## Initial implementation and RL foundation

The working tree now contains a versioned [ontology](../source/data/game_ontology.v1.json)
and validated loader, independent immutable beliefs with per-contact aging,
director belief/scouting-question contracts, bounded counter-target transfers,
and question-based Observer choices. Worker scouting has bounded opportunity and
loss budgets; a missing tag reserves replacement budget without being called a
death, and an interrupted return does not complete an inspection. Observer choices
charge travel, observed exposure and actual replacement cost; confirmed losses
trigger a backoff. The first live integration (`belief-gate-v1-20261031`) lost
all three matched Zerg Timing games at 820.4 seconds and was rejected. Its
cost-aware controller is retained as `experimental_scouting.BeliefScoutController`;
runtime scouting returns to the R2 controller. Beliefs and per-contact evidence
continue to be logged, while `Assessment.belief_control` defaults to false and
the rejected belief-driven production/risk rules do not govern live plans.
The new [hardcoded milestone](hardcoded-elite-milestone.md) takes priority.

The [computed baseline](evaluations/2026-10-31-strategy-belief-baseline.md) publishes
time-weighted recognition, planned response, delivered readiness and tech/budget
metrics with formulas and evidence coverage. The [first RL architecture](rl-architecture.md)
defines how the same ontology and uncertain beliefs feed a recurrent policy and
structured action vector. No learned policy or calibrated uncertainty model is
included in this initial implementation.

## Reference basis

- Blizzard's [SC2 scouting guide](https://news.blizzard.com/en-us/article/4488316/game-guide-scouting)
  recommends repeated information gathering about production and expansions,
  and identifies workers and Observers as Protoss scouting methods. This motivates
  different questions and methods rather than one fixed route.
- Max's [Scouting basics](https://terrancraft.com/2014/09/14/scouting-basics/)
  emphasizes a purpose for each scout and cautions against overconfident deductions.
  Its old supply/timing examples are not copied into this patch's build order.
- Hostetler et al., [Inferring Strategies from Limited Reconnaissance](https://arxiv.org/abs/1210.4880),
  model evidence under partial observability and the opportunity cost of scouting.
  This motivates beliefs and information value, not a claim that our initial
  transparent heuristic is a trained Bayesian model.
- Synnaeve et al., [A StarCraft Defogger](https://arxiv.org/abs/1812.00054),
  distinguish state estimation from future prediction and evaluate downstream
  usefulness. These two research papers concern Brood War; their principles do
  not validate SC2 thresholds or combat predictions.
- Blizzard's [5.0.17 patch notes](https://news.blizzard.com/en-gb/article/24309308/starcraft-ii-5-0-17-patch-notes)
  roll back several 5.0.16 changes, including restoring twelve starting workers.
  Historical guides supply principles; installed-patch data and matched live
  tests determine current timings and action effects.

## Implementation and measurement contract

1. Maintain independent aggression and economy beliefs; they can both be supported.
   Represent air/armored-ground/light-ground/cloak tech separately. Unknown starts
   with maximum uncertainty, not an assertion of safety or a free expansion.
2. Keep evidence timestamps and identities. Re-reading the same sighting must not
   add confidence. Decay confidence when information ages. A newly seen unit must
   not refresh unrelated old tech or every remembered unit. Fog is not negative
   evidence; positively inspected empty locations only describe those locations.
3. Report observed enemy supply as a lower bound, retained sightings separately,
   and a deliberately broad heuristic range for unseen force. Relative supply
   strength carries that uncertainty. Existing local, weapon-aware fight evidence
   remains distinct from the global estimate and retains its safety checks.
4. Give scouts named questions: opening commitment, technology, army location/
   strength, and expansion occupancy. Rank information relevance and uncertainty
   against travel/opportunity cost, observed weapon exposure and loss budgets.
   Preserve human ownership, retreat routes and one-order arbitration. Do not
   introduce Hallucination or any combat ability without its explicit opt-in.
5. Expose beliefs to the immutable director contract. Change build targets only
   from sufficiently fresh positive evidence, with reversible targets and explicit
   reasons. Do not turn a confident but uncalibrated five-label guess into an
   unconditional counterbuild.
6. Measure time-weighted label accuracy, abstention coverage, Brier error, early
   recognition/lead and per-axis uncertainty/evidence age. Configured AI build is
   evaluation-only and an imperfect reference for a changing, mixed strategy.
7. Separately score planned counter-role allocation, tech feasibility and delivered
   response readiness against fresh observed threats. Publish the score formula,
   evidence coverage and missing-data cases. These are diagnostic proxies, not
   combat win probabilities; compare them with actual trades, losses and outcomes.
8. Log scouting information gained, assignments, actual known losses and estimated
   opportunity cost separately. Returning alive without inspecting a destination
   earns no completion or information credit. Do not call a temporarily missing
   worker dead without confirmation.

## Acceptance sequence

Synthetic tests cover unknown/future/stale evidence, deduplication, transitions,
mixed tech, strength uncertainty, actor ownership and scout cost/loss budgets.
Recorded-state reports establish the current metric baseline before tactics tune.
Then freeze an isolated candidate for three explicit Zerg Timing trials at the
new 3600-second bound. Reject poor candidates early. A promising repair proceeds
to retention checks for the seven R2-winning groups, with at most eight clients.
No source changes during a live batch. No claim of generalization, calibrated
confidence, counterfactual wins or shared human-control acceptance follows from
synthetic tests or offline analysis alone.
