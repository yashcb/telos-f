"""Human-facing renderings constrained by Inquiry Packet state."""

from __future__ import annotations

from telos_f.models import Decision, InquiryPacket


class PacketRenderer:
    """Render packet state without adding untracked evidence-dependent claims."""

    def render(self, packet: InquiryPacket) -> str:
        decision = packet.decision_state
        anchors = ", ".join(anchor.content for anchor in packet.anchors) or "no accepted shared anchor yet"
        claims = "; ".join(claim.proposition for claim in packet.claims) or "no accepted factual claim yet"
        remainders = "; ".join(remainder.content for remainder in packet.remainders) or "no explicit remainder"
        if decision is None:
            return f"Inquiry '{packet.inquiry.goal}' is compiled, but closure has not yet been decided. Anchors: {anchors}."
        if decision.state is Decision.INVESTIGATE:
            return f"Investigate before resolving '{packet.inquiry.goal}'. Current claims: {claims}. Reason: {decision.reason}"
        if decision.state is Decision.CONTRAST:
            return f"Contrast live commitments for '{packet.inquiry.goal}'. Anchors: {anchors}. Reason: {decision.reason}"
        if decision.state is Decision.PRESERVE_OPENNESS:
            return f"Shared anchor: {anchors}. Preserved remainder: {remainders}. The receiver should complete the final movement."
        if decision.state is Decision.ROLLBACK:
            return f"Rollback is required for '{packet.inquiry.goal}' because the path drifted. Reason: {decision.reason}"
        if decision.state is Decision.REPAIR_OR_STOP:
            return f"Repair or request context for '{packet.inquiry.goal}'. Reason: {decision.reason}"
        if decision.state is Decision.TRANSFER_TO_HUMAN:
            return f"This remainder belongs to human judgment: {remainders}. Reason: {decision.reason}"
        if decision.state is Decision.RESOLVE_PROVISIONALLY:
            return f"Provisional resolution for '{packet.inquiry.goal}': {claims}. Revision remains possible if grounds change."
        return f"Closure decision for '{packet.inquiry.goal}': {decision.state}. Reason: {decision.reason}"
