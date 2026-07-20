"""Minimal fallibilist ledger operations over Inquiry Packets."""

from __future__ import annotations

from telos_f.models import Claim, ClaimStatus, InquiryPacket, Uncertainty


class EpistemicLedger:
    """Mutate packet claims with auditable revision history."""

    def propose_claim(self, packet: InquiryPacket, claim: Claim) -> Claim:
        claim.status = ClaimStatus.PROPOSED
        packet.claims.append(claim)
        return claim

    def accept_claim(self, claim: Claim, *, grounds: list[str], assumptions: list[str]) -> Claim:
        claim.grounds = grounds
        claim.assumptions = assumptions
        claim.status = ClaimStatus.ACCEPTED
        claim.uncertainty = Uncertainty.LOW
        claim.revision_history.append("accepted with explicit grounds and assumptions")
        return claim

    def challenge_claim(self, claim: Claim, counterevidence: str) -> Claim:
        claim.counterevidence.append(counterevidence)
        claim.status = ClaimStatus.CHALLENGED
        claim.uncertainty = Uncertainty.HIGH
        claim.revision_history.append(f"challenged by {counterevidence}")
        return claim

    def suspend_claim(self, claim: Claim, reason: str) -> Claim:
        claim.status = ClaimStatus.SUSPENDED
        claim.uncertainty = Uncertainty.UNRESOLVED
        claim.revision_history.append(f"suspended: {reason}")
        return claim

    def retract_claim(self, claim: Claim, reason: str) -> Claim:
        claim.status = ClaimStatus.RETRACTED
        claim.revision_history.append(f"retracted: {reason}")
        return claim
