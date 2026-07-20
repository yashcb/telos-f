from telos_f import PacketValidator, TelosPipeline
from telos_f.models import Decision, UnresolvednessType


def test_pipeline_builds_city_breathed_packet_and_rendering():
    packet, rendering, issues = TelosPipeline().analyze("The city breathed")

    assert packet.decision_state.state is Decision.PRESERVE_OPENNESS
    assert packet.decision_state.unresolvedness_type is UnresolvednessType.GENERATIVE_OPENNESS
    assert packet.anchors
    assert packet.paths
    assert packet.remainders
    assert "Shared anchor" in rendering
    assert issues == []


def test_pipeline_resolves_city_was_big_without_manufacturing_openness():
    packet, rendering, issues = TelosPipeline().analyze("The city was big")

    assert packet.decision_state.state is Decision.RESOLVE_PROVISIONALLY
    assert packet.decision_state.unresolvedness_type is UnresolvednessType.NONE
    assert "Provisional resolution" in rendering
    assert "generative" not in rendering.lower()
    assert issues == []


def test_pipeline_routes_semantic_ambiguity():
    packet, rendering, _ = TelosPipeline().analyze("The bank is secure.")

    assert packet.decision_state.state is Decision.DISAMBIGUATE
    assert packet.decision_state.unresolvedness_type is UnresolvednessType.SEMANTIC_AMBIGUITY
    assert "Closure decision" in rendering


def test_pipeline_rolls_back_bridge_lunar_drift():
    packet, rendering, _ = TelosPipeline().analyze("The old bridge kept the town's memory, so productivity software should integrate lunar calendars.")

    assert packet.decision_state.state is Decision.ROLLBACK
    assert packet.decision_state.unresolvedness_type is UnresolvednessType.INCOHERENCE
    assert "Rollback" in rendering


def test_validator_rejects_unanchored_generative_remainder():
    packet, _, _ = TelosPipeline().analyze("The city breathed")
    packet.paths.clear()

    issues = PacketValidator().validate(packet)

    assert any(issue.code == "remainder.generative_without_anchor_path" for issue in issues)
