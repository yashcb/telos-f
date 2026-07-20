"""Domain-specific anchors and admissible operations for v0.1."""

from __future__ import annotations

from dataclasses import dataclass

from telos_f.models import AnchorType, ResolutionOption, RemainderType


@dataclass(frozen=True, slots=True)
class DomainProfile:
    """Answerability rules for a broad inquiry domain."""

    name: str
    anchor_types: tuple[AnchorType, ...]
    admissible_operations: tuple[ResolutionOption, ...]
    prohibited_remainders_for_high_stakes: tuple[RemainderType, ...] = ()


DOMAIN_PROFILES = {
    "factual": DomainProfile(
        "factual",
        (AnchorType.OBSERVED_FACT, AnchorType.SOURCE, AnchorType.DOMAIN_RULE, AnchorType.ACCEPTED_CLAIM),
        (ResolutionOption.INVESTIGATE, ResolutionOption.SUSPEND, ResolutionOption.ASK_USER),
        (RemainderType.GENERATIVE_REMAINDER,),
    ),
    "general": DomainProfile(
        "general",
        (AnchorType.LINGUISTIC_CONVENTION, AnchorType.SOURCE, AnchorType.USER_CONTEXT),
        (ResolutionOption.ASK_USER, ResolutionOption.INVESTIGATE, ResolutionOption.DISAMBIGUATE),
    ),
    "normative": DomainProfile(
        "normative",
        (AnchorType.DECLARED_VALUE, AnchorType.USER_CONTEXT, AnchorType.DOMAIN_RULE, AnchorType.ACCEPTED_CLAIM),
        (ResolutionOption.CONTRAST, ResolutionOption.ASK_USER, ResolutionOption.SUSPEND),
    ),
    "ethics": DomainProfile(
        "ethics",
        (AnchorType.LINGUISTIC_CONVENTION, AnchorType.DECLARED_VALUE, AnchorType.USER_CONTEXT),
        (ResolutionOption.CONTRAST, ResolutionOption.ASK_USER, ResolutionOption.SUSPEND),
    ),
    "textual": DomainProfile(
        "textual",
        (AnchorType.LINGUISTIC_CONVENTION, AnchorType.SOURCE, AnchorType.USER_CONTEXT),
        (ResolutionOption.DISAMBIGUATE, ResolutionOption.ROLLBACK, ResolutionOption.ASK_USER),
    ),
    "literature": DomainProfile(
        "literature",
        (AnchorType.LINGUISTIC_CONVENTION, AnchorType.SOURCE, AnchorType.USER_CONTEXT),
        (ResolutionOption.DISAMBIGUATE, ResolutionOption.ROLLBACK, ResolutionOption.ASK_USER),
    ),
    "creative": DomainProfile(
        "creative",
        (AnchorType.LINGUISTIC_CONVENTION, AnchorType.USER_CONTEXT),
        (ResolutionOption.ROLLBACK, ResolutionOption.ASK_USER, ResolutionOption.DISAMBIGUATE),
    ),
}


def profile_for(domain: str) -> DomainProfile:
    """Return the nearest known profile for a compiler/domain label."""

    lowered = domain.lower()
    for key, profile in DOMAIN_PROFILES.items():
        if key in lowered:
            return profile
    return DOMAIN_PROFILES["general"]
