# Local LLM strategist options

## Purpose

Evaluate how to add a local language model as a slow strategic advisor for the
human-controlled SC2 assistant. The model may recommend a tactical mode and a
brief explanation from locally observed state. It must not issue SC2 actions,
manage units directly, or delay the game loop.

This is a design proposal. It does not add a model runtime, dependency, or live
integration.

## Existing boundaries

The assistant owns the only SC2 API connection. Every five wall-clock seconds,
after an observation, it writes a sampled state record to
`logs/runtime-<session>.state.jsonl`. The record includes the observed player
state, available abilities, tactical decision, settings, and relevant events.

The existing strategy-script hook accepts a JSON context and returns a strict
plan containing `strategy`, `reason`, and optional map target. It is launched as
a fresh process with a one-second timeout for each evaluation. This is suitable
for deterministic Python policies, but not for loading a local model or waiting
for inference. Model work must therefore happen asynchronously outside the SC2
observation/action path.

The supported strategic modes are `defend`, `regroup`, `push`, and `retreat`.
The current deterministic auto policy handles local threats, force readiness,
and retreats. The model should advise only where that existing policy leaves
room for a slower campaign-level choice.

## Options

| Option | Shape | Advantages | Costs and risks | Use |
| --- | --- | --- | --- | --- |
| A. Offline session analyst | Read completed state JSONL and replay/session report; generate a post-match summary or next-match policy suggestion | Safest; no runtime coupling or latency; useful for prompt and state design | Cannot affect current match; replay interpretation is separate work | Start here to measure what information is useful |
| B. Asynchronous local strategist sidecar | Persistent local process watches a compact state mailbox, runs a local model, and writes a versioned recommendation mailbox | Model stays warm; slow inference is isolated; can skip stale samples and retain last valid recommendation | Requires process lifecycle, IPC, validation, freshness and failure behavior | Preferred live architecture after offline evaluation |
| C. Persistent in-process model client | Load model in the assistant process and schedule inference outside tactical ticks | Fewer processes and direct access to state | Model imports/resources can destabilize SC2 runtime; cancellation and shutdown become coupled; hard to isolate stalls | Avoid for first integration |
| D. Run the current strategy script with an LLM | Invoke model from the existing per-evaluation script | Small apparent integration | Fresh process/load overhead and one-second timeout conflict with local inference; a slow call can fail every sample | Do not use as the runtime design |

## Recommended direction

Use a two-stage path: begin with **A** to establish whether sampled state supports
useful strategic advice, then implement **B** behind an opt-in setting. Keep the
LLM advisory and low-frequency. Deterministic tactical logic remains responsible
for immediate defense, retreat, wave assembly, and issuing orders.

### Sidecar flow

1. The assistant publishes a compact, versioned strategist input after each
   existing state sample. Include session ID, monotonically increasing sample
   number, captured time, game loop, map bounds, current mode/reason, resources,
   supply and army composition, bases/workers, known enemy sightings, pending
   wave/readiness data, and only the events needed to judge a campaign change.
2. A persistent sidecar watches the latest input. It may coalesce samples while
   busy and should prefer the newest sample over building an inference backlog.
3. The sidecar builds a bounded prompt from the compact state and calls a
   configurable local inference endpoint or local model runner. Keep the model
   adapter replaceable; do not bind the assistant to one vendor protocol in the
   first design.
4. The model returns a small structured recommendation, not prose-only control:
   schema version, source sample number, mode (`defend`, `regroup`, `push`, or
   `retreat`), optional objective category, confidence, and a short rationale.
   It cannot return coordinates, unit tags, abilities, chat commands, or raw
   SC2 orders.
5. The assistant reads the latest recommendation at a safe strategy decision
   point, validates its schema and session/sample identity, and applies it only
   if it is fresh. Existing safety gates and ownership rules still decide
   whether an order can be issued.

Prefer named objective categories (home defense, rally, known enemy base,
known expansion) over model-generated coordinates. The assistant resolves a
category into a currently valid in-bounds target using its own observed state.

### Timing and freshness

- Keep the current five-second observation/state sampling unchanged.
- Start with a model decision cadence of 30 seconds, with optional event-triggered
  requests for a newly observed attack or a major army/wave transition.
- Allow one inference in flight. Replace pending input with the newest sample;
  never queue every sample.
- Configure a bounded inference budget (initial target: up to 20 seconds). If a
  recommendation misses its budget or is older than the configured freshness
  window (initial target: 45 seconds or 9 sampled records), ignore it.
- Preserve the last valid recommendation only while it remains fresh. On expiry,
  model error, malformed output, missing sidecar, or disabled setting, use the
  deterministic `auto` strategy.
- An immediate local threat, depleted/outmatched army, explicit manual mode,
  pause, or attack-disabled state always takes precedence over the model.

