"""Typed ontology models for the telos-f inquiry state.

The models in this module mirror section 5 of ``project_explanation.md``:
rather than treating all system state as undifferentiated text, they separate
claims, interpretations, paths, tensions, remainders, and closure decisions so
that each object can carry the validity conditions appropriate to its role.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Stakes(StrEnum):
    """Material significance of an inquiry for closure regulation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RequestedAction(StrEnum):
    """Operation requested by the inquiry initiator."""

    ANSWER = "answer"
    INTERPRET = "interpret"
    INVESTIGATE = "investigate"
    COMPARE = "compare"
    CREATE = "create"
    DECIDE = "decide"
    EXPLORE = "explore"


class ClosurePolicy(StrEnum):
    """Preferred policy for deciding when closure has been earned."""

    RESOLVE = "resolve"
    PRESERVE_OPEN = "preserve_open"
    INVESTIGATE_FIRST = "investigate_first"
    CONTRAST = "contrast"
    ASK_USER = "ask_user"
    AUTO = "auto"


class AnchorType(StrEnum):
    """Kinds of constraints that can ground an inquiry."""

    LINGUISTIC_CONVENTION = "linguistic_convention"
    OBSERVED_FACT = "observed_fact"
    SOURCE = "source"
    DOMAIN_RULE = "domain_rule"
    USER_CONTEXT = "user_context"
    DECLARED_VALUE = "declared_value"
    ACCEPTED_CLAIM = "accepted_claim"


class Strength(StrEnum):
    """Qualitative support strength used for anchors and interpretations."""

    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"


class Uncertainty(StrEnum):
    """Degree of uncertainty attached to a revisable claim."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNRESOLVED = "unresolved"


class ClaimStatus(StrEnum):
    """Lifecycle state for a claim under fallibilist revision."""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    CHALLENGED = "challenged"
    RETRACTED = "retracted"
    SUSPENDED = "suspended"


class InterpretationStatus(StrEnum):
    """Lifecycle state for a possible understanding of a source signal."""

    PROPOSED = "proposed"
    RETAINED = "retained"
    REJECTED = "rejected"
    HUMAN_OWNED = "human_owned"


class ContinuityResult(StrEnum):
    """Whether a local transition satisfies a continuity dimension."""

    PASS = "pass"
    FAIL = "fail"
    NOT_APPLICABLE = "not_applicable"


class Novelty(StrEnum):
    """How much new material a path step introduces."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PathStatus(StrEnum):
    """State of a connected path through claims or interpretations."""

    ACTIVE = "active"
    COMPLETE = "complete"
    ROLLED_BACK = "rolled_back"
    DRIFT_DETECTED = "drift_detected"


class TensionType(StrEnum):
    """Kinds of currently unharmonized relations."""

    CONTRADICTION = "contradiction"
    COMPETING_VALUE = "competing_value"
    INCOMPATIBLE_INTERPRETATION = "incompatible_interpretation"
    UNRESOLVED_ASSUMPTION = "unresolved_assumption"
    EVIDENCE_CONFLICT = "evidence_conflict"


class Severity(StrEnum):
    """Relative importance of a tension."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ResolutionOption(StrEnum):
    """Available operations for addressing a tension."""

    INVESTIGATE = "investigate"
    DISAMBIGUATE = "disambiguate"
    CONTRAST = "contrast"
    SUSPEND = "suspend"
    ROLLBACK = "rollback"
    ASK_USER = "ask_user"


class RemainderType(StrEnum):
    """Forms of content that remain unresolved after inquiry work."""

    EVIDENCE_GAP = "evidence_gap"
    AMBIGUITY = "ambiguity"
    PLURALISM = "pluralism"
    OPEN_QUESTION = "open_question"
    GENERATIVE_REMAINDER = "generative_remainder"


class RemainderOwner(StrEnum):
    """Who owns or must complete a remainder."""

    SYSTEM = "system"
    HUMAN = "human"
    SHARED = "shared"
    EXTERNAL_EVIDENCE = "external_evidence"


class Decision(StrEnum):
    """The closure regulator's current posture."""

    RESOLVE = "resolve"
    RESOLVE_PROVISIONALLY = "resolve_provisionally"
    CONTINUE = "continue"
    INVESTIGATE = "investigate"
    DISAMBIGUATE = "disambiguate"
    CONTRAST = "contrast"
    SUSPEND = "suspend"
    ROLLBACK = "rollback"
    PRESERVE_OPENNESS = "preserve_openness"
    ASK_USER = "ask_user"
    REPAIR_OR_STOP = "repair_or_stop"
    TRANSFER_TO_HUMAN = "transfer_to_human"


class UnresolvednessType(StrEnum):
    """Taxonomy of what remains unresolved in the current state."""

    INCOHERENCE = "incoherence"
    EPISTEMIC_INSUFFICIENCY = "epistemic_insufficiency"
    SEMANTIC_AMBIGUITY = "semantic_ambiguity"
    PERSPECTIVAL_OR_NORMATIVE_PLURALITY = "perspectival_or_normative_plurality"
    GENERATIVE_OPENNESS = "generative_openness"
    NONE = "none"


class StoppingCondition(StrEnum):
    """Why the system has stopped or is prepared to stop."""

    SUFFICIENT_RESOLUTION = "sufficient_resolution"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    VALUE_CONFLICT = "value_conflict"
    GENERATIVE_OPENNESS = "generative_openness"
    RESOURCE_LIMIT = "resource_limit"
    INCOHERENCE = "incoherence"
    HUMAN_JUDGMENT_REQUIRED = "human_judgment_required"


