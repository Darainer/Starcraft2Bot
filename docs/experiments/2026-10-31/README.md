# Production recovery candidate — 2026-10-31

`production-v5-r1.patch` is the complete candidate delta against `9fd64a1`.
Apply it only to a separate clean checkout of that revision:

```powershell
git apply production-v5-r1.patch
```

It reconciles the archived v5 integration with the later scoped gas reservation.
The checkpoint's independent scouting retry draft is deliberately absent: this
candidate retains the same baseline scouting as the previously evaluated v4.
It also includes current reporting, the eight-client trial ceiling, corrected
synthetic production costs and the Python-module Windows entry points.

`scouting-retry-unpromoted.patch` separately preserves the checkpoint's scouting
retry source and tests against `9fd64a1`. It is not part of either evaluated
production candidate; keep it separate until it earns its own matched trial.

The [manifest](production-v5-r1-manifest.json) records source/configuration hashes,
archive inputs, map hash, fixed settings and software validation. Raw logs,
runtime reports, replays and installation paths remain ignored and local.
Git patch application can normalize line endings; compare source text after
normalizing newlines if comparing an applied archive to raw-byte run hashes.

The original failing gas-release test assigned a Robotics Facility two supply.
BurnySC2 therefore treated production as a morph and subtracted the producer's
price, leaving a computed zero-gas Immortal. Correcting structure supply and
explicit Robotics prices makes the test meaningful. Added assertions check
275 minerals / 100 gas / 4 supply independently, actual resource charging,
reservation revocation, and a real reinforcement-controller call before and
after first-Immortal training. Test cases no longer patch unit prices or derive
their expected spending from the implementation under test.

Software checks: locked sync, Ruff lint/format, configured mypy, **452 tests with
92.74% coverage**, source/wheel builds. The historical v5 archive and its stopped
status remain unchanged; this is a new candidate identity with separate evidence.

R1 lost all three matched Zerg Macro games (875.4 / 815.4 / 875.4 sampled game
seconds) and is **rejected**. Starts, unchanged source and nonempty replays were
verified; no retention or full-matrix games were launched for it. See the
[targeted report](../../evaluations/2026-10-31-production-v5-r1-zerg-macro.md).

`production-v5-r2.patch` is another complete delta against clean `9fd64a1`, not
an incremental patch on R1. Its only gameplay change from R1 makes the opening's
priority Gateway/Core path try every safe ready Pylon in distance order, matching
the existing general construction path. The captured Macro opening had two
Zealots, two Gateways, two Pylons and over 1,000 minerals, but no Core at 170.4s.
The nearest Pylon's placement was blocked; the later general construction path
built at rear power after the 180-second opening bound. A regression test uses
the captured structure coordinates and a blocked front/usable rear placement
query to exercise real construction and spending through `macro()`.

R2 passed **453 tests with 92.78% coverage** and the full locked software checks.
Its [Macro triplet](../../evaluations/2026-10-31-production-v5-r2-zerg-macro.md)
won **3/3** at 1055.4 sampled game seconds. Rush, Power and both Air retention
triplets also won 3/3 (15/15 across five fixed conditions). Broader regression
evaluation is in progress. The main working tree now adopts R2 gameplay with the
later UUID trial-runner fix. No shared human-control acceptance is implied; see the
[runtime recheck](../../evaluations/2026-10-31-runtime.md).

The archives retain the exact evaluated runner. Two simultaneous retention
invocations collided on its timestamp-only artifact names; those six attempts
are explicitly invalid/aborted and excluded. Stagger runner starts when using
the archived version. The main checkout has the later UUID naming fix, tested
with two runners sharing one clock value; it changes artifact naming only.
