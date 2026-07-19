"""Rule-based closure regulation for telos-f inquiry packets.

The regulator implements the inspectable Phase 5 decision table from
``project_explanation.md``.  It does not try to answer the inquiry itself;
instead, it classifies why closure has or has not been earned and returns a
``DecisionState`` with renderable metadata explaining why the system stopped,
continued, rolled back, or transferred judgment.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from telos_f.models import (
    ClaimStatus,
    ContinuityResult,
    Decision,
    DecisionState,
    InquiryPacket,
    PathStatus,
    RemainderOwner,
    RemainderType,
    ResolutionOption,
    Severity,
    StoppingCondition,
    TensionType,
    Uncertainty,
    UnresolvednessType,
)

# The project documentation sometimes names the aggregate state "InquiryState".
# Keep that spelling available without introducing a second runtime shape.
InquiryState = InquiryPacket


@dataclass(frozen=True, slots=True)
class ClosureRule:
    """An inspectable rule connecting a detected condition to closure action."""

    condition: str
    decision: Decision
    unresolvedness_type: UnresolvednessType
    stopping_condition: StoppingCondition | None
    reason: str
    next_actions: tuple[str, ...]


class ClosureRegulator:
    """Classify an inquiry state and choose the next closure operation.

    Rules are intentionally ordered.  Blocking failures that can make later
    output misleading—human ownership, path drift, incoherence, missing
    evidence, ambiguity, and value conflict—are evaluated before provisional
    resolution or preservation of coherent openness.
    """

    def decide(self, state: InquiryPacket | InquiryState) -> DecisionState:
        """Return a closure decision for an ``InquiryPacket``/``InquiryState``.

        The returned ``DecisionState`` includes a human-readable reason,
        unresolvedness classification, next actions, stopping condition, and
        metadata suitable for an expression layer to render "why the system
        stopped."
        """

        rule, evidence = self._select_rule(state)
        return DecisionState(
            id=f"closure-{uuid4()}",
            state=rule.decision,
            reason=rule.reason,
            unresolvedness_type=rule.unresolvedness_type,
            next_actions=list(rule.next_actions),
            stopping_condition=rule.stopping_condition,
            metadata={
                "condition": rule.condition,
                "why_stopped": rule.reason,
                "evidence": evidence,
                "rule_table_source": "project_explanation.md section 10, Phase 5",
                "inquiry_id": state.inquiry.id,
                "inquiry_goal": state.inquiry.goal,
            },
        )

    def __call__(self, state: InquiryPacket | InquiryState) -> DecisionState:
        """Alias for ``decide`` so the regulator can be used as a callable."""

        return self.decide(state)

    def _select_rule(self, state: InquiryPacket) -> tuple[ClosureRule, dict[str, object]]:
        if evidence := self._human_owned_judgment(state):
            return HUMAN_OWNED_JUDGMENT, evidence
        if evidence := self._path_drift(state):
            return PATH_DRIFT, evidence
        if evidence := self._incoherence(state):
            return INCOHERENCE, evidence
        if evidence := self._missing_evidence(state):
            return MISSING_EVIDENCE, evidence
        if evidence := self._ordinary_ambiguity(state):
            return ORDINARY_AMBIGUITY, evidence
        if evidence := self._competing_value_systems(state):
            return COMPETING_VALUE_SYSTEMS, evidence
        if evidence := self._coherent_openness(state):
            return COHERENT_OPENNESS, evidence
        if evidence := self._stable_factual_support(state):
            return STABLE_FACTUAL_SUPPORT, evidence
        return MISSING_EVIDENCE, {
            "defaulted": True,
            "message": "No rule supplied sufficient support for closure; investigate before resolving.",
        }

    def _human_owned_judgment(self, state: InquiryPacket) -> dict[str, object]:
        remainders = [r.id for r in state.remainders if r.belongs_to is RemainderOwner.HUMAN]
        return {"human_owned_remainders": remainders} if remainders else {}

    def _path_drift(self, state: InquiryPacket) -> dict[str, object]:
        drifted_paths = [p.id for p in state.paths if p.status is PathStatus.DRIFT_DETECTED]
        failed_steps = [
            {"path_id": path.id, "from": step.from_ref, "to": step.to_ref}
            for path in state.paths
            for step in path.steps
            if ContinuityResult.FAIL
            in (
                step.referential,
                step.relational,
                step.pragmatic,
                step.causal_or_argumentative,
                step.thematic,
                step.contextual,
                step.tonal,
                step.cue_dependence,
            )
        ]
        return {"drifted_paths": drifted_paths, "failed_steps": failed_steps} if drifted_paths or failed_steps else {}

    def _incoherence(self, state: InquiryPacket) -> dict[str, object]:
        tensions = [
            t.id
            for t in state.tensions
            if t.type in {TensionType.CONTRADICTION, TensionType.INCOMPATIBLE_INTERPRETATION}
            and t.severity is Severity.HIGH
        ]
        rejected_claims = [c.id for c in state.claims if c.status is ClaimStatus.RETRACTED]
        return {"high_severity_tensions": tensions, "retracted_claims": rejected_claims} if tensions else {}

    def _missing_evidence(self, state: InquiryPacket) -> dict[str, object]:
        remainders = [r.id for r in state.remainders if r.type is RemainderType.EVIDENCE_GAP]
        claims = [
            c.id
            for c in state.claims
            if c.uncertainty in {Uncertainty.HIGH, Uncertainty.UNRESOLVED}
            and not c.grounds
        ]
        evidence_conflicts = [t.id for t in state.tensions if t.type is TensionType.EVIDENCE_CONFLICT]
        return {"evidence_gap_remainders": remainders, "ungrounded_claims": claims, "evidence_conflicts": evidence_conflicts} if remainders or claims or evidence_conflicts else {}

    def _ordinary_ambiguity(self, state: InquiryPacket) -> dict[str, object]:
        remainders = [r.id for r in state.remainders if r.type is RemainderType.AMBIGUITY]
        tensions = [
            t.id
            for t in state.tensions
            if t.type is TensionType.INCOMPATIBLE_INTERPRETATION
            and ResolutionOption.DISAMBIGUATE in t.resolution_options
        ]
        interpretations = [i.id for i in state.interpretations if i.alternatives]
        return {"ambiguous_remainders": remainders, "disambiguation_tensions": tensions, "interpretations_with_alternatives": interpretations} if remainders or tensions or interpretations else {}

    def _competing_value_systems(self, state: InquiryPacket) -> dict[str, object]:
        tensions = [t.id for t in state.tensions if t.type is TensionType.COMPETING_VALUE]
        pluralism = [r.id for r in state.remainders if r.type is RemainderType.PLURALISM]
        return {"competing_value_tensions": tensions, "pluralism_remainders": pluralism} if tensions or pluralism else {}

    def _coherent_openness(self, state: InquiryPacket) -> dict[str, object]:
        remainders = [r.id for r in state.remainders if r.type is RemainderType.GENERATIVE_REMAINDER]
        has_anchor = bool(state.anchors)
        return {"generative_remainders": remainders, "anchor_count": len(state.anchors)} if remainders and has_anchor else {}

    def _stable_factual_support(self, state: InquiryPacket) -> dict[str, object]:
        supported_claims = [
            c.id
            for c in state.claims
            if c.status is ClaimStatus.ACCEPTED
            and c.uncertainty is Uncertainty.LOW
            and bool(c.grounds)
            and not c.counterevidence
        ]
        return {"supported_claims": supported_claims} if supported_claims and not state.tensions else {}


INCOHERENCE = ClosureRule(
    condition="incoherence",
    decision=Decision.REPAIR_OR_STOP,
    unresolvedness_type=UnresolvednessType.INCOHERENCE,
    stopping_condition=StoppingCondition.INCOHERENCE,
    reason="No stable shared interpretation is available; repair the state or stop rather than forcing closure.",
    next_actions=("repair contradictions", "request clarifying context", "stop if repair is unavailable"),
)
MISSING_EVIDENCE = ClosureRule(
    condition="missing evidence",
    decision=Decision.INVESTIGATE,
    unresolvedness_type=UnresolvednessType.EPISTEMIC_INSUFFICIENCY,
    stopping_condition=StoppingCondition.INSUFFICIENT_EVIDENCE,
    reason="The inquiry appears answerable, but current support is insufficient; investigate before resolving.",
    next_actions=("retrieve or request evidence", "test assumptions", "revise claims after evidence changes"),
)
ORDINARY_AMBIGUITY = ClosureRule(
    condition="ordinary ambiguity",
    decision=Decision.DISAMBIGUATE,
    unresolvedness_type=UnresolvednessType.SEMANTIC_AMBIGUITY,
    stopping_condition=None,
    reason="Multiple ordinary meanings remain live because the signal is under-specified; disambiguate before closure.",
    next_actions=("ask a clarifying question", "separate candidate readings", "choose only after context narrows meaning"),
)
COMPETING_VALUE_SYSTEMS = ClosureRule(
    condition="competing value systems",
    decision=Decision.CONTRAST,
    unresolvedness_type=UnresolvednessType.PERSPECTIVAL_OR_NORMATIVE_PLURALITY,
    stopping_condition=StoppingCondition.VALUE_CONFLICT,
    reason="Legitimate positions depend on different value commitments; contrast assumptions instead of collapsing them.",
    next_actions=("name value commitments", "contrast consequences", "mark unresolved normative choice"),
)
STABLE_FACTUAL_SUPPORT = ClosureRule(
    condition="stable factual support",
    decision=Decision.RESOLVE_PROVISIONALLY,
    unresolvedness_type=UnresolvednessType.NONE,
    stopping_condition=StoppingCondition.SUFFICIENT_RESOLUTION,
    reason="Accepted low-uncertainty claims have grounds and no live counterevidence; resolve provisionally.",
    next_actions=("render provisional answer", "state grounds", "name revision conditions"),
)
COHERENT_OPENNESS = ClosureRule(
    condition="coherent openness",
    decision=Decision.PRESERVE_OPENNESS,
    unresolvedness_type=UnresolvednessType.GENERATIVE_OPENNESS,
    stopping_condition=StoppingCondition.GENERATIVE_OPENNESS,
    reason="A shared anchor exists, but the remaining openness is generative; preserve the remainder for the receiver.",
    next_actions=("render shared anchor", "preserve remainder", "invite human completion without exhausting meaning"),
)
PATH_DRIFT = ClosureRule(
    condition="path drift",
    decision=Decision.ROLLBACK,
    unresolvedness_type=UnresolvednessType.INCOHERENCE,
    stopping_condition=StoppingCondition.INCOHERENCE,
    reason="The reasoning path has drifted from local continuity; roll back to the last stable point.",
    next_actions=("identify last rollback point", "discard drifted step", "resume from grounded anchor"),
)
HUMAN_OWNED_JUDGMENT = ClosureRule(
    condition="human-owned judgment",
    decision=Decision.TRANSFER_TO_HUMAN,
    unresolvedness_type=UnresolvednessType.GENERATIVE_OPENNESS,
    stopping_condition=StoppingCondition.HUMAN_JUDGMENT_REQUIRED,
    reason="The unresolved remainder belongs to human judgment; transfer rather than silently completing it.",
    next_actions=("mark human-owned remainder", "explain transfer", "offer structured options if useful"),
)
