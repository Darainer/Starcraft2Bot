# Live acceptance checklist — pending

No live SC2 match was available in the development environment. Record the
SC2 version, OS, Python version, map, result and replay for these checks.

1. Launch `python -m source.run_assistant --difficulty Easy`. Confirm a graphical
   window, normal camera/mouse/hotkeys and real-time progression.
2. Select combat units and issue move/attack orders while probes and pylons are
   produced. Confirm selection and camera are retained.
3. Run `!assist pause`. Confirm no new assistant commands after it is processed.
   Existing orders may complete. Resume and verify macro.
4. Toggle workers, supply, gas, construction, production, upgrades and expansion
   separately. Verify each stops its own new orders without changing others.
5. Set `!assist reserve 400 100`. Observe that assistant purchases leave that
   balance. Human spending can reduce it. Clear with `!assist reserve 0 0`.
6. Select a probe, `!assist release`, deselect and scout/build. Confirm it is not
   reassigned. Claim it and confirm eligibility. Check selected production
   buildings do not receive new production commands.
7. Reach three bases and observe gas saturation, replacement workers, supply
   recovery, tech construction and continued reinforcements.
8. Set `high_templar` to 4; enable Storm and Feedback and allow research. Verify
   actual spell effects. Confirm friendlies block Storm targeting and
   selected/released casters are not given casts. Check no out-of-range chasing.
9. Independently test Guardian Shield, Blink and Void Ray Alignment. Check
   toggles stop new casts and review action errors/replays for repeated casts.
10. Destroy the last Nexus; test rebuild with surviving probes, a lost
    expansion, exhausted mineral line and supply cap at 200.
11. End the match and verify replay saving. Record failures as reproducible
    scenarios before broadening automation.

Acceptance requires the relevant scenarios in the actual graphical client.
Passing synthetic tests is not a substitute for these checks.
