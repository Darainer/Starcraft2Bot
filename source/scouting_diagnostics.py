"""Describe information availability separately from coarse-label model errors."""

from collections import defaultdict

from source.opponent_strategy import LABELS


class ScoutingDiagnostics:
    def __init__(self, reference=None):
        self.reference = reference if reference in LABELS else None
        self.previous = None
        self.duration = defaultdict(float)
        self.correct = defaultdict(float)
        self.committed = defaultdict(float)
        self.brier = defaultdict(float)
        self.first_facts = {}
        self.examples = []
        self.first_correct = None

    def observe(self, facts, prediction):
        now = facts["time_seconds"]
        if self.previous is not None:
            before, groups, correct, committed, brier = self.previous
            elapsed = now - before
            if elapsed <= 0:
                raise ValueError("Diagnostic observations must advance")
            for group in groups:
                covered = max(0, min(now, 240) - before) if group.startswith("opening/") else elapsed
                self.duration[group] += covered
                self.correct[group] += covered * correct
                self.committed[group] += covered * committed
                self.brier[group] += covered * brier
        present = facts["fact_presence"]
        for name, value in present.items():
            if value:
                self.first_facts.setdefault(name, now)
        groups = ["all", *(name for name, value in present.items() if value)]
        if not (
            present.get("fresh_army_contact", present["fresh_force"])
            or present["fresh_technology"]
            or present["fresh_expansion"]
        ):
            groups.append("no_fresh_relevant_evidence")
        groups += [f"opening/{group}" for group in groups] if now < 240 else []
        correct = self.reference is not None and prediction["category"] == self.reference
        committed = prediction["category"] != "Unknown"
        brier = (
            sum((prediction["probabilities"][label] - (label == self.reference)) ** 2 for label in LABELS)
            if self.reference is not None
            else 0
        )
        if correct and self.first_correct is None:
            self.first_correct = now
        if self.reference is not None and not correct and len(self.examples) < 12:
            signature = (prediction["category"], prediction["leading_hypothesis"], tuple(present.values()))
            if all(tuple(example["signature"]) != signature for example in self.examples):
                self.examples.append(
                    {
                        "time": now,
                        "signature": signature,
                        "fact_presence": present,
                        "evidence": prediction["evidence"],
                    }
                )
        self.previous = now, groups, correct, committed, brier

    def result(self):
        return {
            "first_fresh_fact_seconds": self.first_facts,
            "first_correct_label_seconds": self.first_correct,
            "strata": {
                key: {
                    "recorded_seconds": seconds,
                    "accuracy": self.correct[key] / seconds if self.reference is not None else None,
                    "commitment_coverage": self.committed[key] / seconds,
                    "conditional_accuracy": self.correct[key] / self.committed[key]
                    if self.reference is not None and self.committed[key]
                    else None,
                    "brier": self.brier[key] / seconds if self.reference is not None else None,
                }
                for key, seconds in sorted(self.duration.items())
                if seconds
            },
            "error_examples": self.examples,
            "scope": "Overlapping observed-fact strata; configured build is a weak evaluation label. Conditional errors describe logic/data gaps, not a causal information ceiling.",
        }
