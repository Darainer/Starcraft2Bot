# Military doctrine for strategic control

Design proposal, 2026-10-31. Use the **U.S. Army operations process**, supported
by mission command, intelligence preparation, reconnaissance and sustainment, as
one coherent framework for this bot. This is an analogy for software design and
decision making under uncertainty. Doctrine does not establish SC2 counters,
combat equations, probabilities or winning thresholds. Those require game data
and matched experiments. No gameplay change is implemented by this document.

## Doctrinal foundation

Publication and change dates below were checked against the Army Publishing
Directorate on 2026-10-31:

| Official source | Verified edition | Relevant principle |
| --- | --- | --- |
| [ADP 5-0, The Operations Process](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN18126-ADP_5-0-000-WEB-3.pdf) | 31 July 2019; active | Plan, prepare and execute with continuous assessment; maintain running estimates. Paragraphs 1-54–56 distinguish facts, assumptions, enemy/friendly status and recommendations. |
| [ADP 6-0, Command and Control](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN47032-ADP_6-0-000-WEB-1.pdf) | 7 July 2026; active | Use commander’s intent and mission command to support subordinate decision making. The 2019 publication is not cited as the current edition. |
| [ATP 2-01.3, Intelligence Preparation of the Operational Environment](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN43736-ATP_2-01.3-003-WEB-7.pdf) | Basic publication: 1 March 2019; Change 3: 15 May 2025 | Develop enemy courses of action and discriminating indicators, locations and decision points. Paragraphs 6-34–36 and 6-64–67 provide the central model. |
| [FM 3-98, Reconnaissance and Security Operations](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN37194-FM_3-98-000-WEB-1.pdf) | 10 January 2023; active | Reconnaissance answers decision requirements in time; specify engagement/disengagement criteria. See paragraphs 3-53–56 and 4-6. |
| [FM 4-0, Sustainment Operations](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN46157-FM_4-0-000-WEB-1.pdf) | 20 March 2026; active | Integrate sustainment into operations to preserve freedom of action, operational reach and endurance. |

These publications fit together: intelligence informs the plan; reconnaissance
resolves important uncertainties; intent coordinates execution; sustainment makes
the plan supportable; assessment determines whether it worked. OODA can serve as
a shorthand for rapid feedback within this structure. The selected Army stack
provides more concrete design contracts for this project.

## Mapping into the bot

The existing modules provide foundations; the extensions below are proposals.

| Doctrine concept | Repository seam | Proposed SC2 contract |
| --- | --- | --- |
| Running estimates and shared understanding | `opponent_beliefs.py`, `game_assessment.py`, `game_ontology.py` | Separate observed facts, retained sightings and hypotheses; record evidence age, provenance and uncertainty. Missing vision remains unknown. |
| Enemy courses of action (COAs) | `opponent_strategy.py`, `strategy_policies.py` | Maintain competing explanations of what the opponent may do next, including timing, technology, army disposition and economic commitment. |
| Intent and mission orders | `StrategicDirector`, `StrategicPlan` | Express purpose, desired conditions, assigned force, constraints and replanning triggers. A target coordinate alone is insufficient. |
| Decision-linked reconnaissance | `scouting.py`; experimental question-based controller | Associate each question with a decision, distinguishing evidence, inspection location, useful deadline, scout budget and withdrawal conditions. |
| Disciplined local initiative | `missions.py`, `army_waves.py`, `tactics.py`, `combat_assessment.py` | Let local controllers choose safe approaches, preserve volleys and disengage under explicit conditions while retaining strategic intent and ownership guards. |
| Sustainment and reserves | `economy_assistant.py`, `strategy_profiles.py` | Assess productive capacity, replenishment and protected resources before committing an attack or delaying replacement income. |
| Continuous assessment | `session_review.py`, `evaluate_matches.py`, `analyze_session.py` | Compare expected effects with observed results; distinguish task completion from useful effects and causal hypotheses from evidence. |

Mission command here means bounded controller autonomy, not human leadership
psychology. Local initiative cannot claim selected/released actors, bypass
`issue`, bypass resource reservations or enable an optional combat ability.

## Enemy COAs and build suitability

IPOE prioritizes enemy COAs while retaining both the **most likely** and **most
dangerous** possibilities. The dangerous COA depends on the friendly plan: a
cloaked attack is especially consequential when detection is absent. It need not
be the most likely explanation.

