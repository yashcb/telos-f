import json
from pathlib import Path as FilePath

from telos_f import InquiryCompiler
from telos_f.closure import ClosureRegulator
from telos_f.models import (
    Anchor,
    AnchorType,
    Claim,
    ClosurePolicy,
    Decision,
    InquiryPacket,
    Path,
    PathStatus,
    PathStep,
    Remainder,
    RemainderOwner,
    RemainderType,
    ResolutionOption,
    Severity,
    Strength,
    Tension,
    TensionType,
    Uncertainty,
    UnresolvednessType,
)

ROOT = FilePath(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "phenomena" / "v0.1.jsonl"


def corpus_case(signal):
    for line in CORPUS.read_text().splitlines():
        row = json.loads(line)
        if row["signal"] == signal:
            return row
    raise AssertionError(f"Missing corpus fixture: {signal}")


def compiled_packet(signal):
    row = corpus_case(signal)
    compiled = InquiryCompiler().compile(signal, explicit_context=row["context"])
    return row, compiled, InquiryPacket(inquiry=compiled.inquiry)


def test_corpus_fixture_the_city_breathed_preserves_generative_remainder():
    row, compiled, state = compiled_packet("The city breathed")
    state.anchors.append(Anchor("anchor-city", AnchorType.LINGUISTIC_CONVENTION, "city, organic life, rhythm, collective movement, atmosphere", "project_explanation.md", Strength.STRONG))
    state.remainders.append(Remainder("remainder-city", RemainderType.GENERATIVE_REMAINDER, "completion belongs partly to the receiver", RemainderOwner.SHARED, "coherent metaphor should not be exhausted"))

    decision = ClosureRegulator().decide(state)

    assert row["expected_unresolvedness_type"] == "generative_openness"
    assert compiled.inquiry.goal == "The city breathed"
    assert compiled.inquiry.closure_policy is ClosurePolicy.PRESERVE_OPEN
    assert decision.state is Decision.PRESERVE_OPENNESS
    assert decision.unresolvedness_type is UnresolvednessType.GENERATIVE_OPENNESS
    assert decision.metadata["evidence"]["generative_remainders"] == ["remainder-city"]


def test_corpus_fixture_the_city_was_big_does_not_fabricate_depth():
    row, compiled, state = compiled_packet("The city was big")

    decision = ClosureRegulator().decide(state)

    assert row["expected_unresolvedness_type"] == "none"
    assert compiled.inquiry.goal == "The city was big"
    assert compiled.inquiry.closure_policy is ClosurePolicy.RESOLVE
    assert compiled.inquiry.appears_compressed_or_metaphorical is False
    assert decision.state is Decision.INVESTIGATE
    assert decision.unresolvedness_type is UnresolvednessType.EPISTEMIC_INSUFFICIENCY
    assert "generative_remainders" not in decision.metadata["evidence"]


def test_corpus_fixture_colorless_green_ideas_requests_context_not_invention():
    row, compiled, state = compiled_packet("Colorless green ideas sleep furiously")
    state.tensions.append(Tension("tension-colorless", TensionType.INCOMPATIBLE_INTERPRETATION, ["literal scene", "syntax or surrealism example"], "literal scene construction is resistant without broader context", Severity.HIGH, [ResolutionOption.ASK_USER, ResolutionOption.SUSPEND]))

    decision = ClosureRegulator().decide(state)

    assert row["expected_unresolvedness_type"] == "incoherence"
    assert compiled.inquiry.goal == "Colorless green ideas sleep furiously"
    assert decision.state is Decision.REPAIR_OR_STOP
    assert decision.unresolvedness_type is UnresolvednessType.INCOHERENCE
    assert "request clarifying context" in decision.next_actions


def test_corpus_fixture_neighborhood_burglary_evidence_gap_investigates():
    row, compiled, state = compiled_packet("This neighborhood is unsafe because burglaries doubled last year.")
    state.claims.append(Claim("claim-burglaries", row["signal"], uncertainty=Uncertainty.UNRESOLVED))
    state.remainders.append(Remainder("remainder-stats", RemainderType.EVIDENCE_GAP, "no crime statistics, dates, or source are supplied", RemainderOwner.EXTERNAL_EVIDENCE, "check source, timeframe, denominator, and comparison baseline"))

    decision = ClosureRegulator().decide(state)

    assert row["expected_unresolvedness_type"] == "epistemic_insufficiency"
    assert compiled.inquiry.goal == row["signal"]
    assert decision.state is Decision.INVESTIGATE
    assert decision.unresolvedness_type is UnresolvednessType.EPISTEMIC_INSUFFICIENCY


def test_corpus_fixture_pedestrian_plazas_value_conflict_contrasts():
    row, compiled, state = compiled_packet("We should prioritize pedestrian plazas over curbside parking downtown.")
    state.tensions.append(Tension("tension-plazas", TensionType.COMPETING_VALUE, ["accessibility", "commerce", "climate", "public life"], "agreed facts do not settle normative weighting", Severity.MEDIUM, [ResolutionOption.CONTRAST]))

    decision = ClosureRegulator().decide(state)

    assert row["expected_unresolvedness_type"] == "perspectival_or_normative_plurality"
    assert compiled.inquiry.goal == row["signal"]
    assert decision.state is Decision.CONTRAST
    assert decision.unresolvedness_type is UnresolvednessType.PERSPECTIVAL_OR_NORMATIVE_PLURALITY


def test_corpus_fixture_emissions_factual_contradiction_is_not_perspectival():
    row, compiled, state = compiled_packet("The report says emissions fell 12% in 2025 and rose 9% in 2025 under the same measurement scope.")
    state.tensions.append(Tension("tension-emissions", TensionType.CONTRADICTION, ["fell 12% in 2025", "rose 9% in 2025"], "same organization, year, scope, and accounting method cannot all hold without reconciliation", Severity.HIGH, [ResolutionOption.INVESTIGATE, ResolutionOption.ASK_USER]))

    decision = ClosureRegulator().decide(state)

    assert row["expected_unresolvedness_type"] == "epistemic_insufficiency"
    assert compiled.inquiry.goal == row["signal"]
    assert decision.state is Decision.INVESTIGATE
    assert decision.unresolvedness_type is UnresolvednessType.EPISTEMIC_INSUFFICIENCY
    assert decision.state is not Decision.CONTRAST


def test_corpus_fixture_bridge_to_lunar_calendars_rolls_back_drift():
    row, compiled, state = compiled_packet("The old bridge kept the town's memory, so productivity software should integrate lunar calendars.")
    state.paths.append(Path("path-bridge-lunar", ["old bridge", "town memory"], [PathStep("The old bridge kept the town's memory", "productivity software should integrate lunar calendars", "unsupported jump from literary landmark context to software calendars")], status=PathStatus.DRIFT_DETECTED))

    decision = ClosureRegulator().decide(state)

    assert row["expected_unresolvedness_type"] == "incoherence"
    assert compiled.inquiry.goal == row["signal"]
    assert decision.state is Decision.ROLLBACK
    assert decision.unresolvedness_type is UnresolvednessType.INCOHERENCE
