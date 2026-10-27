# Experimental source archive

These unified patches preserve the session's candidate source and tests. They are
review artifacts, not enabled features or promoted policies. Apply a patch only
to a **separate clean checkout of `9fd64a1`**, never on top of this checkpoint or
another candidate. Candidate patches are complete deltas from that common base.
They use zero-context hunks: apply with `git apply --unidiff-zero <candidate>.patch`.

See [session closeout](../../session-closeout-2026-10-27.md) for measured outcomes,
failed approaches and limitations. `index.json` lists archived candidates.

`integrated-v5.patch` preserves the earlier staged investment version.
`integrated-v5-gas-unfinished.patch` preserves the latest differing macro and its
focused tests. **One focused test is failing; neither version is promoted or live
validated.** `integrated-v5-status.json` records the stopped work and source hashes.
Some candidate tests originated in staging harnesses; normalize test import paths
in the separate checkout as necessary. Raw live evidence remains local.