For this bot, a COA should describe a possible sequence, such as armored-ground
pressure followed by expansion, rather than assign one permanent Rush/Macro
label. Aggression and economic commitment can coexist. Keep supporting and
contradicting observations, unknowns and age separately. A production structure
permits a technology path; it does not prove the resulting army exists.

Compare candidate responses against those COAs for feasibility, timely delivery,
combat suitability and exposure to alternatives. Preserve a bounded contingency
reserve rather than buying every possible counter. Any posterior probabilities,
role-fit weights or expected-utility calculation are **our proposed SC2 model**;
doctrine does not supply them. Current heuristic confidence is not a calibrated
probability. Never import real-world force ratios as SC2 engagement thresholds.

## Example: scouting before a counterbuild decision

Suppose recent observations suggest armored-ground pressure, but its scale and
departure time remain uncertain. The decision is whether to accelerate Robotics
and an Immortal or retain immediate ranged defense and income investment.

Issue a concrete question: inspect the suspected production area and a relevant
approach for evidence that distinguishes an imminent attack from continued
production or expansion. A proposed latest useful reporting time is:

```text
estimated contact time
  - critical-path response lead time (resources, prerequisites, production, travel)
  - a measured allowance for uncertainty and execution delay
```

Allow tasks to overlap when computing the critical path, and use ranges where
timings are uncertain. This is our implementation of
decision-linked reconnaissance, not a universal military or SC2 timing rule.
Charge the scout’s travel, foregone mining and replacement exposure; compare an
existing Observer with an eligible Probe and record the method’s actual cost.
Do not require an Observer to authorize the Robotics Facility that produces it.

Fresh positive unit/tech evidence may justify accelerating the counter. An
interrupted scout or unobserved building location cannot establish its absence.
Per-contact timestamps prevent one newly seen unit refreshing an old army.
At the deadline, an unanswered question remains uncertain; use a predeclared
fallback and contingency rather than waiting indefinitely or inventing safety.
Whether this improves on the current opening is a separate live-test hypothesis.

## Readiness, participation and endurance

Assess the complete chain: desired counter, attainable budget, completed powered
prerequisites, produced units, arrival and effective firing. Suitable units behind
a blocked frontline or outside useful range must not receive full credit as
participating combat power. Engagement criteria should describe the threatening
weapons, approach, available force and retreat conditions, with hysteresis to
avoid repeated order cancellation. Local controllers need authority to respond
to new contact without waiting for a strategic refresh.

Sustainment adds another readiness condition. A large army can still approach
economic culmination if losses and production outrun remaining income. Track
mineral-bearing capacity, depletion, idle workers, replacement-base lead time,
reinforcement routes and reserves. A surviving Nexus is not necessarily a
productive mineral line. Scout a proposed replacement site; absent fogged
resource amounts are unknown, not proof of depletion. These are SC2 analogies
to operational endurance, not claims that military logistics equations apply.

ADP 5-0 paragraphs 5-13–19 distinguish measures of performance from measures of
effectiveness. Apply that distinction explicitly:

| Task/performance indicator | Effectiveness evidence |
| --- | --- |
| Scout reached the requested point | Decision-relevant evidence arrived before the response deadline at acceptable cost. |
| Robotics/counter unit completed | The counter arrived, could fire and contributed to the intended defense or attack. |
| Expansion order accepted | New income became available before old capacity failed. |
| Attack orders issued | The intended objective progressed, with sustainable losses and resolved outcomes. |

Confidence falling or rising alone is not effectiveness. Measure calibration
where independent truth is available; retain coverage, lead time, delivered
readiness, weapon participation and resolved wins alongside diagnostic trade
metrics. Sampled scores do not prove causation.

## Small, staged experiments

1. Log COAs, intent, decision questions and predicted outcomes in shadow mode.
   Test evidence aging, unknown resource amounts, interrupted inspection and
   ownership invariants synthetically.
2. Trial one decision-linked scouting question or counter-investment trigger in
   a frozen targeted triplet. Preserve 3600-second bounds and matching starts;
   reject poor candidates before broader regression.
3. Test weapon participation and income replacement separately. Record expected
   versus observed effects, then retain established winners before promotion.
4. Complete the [hardcoded milestone](hardcoded-elite-milestone.md), including
   community opponents and holdouts. Later, the [RL policy](rl-architecture.md)
   can consume the same beliefs and propose actions through the guarded plan
   decoder. Doctrine supplies structure; empirical SC2 evidence supplies the
   coefficients, thresholds and acceptance decision.