These timings are starting values for evaluation, not performance claims. Measure
end-to-end inference latency on the user's target PC before choosing a model.

## Safety and ownership

- Model output is a hint to the tactical strategy selector; it is never an API
  action or arbitrary strategy script.
- Keep selection preservation, released-unit exclusions, ownership checks, and
  pause behavior unchanged. A selected or released unit cannot become model-owned.
- Continue to require existing wave assembly, scouting, composition, and local
  threat gates before a push becomes unit orders.
- Retreat and defend choices can be strengthened by deterministic safety rules;
  the model must not suppress them.
- Combat abilities remain individually opt-in. The model cannot enable spells or
  issue abilities.
- Treat observations and any future opponent text/chat as untrusted data. Do not
  place external text into privileged instructions or permit it to request
  arbitrary code, shell commands, file access, or network access.
- Keep model endpoint local by default. The runtime must not silently upload
  snapshots or replays to an external service.

## Model and prompt strategy

Do not select a model by parameter count alone. Benchmark candidate local models
on the actual Windows machine for cold start, warm response latency, memory use,
structured-output reliability, and strategic usefulness. Keep inference settings
and model identifier in explicit local configuration; do not fetch model weights
at game launch.

Feed a concise strategic summary, not the full raw protobuf observation. Preserve
raw state in existing local logs for audit, but extract only decision-relevant
facts for model input. Include the current deterministic recommendation and its
reason so the model can advise a change instead of reconstructing every tactical
fact. Do not ask it to calculate DPS, simulate combat, or infer hidden fog-of-war
state from absent data.

Use structured JSON output with strict local validation. Reject unknown fields,
unknown modes, invalid confidence values, mismatched session/sample IDs, and
outputs that exceed size limits. The rationale is diagnostic only and is never
executed.

## Configuration and operation

Keep this opt-in. An eventual configuration could expose:

- `llm_strategist.enabled` (default false)
- `llm_strategist.endpoint` (loopback only by default)
- `llm_strategist.model` (explicit local model name)
- `llm_strategist.interval_seconds` (initially 30)
- `llm_strategist.timeout_seconds` (initially 20)
- `llm_strategist.max_recommendation_age_seconds` (initially 45)

These names and defaults are proposals. The normal assistant must start and run
when the sidecar or model is absent. Provide an explicit status indicator showing
last input sample, last successful recommendation, its age, and fallback reason.
A manual control command should disable the advisor immediately without changing
existing pause, attack, selection, or spell semantics.

Prefer an explicit user-managed model service initially. If a later launcher
starts or stops the sidecar, follow the documented Windows setup/launch stages
and preserve handoffs; do not silently download weights or change SC2 install
selection.

## Evaluation plan

1. **Offline evidence:** replay recorded session snapshots through candidate
   prompts and compare recommendations with the deterministic strategy and
   observed outcomes. Include ties, failed pushes, base raids, retreat cases, and
   fog-of-war cases. Do not use replay/API success as evidence that human input
   works.
2. **Policy quality:** compare against deterministic auto on identical recorded
   inputs. Track safe-mode violations, stale recommendations, recommendation
   changes, invalid JSON, and whether a recommendation was actionable with
   currently known information.
3. **Runtime cost:** measure warm/cold latency and memory on target hardware.
   Confirm inference never blocks the SC2 loop and that stale work is discarded.
4. **Synthetic integration:** test version/schema validation, wrong session,
   stale sample, timeout, sidecar exit, malformed response, coalescing, manual
   disable, and deterministic fallback without launching SC2.
5. **Live acceptance:** only after synthetic and offline evaluation, use the
   Windows live checklist. Record the exact ping binary/data identity and human
   input checks. If desktop access is unavailable, record live validation as
   pending rather than inferring it from logs or API responses.

## Suggested implementation sequence

1. Add a compact strategist-input schema and an offline replay/evaluation tool;
   do not change live decisions.
2. Benchmark a small set of locally available inference runtimes/models with a
   representative prompt and record latency, memory, and structured-output
   compliance.
3. Define sidecar mailbox/process lifecycle and freshness policy; test the pure
   input/output validator independently.
4. Add opt-in advisor configuration and a non-blocking recommendation reader
   with deterministic fallback. Keep the current auto strategy as default.
5. Complete offline comparisons, then live Windows acceptance before considering
   any default change.

## Open decisions for implementation

- Which local inference runtime is already installed or preferred on the target
  Windows PC?
- What model size fits alongside SC2 without harming frame/step throughput?
- Should the advisor recommend only a strategy mode initially, or also choose
  among named strategic objectives?
- Is 30 seconds useful after measuring model latency and observing game pace?

Resolve these with measured target-machine data. No model or runtime should be
chosen solely from generic hardware assumptions.
