"""Validation rules for auditable v0.1 Inquiry Packets."""

from __future__ import annotations

from dataclasses import dataclass

from telos_f.models import (
    ClaimStatus,
    InquiryPacket,
    InterpretationStatus,
    RemainderType,
    Stakes,
    UnresolvednessType,
)


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A packet invariant violation or warning."""

    code: str
    message: str
    severity: str = "error"


class PacketValidator:
    """Validate constitutional and packet-level v0.1 invariants."""

    def validate(self, packet: InquiryPacket) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        anchor_ids = {anchor.id for anchor in packet.anchors}
        path_targets = {step.to_ref for path in packet.paths for step in path.steps}
        path_sources = {step.from_ref for path in packet.paths for step in path.steps}

        if not packet.inquiry.goal.strip():
            issues.append(ValidationIssue("inquiry.empty_goal", "Inquiry goal must be non-empty."))

        for claim in packet.claims:
            if claim.status is ClaimStatus.ACCEPTED and not (set(claim.grounds) & anchor_ids):
                issues.append(ValidationIssue("claim.accepted_without_anchor", f"Accepted claim {claim.id} must cite at least one anchor as grounds."))
            if claim.status is ClaimStatus.ACCEPTED and not claim.assumptions:
                issues.append(ValidationIssue("claim.accepted_without_assumptions", f"Accepted claim {claim.id} must expose assumptions or revision conditions."))

        for interpretation in packet.interpretations:
            if interpretation.status is InterpretationStatus.RETAINED and interpretation.signal_ref not in anchor_ids and not anchor_ids:
                issues.append(ValidationIssue("interpretation.retained_without_anchor", f"Retained interpretation {interpretation.id} needs a shared anchor."))

        for remainder in packet.remainders:
            if remainder.type is RemainderType.GENERATIVE_REMAINDER:
                has_path = remainder.id in path_targets or remainder.id in path_sources or bool(packet.paths)
                if not packet.anchors or not has_path:
                    issues.append(ValidationIssue("remainder.generative_without_anchor_path", f"Generative remainder {remainder.id} needs a shared anchor and non-arbitrary path."))
            if remainder.type is RemainderType.EVIDENCE_GAP and packet.inquiry.stakes in {Stakes.HIGH, Stakes.CRITICAL}:
                if packet.decision_state and packet.decision_state.unresolvedness_type is UnresolvednessType.GENERATIVE_OPENNESS:
                    issues.append(ValidationIssue("remainder.evidence_gap_as_openness", "Consequential evidence gaps must not be rendered as productive openness."))

        if packet.decision_state and packet.decision_state.unresolvedness_type is UnresolvednessType.GENERATIVE_OPENNESS:
            if any(remainder.type is RemainderType.EVIDENCE_GAP for remainder in packet.remainders):
                issues.append(ValidationIssue("decision.openness_with_evidence_gap", "Generative openness cannot mask an evidence gap."))

        return issues

    def assert_valid(self, packet: InquiryPacket) -> None:
        """Raise ``ValueError`` when packet invariants fail."""

        issues = self.validate(packet)
        errors = [issue for issue in issues if issue.severity == "error"]
        if errors:
            joined = "; ".join(f"{issue.code}: {issue.message}" for issue in errors)
            raise ValueError(joined)
