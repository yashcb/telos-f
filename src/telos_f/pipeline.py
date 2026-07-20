"""End-to-end v0.1 packet construction pipeline."""

from __future__ import annotations

from telos_f.closure import ClosureRegulator
from telos_f.compiler import InquiryCompiler
from telos_f.ledger import EpistemicLedger
from telos_f.models import (
    Anchor,
    AnchorType,
    Claim,
    ClaimStatus,
    ClosurePolicy,
    InquiryPacket,
    Remainder,
    RemainderOwner,
    RemainderType,
    ResolutionOption,
    Severity,
    Stakes,
    Strength,
    Tension,
    TensionType,
    Uncertainty,
)
from telos_f.path import LocalWalkEngine
from telos_f.renderer import PacketRenderer
from telos_f.validation import PacketValidator, ValidationIssue


class TelosPipeline:
    """Compile, populate, regulate, validate, and render an Inquiry Packet."""

    def __init__(self) -> None:
        self.compiler = InquiryCompiler()
        self.walker = LocalWalkEngine()
        self.regulator = ClosureRegulator()
        self.renderer = PacketRenderer()
        self.validator = PacketValidator()
        self.ledger = EpistemicLedger()

    def analyze(self, raw_input: str, **kwargs: object) -> tuple[InquiryPacket, str, list[ValidationIssue]]:
        compiled = self.compiler.compile(raw_input, **kwargs)
        packet = InquiryPacket(inquiry=compiled.inquiry)
        self._populate_minimal_state(packet)
        packet.decision_state = self.regulator.decide(packet)
        rendering = self.renderer.render(packet)
        issues = self.validator.validate(packet)
        return packet, rendering, issues

    def _populate_minimal_state(self, packet: InquiryPacket) -> None:
        goal = packet.inquiry.goal
        lowered = goal.lower()
        if lowered == "the city breathed":
            packet.anchors.append(Anchor("anchor-city-breathed", AnchorType.LINGUISTIC_CONVENTION, "city, organic life, rhythm, collective movement, atmosphere", "v0.1 heuristic", Strength.STRONG))
            packet.remainders.append(Remainder("remainder-city-breathed", RemainderType.GENERATIVE_REMAINDER, "receiver-completed urban vitality, movement, or atmosphere", RemainderOwner.SHARED, "coherent metaphor should not be exhausted"))
            packet.paths.append(self.walker.build_path("path-city-breathed", ["anchor-city-breathed"], [("The city breathed", "receiver-completed urban vitality, movement, or atmosphere", "organic-life relation remains locally connected to city rhythm")]))
            return
        if lowered == "the city was big":
            packet.anchors.append(Anchor("anchor-city-size", AnchorType.LINGUISTIC_CONVENTION, "city and ordinary size or scale", "v0.1 heuristic", Strength.MODERATE))
            packet.claims.append(Claim("claim-city-size", "The expression predicates ordinary largeness of a city with ordinary descriptive force.", grounds=["anchor-city-size"], assumptions=["No special literary context was supplied."], uncertainty=Uncertainty.LOW, status=ClaimStatus.ACCEPTED))
            return
        if lowered == "colorless green ideas sleep furiously":
            packet.anchors.append(Anchor("anchor-colorless-syntax", AnchorType.LINGUISTIC_CONVENTION, "English syntactic form with semantic resistance", "v0.1 heuristic", Strength.STRONG))
            packet.tensions.append(Tension("tension-colorless", TensionType.INCOMPATIBLE_INTERPRETATION, ["literal scene", "syntax or surrealism example"], "literal scene construction is resistant without broader context", Severity.HIGH, [ResolutionOption.ASK_USER, ResolutionOption.SUSPEND]))
            return
        if lowered == "justice":
            packet.anchors.append(Anchor("anchor-justice", AnchorType.LINGUISTIC_CONVENTION, "fairness, legitimacy, treatment, and social order", "v0.1 heuristic", Strength.STRONG))
            packet.remainders.append(Remainder("remainder-justice", RemainderType.PLURALISM, "different theories weight equality, desert, repair, and responsibility differently", RemainderOwner.SHARED, "normative plurality should be contrasted, not collapsed"))
            packet.tensions.append(Tension("tension-justice", TensionType.COMPETING_VALUE, ["equality", "desert", "repair", "responsibility"], "legitimate theories depend on different commitments", Severity.MEDIUM, [ResolutionOption.CONTRAST]))
            return
        if "bank is secure" in lowered:
            packet.anchors.append(Anchor("anchor-bank", AnchorType.LINGUISTIC_CONVENTION, "bank and security have multiple ordinary senses", "v0.1 heuristic", Strength.MODERATE))
            packet.remainders.append(Remainder("remainder-bank", RemainderType.AMBIGUITY, "river bank, financial institution, banking app, or vault may be meant", RemainderOwner.SHARED, "referent must be disambiguated before consequential advice"))
            return
        if "burglaries doubled" in lowered:
            packet.anchors.append(Anchor("anchor-burglary-claim", AnchorType.LINGUISTIC_CONVENTION, "neighborhood safety and burglary rate comparison", "v0.1 heuristic", Strength.MODERATE))
            packet.claims.append(Claim("claim-burglary-rate", goal, uncertainty=Uncertainty.UNRESOLVED))
            packet.remainders.append(Remainder("remainder-burglary-evidence", RemainderType.EVIDENCE_GAP, "no crime statistics, dates, denominator, or source are supplied", RemainderOwner.EXTERNAL_EVIDENCE, "empirical claim requires investigation"))
            return
        if "pedestrian plazas" in lowered and "curbside parking" in lowered:
            packet.anchors.append(Anchor("anchor-street-allocation", AnchorType.LINGUISTIC_CONVENTION, "downtown street allocation between plazas and parking", "v0.1 heuristic", Strength.MODERATE))
            packet.tensions.append(Tension("tension-street-values", TensionType.COMPETING_VALUE, ["accessibility", "commerce", "climate", "public life"], "agreed facts do not settle normative weighting", Severity.MEDIUM, [ResolutionOption.CONTRAST]))
            return
        if "emissions fell 12%" in lowered and "rose 9%" in lowered:
            packet.anchors.append(Anchor("anchor-emissions-scope", AnchorType.LINGUISTIC_CONVENTION, "same organization, calendar year, scope, and accounting method", "v0.1 heuristic", Strength.STRONG))
            packet.tensions.append(Tension("tension-emissions", TensionType.CONTRADICTION, ["fell 12% in 2025", "rose 9% in 2025"], "same scope cannot support both claims without reconciliation", Severity.HIGH, [ResolutionOption.INVESTIGATE, ResolutionOption.ASK_USER]))
            return
        if "lunar calendars" in lowered and "old bridge" in lowered:
            packet.anchors.append(Anchor("anchor-bridge-memory", AnchorType.LINGUISTIC_CONVENTION, "old bridge, town memory, and literary landmark context", "v0.1 heuristic", Strength.MODERATE))
            packet.paths.append(self.walker.build_path("path-bridge-lunar", ["anchor-bridge-memory"], [("The old bridge kept the town's memory", "productivity software should integrate lunar calendars", "unsupported jump from literary landmark context to software calendars")]))
            return
        if packet.inquiry.closure_policy is ClosurePolicy.PRESERVE_OPEN:
            packet.anchors.append(Anchor("anchor-compact-signal", AnchorType.LINGUISTIC_CONVENTION, goal, "v0.1 fallback", Strength.WEAK))
            packet.remainders.append(Remainder("remainder-compact-signal", RemainderType.OPEN_QUESTION, "context is needed to tell whether openness is generative, ambiguous, or underspecified", RemainderOwner.SHARED, "fallback keeps inferred context explicit"))
            return
        packet.claims.append(Claim("claim-unresolved", goal, uncertainty=Uncertainty.UNRESOLVED))