@dataclass(slots=True)
class Inquiry:
    """The object being explored: goal, context, stakes, and closure policy.

    In the ontology, an ``Inquiry`` is the current target of regulation. It
    records what is being asked, why it matters, which resources are available,
    and which closure policy should guide—but not override—the system's work.
    """

    id: str
    goal: str
    domain: str
    context: str | None
    stakes: Stakes
    requested_action: RequestedAction
    closure_policy: ClosurePolicy
    available_resources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class Anchor:
    """A grounding constraint shared by, supplied to, or accepted in inquiry.

    ``Anchor`` maps to the ontology's common ground: conventions, facts,
    sources, domain rules, user-supplied experiences, values, or prior accepted
    claims that constrain later claims, interpretations, and path transitions.
    """

    id: str
    type: AnchorType
    content: str
    provenance: str
    strength: Strength


@dataclass(slots=True)
class Claim:
    """A revisable proposition with grounds, scope, and revision traces.

    This model operationalizes fallibilism from the ontology: claims are not
    bare assertions, but propositions conditional on grounds, sources,
    assumptions, dependencies, counterevidence, uncertainty, and revision
    history.
    """

    id: str
    proposition: str
    grounds: list[str] = field(default_factory=list)
    source: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    scope: str = ""
    dependencies: list[str] = field(default_factory=list)
    counterevidence: list[str] = field(default_factory=list)
    uncertainty: Uncertainty = Uncertainty.UNRESOLVED
    revision_history: list[str] = field(default_factory=list)
    status: ClaimStatus = ClaimStatus.PROPOSED


@dataclass(slots=True)
class Interpretation:
    """A possible understanding whose quality is contextual, not merely true.

    ``Interpretation`` maps to the hermeneutic portion of the ontology: a
    reading is assessed by fidelity to the source signal, contextual fit,
    relational continuity, explanatory power, horizon or perspective, and live
    alternatives rather than by factual truth alone.
    """

    id: str
    signal_ref: str
    reading: str
    fidelity_to_source_signal: Strength
    contextual_fit: Strength
    relational_continuity: Strength
    explanatory_power: Strength
    horizon_or_perspective: str | None = None
    alternatives: list[str] = field(default_factory=list)
    status: InterpretationStatus = InterpretationStatus.PROPOSED


@dataclass(slots=True)
class PathStep:
    """One locally connected transition in a path of reasoning or reading.

    A ``PathStep`` preserves how the system moved from one claim or
    interpretation to another, exposing continuity dimensions so drift,
    arbitrary association, and unsupported novelty can be detected.
    """

    from_ref: str
    to_ref: str
    transition_reason: str
    referential: ContinuityResult = ContinuityResult.NOT_APPLICABLE
    relational: ContinuityResult = ContinuityResult.NOT_APPLICABLE
    pragmatic: ContinuityResult = ContinuityResult.NOT_APPLICABLE
    causal_or_argumentative: ContinuityResult = ContinuityResult.NOT_APPLICABLE
    thematic: ContinuityResult = ContinuityResult.NOT_APPLICABLE
    contextual: ContinuityResult = ContinuityResult.NOT_APPLICABLE
    tonal: ContinuityResult = ContinuityResult.NOT_APPLICABLE
    cue_dependence: ContinuityResult = ContinuityResult.NOT_APPLICABLE
    novelty: Novelty = Novelty.LOW


@dataclass(slots=True)
class Path:
    """A sequence of locally connected movements through typed state.

    ``Path`` maps to the ontology's requirement to show how inquiry arrived at
    claims or interpretations. It begins from anchors, records each transition,
    and keeps rollback points for revision when drift or incoherence appears.
    """

    id: str
    start_anchor_ids: list[str]
    steps: list[PathStep] = field(default_factory=list)
    rollback_points: list[str] = field(default_factory=list)
    status: PathStatus = PathStatus.ACTIVE


@dataclass(slots=True)
class Tension:
    """An unharmonized relation that blocks simple closure.

    ``Tension`` represents contradiction, value competition, incompatible
    interpretation, unresolved assumption, or evidence conflict. It identifies
    affected items, severity, and admissible operations before closure can be
    earned.
    """

    id: str
    type: TensionType
    items: list[str]
    description: str
    severity: Severity
    resolution_options: list[ResolutionOption]


@dataclass(slots=True)
class Remainder:
    """Typed unresolved content that should be investigated or preserved.

    ``Remainder`` distinguishes evidence gaps, ambiguities, pluralism, open
    questions, and generative remainders so the system does not confuse missing
    evidence with productive openness or silently complete human-owned meaning.
    """

    id: str
    type: RemainderType
    content: str
    belongs_to: RemainderOwner
    preservation_reason: str
    resolution_conditions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DecisionState:
    """The closure regulator's current position and reason for stopping.

    This model maps to the ontology's decision state: resolve, continue,
    investigate, contrast, suspend, rollback, preserve openness, ask the user,
    or transfer to human judgment based on the kind of unresolvedness present.
    """

    id: str
    state: Decision
    reason: str
    unresolvedness_type: UnresolvednessType
    next_actions: list[str] = field(default_factory=list)
    stopping_condition: StoppingCondition | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class InquiryPacket:
    """The evolving typed inquiry state rendered by downstream outputs.

    ``InquiryPacket`` is the ontology as a single internal product: it gathers
    inquiry metadata, anchors, claims, interpretations, paths, tensions,
    remainders, and the current decision state so natural-language answers can
    be renderings of auditable state rather than the authoritative state itself.
    """

    inquiry: Inquiry
    anchors: list[Anchor] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    interpretations: list[Interpretation] = field(default_factory=list)
    paths: list[Path] = field(default_factory=list)
    tensions: list[Tension] = field(default_factory=list)
    remainders: list[Remainder] = field(default_factory=list)
    decision_state: DecisionState | None = None
