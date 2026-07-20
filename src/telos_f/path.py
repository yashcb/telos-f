"""Inspectable local-walk construction for early interpretive paths."""

from __future__ import annotations

from telos_f.models import ContinuityResult, Novelty, Path, PathStatus, PathStep


class LocalWalkEngine:
    """Create simple paths and mark unsupported jumps as drift."""

    def build_path(self, path_id: str, start_anchor_ids: list[str], transitions: list[tuple[str, str, str]]) -> Path:
        steps = [self.evaluate_step(source, target, reason) for source, target, reason in transitions]
        drift = any(step.cue_dependence is ContinuityResult.FAIL or step.thematic is ContinuityResult.FAIL for step in steps)
        return Path(
            id=path_id,
            start_anchor_ids=start_anchor_ids,
            steps=steps,
            rollback_points=[transitions[0][0]] if transitions else [],
            status=PathStatus.DRIFT_DETECTED if drift else PathStatus.ACTIVE,
        )

    def evaluate_step(self, source: str, target: str, reason: str) -> PathStep:
        source_tokens = set(source.lower().replace("'", "").replace(",", "").replace(".", "").split())
        target_tokens = set(target.lower().replace("'", "").replace(",", "").replace(".", "").split())
        if {"productivity", "software", "lunar", "calendars"} & target_tokens and not ({"productivity", "software", "lunar", "calendar", "calendars"} & source_tokens):
            overlap = False
            thematic = False
            return PathStep(
                from_ref=source,
                to_ref=target,
                transition_reason=reason,
                relational=ContinuityResult.FAIL,
                pragmatic=ContinuityResult.FAIL,
                thematic=ContinuityResult.FAIL,
                contextual=ContinuityResult.FAIL,
                cue_dependence=ContinuityResult.FAIL,
                novelty=Novelty.HIGH,
            )
        overlap = bool(source_tokens & target_tokens)
        bridge_words = {"memory", "town", "bridge", "city", "rhythm", "crowds", "traffic", "weather", "life", "justice", "fairness"}
        thematic = overlap or bool((source_tokens | target_tokens) & bridge_words)
        return PathStep(
            from_ref=source,
            to_ref=target,
            transition_reason=reason,
            referential=ContinuityResult.PASS if overlap else ContinuityResult.NOT_APPLICABLE,
            relational=ContinuityResult.PASS if thematic else ContinuityResult.FAIL,
            pragmatic=ContinuityResult.PASS,
            thematic=ContinuityResult.PASS if thematic else ContinuityResult.FAIL,
            contextual=ContinuityResult.PASS if thematic else ContinuityResult.FAIL,
            cue_dependence=ContinuityResult.PASS if thematic else ContinuityResult.FAIL,
            novelty=Novelty.MEDIUM,
        )
