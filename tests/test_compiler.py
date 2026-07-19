from telos_f.compiler import InquiryCompiler
from telos_f.models import ClosurePolicy, InquiryType, RequestedAction, Stakes


def compile_input(text, **kwargs):
    return InquiryCompiler().compile(text, **kwargs)


def test_justice_fixture_compiles_as_concept_exploration_with_open_closure():
    compiled = compile_input("justice")

    inquiry = compiled.inquiry
    assert inquiry.goal == "justice"
    assert inquiry.inquiry_type is InquiryType.EXPLORATION
    assert inquiry.requested_action is RequestedAction.EXPLORE
    assert inquiry.domain == "ethics"
    assert inquiry.stakes is Stakes.LOW
    assert inquiry.closure_policy is ClosurePolicy.PRESERVE_OPEN
    assert inquiry.appears_compressed_or_metaphorical is True
    assert inquiry.evident_speech_act_beyond_literal_wording is False
    assert "type:compact_concept_exploration" in compiled.trace.rules_fired


def test_city_breathed_fixture_preserves_poetic_openness():
    compiled = compile_input("The city breathed")

    inquiry = compiled.inquiry
    assert inquiry.inquiry_type is InquiryType.INTERPRETATION
    assert inquiry.requested_action is RequestedAction.INTERPRET
    assert inquiry.domain == "literature"
    assert inquiry.closure_policy is ClosurePolicy.PRESERVE_OPEN
    assert inquiry.appears_compressed_or_metaphorical is True
    assert inquiry.evident_speech_act_beyond_literal_wording is True
    assert inquiry.speech_act_note is not None


def test_city_was_big_fixture_resolves_as_plain_fact_or_assertion():
    compiled = compile_input("The city was big")

    inquiry = compiled.inquiry
    assert inquiry.inquiry_type is InquiryType.FACT
    assert inquiry.requested_action is RequestedAction.ANSWER
    assert inquiry.domain == "general"
    assert inquiry.closure_policy is ClosurePolicy.RESOLVE
    assert inquiry.appears_compressed_or_metaphorical is False
    assert inquiry.evident_speech_act_beyond_literal_wording is False


def test_colorless_green_ideas_fixture_records_speech_act_and_assumed_context():
    compiled = compile_input("Colorless green ideas sleep furiously")

    inquiry = compiled.inquiry
    assert inquiry.inquiry_type is InquiryType.INTERPRETATION
    assert inquiry.domain == "linguistics"
    assert inquiry.closure_policy is ClosurePolicy.PRESERVE_OPEN
    assert inquiry.appears_compressed_or_metaphorical is True
    assert inquiry.evident_speech_act_beyond_literal_wording is True
    assert inquiry.speech_act_note is not None
    assert "literal sentence semantics" in " ".join(inquiry.assumed_context)
    assert "speech_act:canonical_syntax_or_surrealism_example" in compiled.trace.rules_fired


def test_explicit_fields_override_heuristics_and_are_recorded():
    compiled = compile_input(
        "Which path should we choose?",
        explicit_context="Planning a deployment rollback.",
        domain="software",
        stakes="high",
        closure_policy="ask_user",
    )

    inquiry = compiled.inquiry
    assert inquiry.explicit_user_context == "Planning a deployment rollback."
    assert inquiry.context == "Planning a deployment rollback."
    assert inquiry.domain == "software"
    assert inquiry.stakes is Stakes.HIGH
    assert inquiry.closure_policy is ClosurePolicy.ASK_USER
    assert inquiry.inquiry_type is InquiryType.DECISION
    assert compiled.trace.supplied_fields["domain"] == "software"
