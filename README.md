# Starcraft2Bot — human economy assistant

Play Protoss with your normal mouse and keyboard while an API bot manages your
economy and build-out. Army movement, attacks, control groups and rally points
remain yours. No screen capture, LLM, cloud service or model training is needed.

**Status:** implementation and automated tests; not yet validated in a live SC2
client. This mode launches a local real-time match against Blizzard's computer
opponent through the official SC2 API. It does not attach to Battle.net ladder,
campaign or Co-op matchmaking. The original autonomous bots remain in `source/`.

## Setup and launch

Use Python 3.10+ and a graphical Windows or macOS StarCraft II installation.
Blizzard's native Linux API package is headless and cannot provide the normal
human gameplay window. Linux + Wine is an unverified alternative; start with
Windows for the simplest supported graphical path.

Install an SC2 API-compatible melee map under your SC2 installation's `Maps/`
folder. The default is `AbyssalReefLE.SC2Map`; select another installed two-player
melee map with `--map`. The name must match your actual map file.

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
uv sync --locked
uv run --locked sc2-assistant --check-config --config config/assistant.example.json
uv run --locked sc2-assistant --map AbyssalReefLE --difficulty Medium --opponent Terran
```

`uv` uses Python 3.12 by default and installs the locked dependencies. No manual
virtual-environment activation is needed. A packaged `sc2-assistant` command and
`python -m source.run_assistant` are both available. For pip-only use, install
the project with `python -m pip install .` in a virtual environment.

Run from the repository root. For a nonstandard installation, set `SC2PATH` to
the game installation root before launching. Use
`--config config/assistant.example.json` to load startup settings.
`--replay replays/my-game.SC2Replay` selects an explicit replay destination;
otherwise each match uses a unique timestamped filename under `replays/`.
Rotating logs are written to `logs/assistant.log`; use `--log-level DEBUG` for
detailed console output. Both destinations can be changed with CLI options.

The launcher starts **one shared Protoss participant**, not a separate allied
bot. Click into the window and play. It uses `realtime=True` and
`raw_affects_selection=False` so API actions restore your selection. Startup
chat and the top-left HUD show the assistant state.

## Default responsibilities

| Assistant | Human |
| --- | --- |
| Probes, idle workers, mineral/gas balancing | Army movement, targets and engagements |
| Pylons and assimilators | Control groups and production rally points |
| Expansion up to three bases when worker count permits | Overall tactics and manual interventions |
| Gateway/Cybernetics Core/Robotics tech and scaled Gateways | Selecting optional abilities to delegate |
| Replenishment to configured unit targets | Selected or explicitly released units/buildings |
| Ground weapons/armor/shields level 1 and Chrono Boost | All combat abilities by default |

Default composition targets: 12 Zealots, 40 Stalkers, 2 Sentries and 6 Immortals.
These are upper targets, not a promise they all fit below 200 supply. Set a target
to zero to stop producing that type. High Templar, Colossi and Void Ray targets
trigger their tech chains when construction is enabled. Expansion saves 400
minerals from lower-priority construction, upgrades and army production;
workers, gas and supply still have priority. User reserves always apply,
including to supply, so a large reserve can intentionally stall the assistant.

## In-game toggles

Press Enter, type a command, and press Enter again. Only chat from your player
is accepted. Commands are case-insensitive. Settings apply to new orders;
they do not cancel queued production or an already issued spell.

```text
!assist help
!assist status
!assist pause
!assist resume
!assist economy off
!assist economy on
!assist expansion off
!assist production off
!assist reserve 400 100
!assist reserve 0 0
!assist set bases 4
!assist set stalkers 30
!assist set high_templar 4
!assist storm on
!assist feedback on
!assist guardian_shield on
!assist blink on
!assist voidray_alignment on
!assist chrono off
!assist spells off
!assist hud off
```

Every boolean in the example JSON accepts `!assist <name> on/off`. `economy`
toggles workers, allocation, supply, gas, expansion, construction, production
and upgrades together. `spells` toggles the five combat abilities together;
Chrono remains independent. `pause` stops all new automation. `set` changes a
numeric setting. Changes are session-only.

**Ownership:** selected units/buildings are temporarily excluded. Select units
then enter `!assist release` to exclude them until `!assist claim` on that
selection or `!assist claim-all`. Use this for scout/build probes or casters you
want manual after deselecting. Workers with move, attack or construction orders
are also left alone. Existing orders continue when you select, release, pause
or disable a feature; override them with normal game commands. Observation
latency means a simultaneous click can still race an assistant command, so
explicit release is the stronger handover.

## Optional powers

| Toggle | Behavior and limits |
| --- | --- |
| `chrono` (on) | Chrono Boost a busy eligible structure; one cast per observation |
| `guardian_shield` | Sentry shield with at least three nearby ground combat units and a nearby ranged threat |
| `feedback` | Feedback on a visible enemy with at least 50 energy already within range |
| `storm` | Storm clusters of at least three visible enemies in range; reject nearby friendlies and recent overlapping assistant storms |
| `blink` | Defensive Stalker Blink toward a Nexus when shields are depleted and health is low; visible/pathable destination farther from nearby threats |
| `voidray_alignment` | Prismatic Alignment while attacking with an armored enemy in weapon range |

Combat abilities default **off**. Available-ability queries check energy,
cooldowns and research. Storm/Blink research is requested when their toggle and
upgrades are enabled; High Templar production requires a nonzero `high_templar`
target. Existing casters can be assisted without enabling their production.
Spells never chase a target. Blink intentionally repositions a unit, and any
enabled spell can interrupt its current attack/movement order. Storm avoidance
only knows current positions: allies can still move into a storm. These are
conservative heuristics, not expert micro or guarantees of good play.

This version does not automate Warp Gate morphing/warp-ins, Force Fields,
Disruptor Novas, Oracle abilities, Archon merging or higher-tier weapon upgrades.
Manually morphed Warp Gates remain human-managed.

## Validation

```bash
uv sync --locked
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy
uv run --locked pytest --cov
uv run --locked sc2-assistant --help
uv build
```

Tests use synthetic protocol data and fake observations with the installed
BurnySC2 SDK. They cannot establish graphical client compatibility or match
performance. Complete the [live checklist](docs/assistant-live-test.md) before
treating this as ready for regular play.

See [CONTRIBUTING.md](CONTRIBUTING.md) for architecture, dependency updates,
pre-commit setup, CI coverage and the boundary between new and legacy code.

## References and legacy code

- [Blizzard SC2 API](https://github.com/Blizzard/s2client-proto): raw state/actions and tool-assisted human play.
- [Shared selection setting](https://github.com/Blizzard/s2client-proto/blob/master/s2clientprotocol/sc2api.proto): `InterfaceOptions.raw_affects_selection`.
- [BurnySC2](https://github.com/BurnySc2/python-sc2): Python SDK, pinned to 7.3.0.
- [Blizzard Linux package](https://github.com/Blizzard/s2client-proto/blob/master/docs/linux.md): headless research client.
- Original tutorial: [Sentdex SC2 series](https://pythonprogramming.net/starcraft-ii-ai-python-sc2-tutorial/).

`source/run_SC2_game.py`, `source/setup_sc2_bot.py` and `source/ThreeBaseVoidRay.py`
are preserved as legacy autonomous examples. Their old interfaces have not been
migrated or validated by the assistant tests; use the new launcher above.

