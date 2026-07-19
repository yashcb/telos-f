from telos_f.models import (
    Anchor,
    AnchorType,
    Claim,
    ClaimStatus,
    ClosurePolicy,
    ContinuityResult,
    Decision,
    DecisionState,
    Inquiry,
    InquiryPacket,
    InquiryType,
    Interpretation,
    InterpretationStatus,
    Novelty,
    Path,
    PathStatus,
    PathStep,
    Remainder,
    RemainderOwner,
    RemainderType,
    RequestedAction,
    ResolutionOption,
    Severity,
    Stakes,
    StoppingCondition,
    Strength,
    Tension,
    TensionType,
    Uncertainty,
    UnresolvednessType,
)


def test_initial_ontology_models_project_explanation_state_objects():
    inquiry = Inquiry(
        id="inquiry-justice",
        goal="justice",
        domain="ethics",
        context="No explicit context; medium-stakes normative exploration.",
        stakes=Stakes.MEDIUM,
        requested_action=RequestedAction.EXPLORE,
        closure_policy=ClosurePolicy.CONTRAST,
        available_resources=["project_explanation.md"],
        inquiry_type=InquiryType.EXPLORATION,
    )
    anchor = Anchor(
        id="anchor-fairness",
        type=AnchorType.LINGUISTIC_CONVENTION,
        content="fairness",
        provenance="project_explanation.md justice fixture",
        strength=Strength.STRONG,
    )
    claim = Claim(
        id="claim-burglary-rate",
        proposition="This neighborhood is unsafe because burglaries doubled last year.",
        assumptions=["same neighborhood boundary", "same reporting method"],
        scope="civic factual and policy",
        uncertainty=Uncertainty.UNRESOLVED,
        status=ClaimStatus.PROPOSED,
    )
    interpretation = Interpretation(
        id="interp-city-breathed",
        signal_ref="The city breathed",
        reading="crowds, traffic, weather, nightlife, or urban vitality",
        fidelity_to_source_signal=Strength.STRONG,
        contextual_fit=Strength.MODERATE,
        relational_continuity=Strength.STRONG,
        explanatory_power=Strength.MODERATE,
        alternatives=["atmosphere", "collective movement"],
        status=InterpretationStatus.RETAINED,
    )
    path = Path(
        id="path-bridge-memory",
        start_anchor_ids=["anchor-fairness"],
        steps=[
            PathStep(
                from_ref="The old bridge kept the town's memory.",
                to_ref="continuity between place and collective history",
                transition_reason="bridge, town, memory, and flood aftermath remain locally connected",
                referential=ContinuityResult.PASS,
                thematic=ContinuityResult.PASS,
                cue_dependence=ContinuityResult.PASS,
                novelty=Novelty.MEDIUM,
            )
        ],
        rollback_points=["The old bridge kept the town's memory."],
        status=PathStatus.ACTIVE,
    )
    tension = Tension(
        id="tension-plazas-parking",
        type=TensionType.COMPETING_VALUE,
        items=["pedestrian plazas", "curbside parking"],
        description="accessibility, commerce, climate, and public life remain differently weighted",
        severity=Severity.MEDIUM,
        resolution_options=[ResolutionOption.CONTRAST],
    )
    remainder = Remainder(
        id="remainder-city-breathed",
        type=RemainderType.GENERATIVE_REMAINDER,
        content="completion belongs partly to the receiver",
        belongs_to=RemainderOwner.SHARED,
        preservation_reason="shared anchor exists without exhaustive paraphrase",
    )
    decision = DecisionState(
        id="decision-contrast",
        state=Decision.CONTRAST,
        reason="Legitimate positions depend on different value commitments.",
        unresolvedness_type=UnresolvednessType.PERSPECTIVAL_OR_NORMATIVE_PLURALITY,
        stopping_condition=StoppingCondition.VALUE_CONFLICT,
    )

    packet = InquiryPacket(
        inquiry=inquiry,
        anchors=[anchor],
        claims=[claim],
        interpretations=[interpretation],
        paths=[path],
        tensions=[tension],
        remainders=[remainder],
        decision_state=decision,
    )

    assert packet.inquiry.goal == "justice"
    assert packet.anchors[0].content == "fairness"
    assert packet.claims[0].grounds == []
    assert packet.interpretations[0].status is InterpretationStatus.RETAINED
    assert packet.paths[0].steps[0].cue_dependence is ContinuityResult.PASS
    assert packet.tensions[0].type is TensionType.COMPETING_VALUE
    assert packet.remainders[0].type is RemainderType.GENERATIVE_REMAINDER
    assert packet.decision_state.state is Decision.CONTRAST
