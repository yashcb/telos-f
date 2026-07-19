from telos_f.closure import ClosureRegulator
from telos_f.models import (
    Anchor,
    AnchorType,
    Claim,
    ClaimStatus,
    ClosurePolicy,
    Decision,
    Inquiry,
    InquiryPacket,
    Remainder,
    RemainderOwner,
    RemainderType,
    RequestedAction,
    Stakes,
    StoppingCondition,
    Strength,
    Tension,
    TensionType,
    Severity,
    Uncertainty,
)


def packet(**overrides):
    base = {
        "inquiry": Inquiry(
            id="i-1",
            goal="test closure",
            domain="test",
            context=None,
            stakes=Stakes.LOW,
            requested_action=RequestedAction.ANSWER,
            closure_policy=ClosurePolicy.AUTO,
        )
    }
    base.update(overrides)
    return InquiryPacket(**base)


def test_missing_evidence_investigates_with_renderable_metadata():
    state = packet(
        claims=[
            Claim(
                id="c-1",
                proposition="An unsupported factual claim.",
                uncertainty=Uncertainty.UNRESOLVED,
            )
        ]
    )

    decision = ClosureRegulator().decide(state)

    assert decision.state is Decision.INVESTIGATE
    assert decision.stopping_condition is StoppingCondition.INSUFFICIENT_EVIDENCE
    assert decision.metadata["condition"] == "missing evidence"
    assert decision.metadata["why_stopped"] == decision.reason
    assert decision.metadata["evidence"]["ungrounded_claims"] == ["c-1"]


def test_competing_values_contrast_before_resolution():
    state = packet(
        tensions=[
            Tension(
                id="t-1",
                type=TensionType.COMPETING_VALUE,
                items=["value-a", "value-b"],
                description="Different commitments produce different answers.",
                severity=Severity.MEDIUM,
                resolution_options=[],
            )
        ]
    )

    decision = ClosureRegulator()(state)

    assert decision.state is Decision.CONTRAST
    assert decision.metadata["condition"] == "competing value systems"


def test_coherent_openness_preserves_remainder():
    state = packet(
        anchors=[
            Anchor(
                id="a-1",
                type=AnchorType.USER_CONTEXT,
                content="Shared interpretive anchor",
                provenance="user",
                strength=Strength.STRONG,
            )
        ],
        remainders=[
            Remainder(
                id="r-1",
                type=RemainderType.GENERATIVE_REMAINDER,
                content="Receiver-completed meaning",
                belongs_to=RemainderOwner.SHARED,
                preservation_reason="Completion appropriately remains open.",
            )
        ],
    )

    decision = ClosureRegulator().decide(state)

    assert decision.state is Decision.PRESERVE_OPENNESS
    assert decision.metadata["condition"] == "coherent openness"


def test_stable_support_resolves_provisionally():
    state = packet(
        claims=[
            Claim(
                id="c-1",
                proposition="A grounded claim.",
                grounds=["source-1"],
                uncertainty=Uncertainty.LOW,
                status=ClaimStatus.ACCEPTED,
            )
        ]
    )

    decision = ClosureRegulator().decide(state)

    assert decision.state is Decision.RESOLVE_PROVISIONALLY
    assert decision.stopping_condition is StoppingCondition.SUFFICIENT_RESOLUTION
