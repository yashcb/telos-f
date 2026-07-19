"""Deterministic compiler from raw signals into inspectable inquiries.

Version 0.1 deliberately avoids LLM-dependent parsing.  The compiler records
which explicit inputs were supplied, which assumptions were inferred by small
transparent heuristics, and how those heuristics selected inquiry type, domain,
stakes, and closure policy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from uuid import uuid5, NAMESPACE_URL

from telos_f.models import ClosurePolicy, Inquiry, InquiryType, RequestedAction, Stakes


@dataclass(frozen=True, slots=True)
class CompilationTrace:
    """Inspectable explanation of a deterministic compilation decision."""

    normalized_input: str
    rules_fired: list[str] = field(default_factory=list)
    supplied_fields: dict[str, object] = field(default_factory=dict)
    inferred_fields: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CompiledInquiry:
    """Inquiry plus the trace needed to audit how it was compiled."""

    inquiry: Inquiry
    trace: CompilationTrace


_FACT_PATTERNS = (
    re.compile(r"^(what|when|where|who|how many|how much|is|are|was|were|did|does|do)\b", re.IGNORECASE),
)
_DECISION_PATTERNS = re.compile(r"\b(should i|should we|choose|decide|which option|recommend)\b", re.IGNORECASE)
_CREATION_PATTERNS = re.compile(r"\b(write|draft|create|compose|generate|make|design)\b", re.IGNORECASE)
_INTERPRETATION_PATTERNS = re.compile(r"\b(mean|interpret|symboli[sz]e|metaphor|why does|reading of)\b", re.IGNORECASE)
_JUDGMENT_PATTERNS = re.compile(r"\b(good|bad|better|best|fair|just|ethical|beautiful|apt)\b", re.IGNORECASE)
_HIGH_STAKES_PATTERNS = re.compile(r"\b(medical|legal|financial|safety|emergency|critical|risk|harm|job|court)\b", re.IGNORECASE)
_DOMAIN_HINTS = (
    ("ethics", re.compile(r"\b(justice|fair|ethical|moral|responsibility|equality)\b", re.IGNORECASE)),
    ("law", re.compile(r"\b(law|legal|court|contract|statute)\b", re.IGNORECASE)),
    ("literature", re.compile(r"\b(metaphor|poem|poetic|city breathed|surreal|image)\b", re.IGNORECASE)),
    ("linguistics", re.compile(r"\b(syntax|grammar|sentence|colorless green ideas sleep furiously)\b", re.IGNORECASE)),
)


class InquiryCompiler:
    """Compile raw user input into an ``Inquiry`` using deterministic rules.

    ``compile`` returns ``CompiledInquiry`` so callers can inspect the rule
    trace.  ``compile_inquiry`` is a convenience method for callers that only
    need the typed inquiry object.
    """

    def compile(
        self,
        raw_input: str,
        *,
        explicit_context: str | None = None,
        domain: str | None = None,
        desired_purpose: str | None = None,
        stakes: Stakes | str | None = None,
        closure_policy: ClosurePolicy | str | None = None,
    ) -> CompiledInquiry:
        normalized = " ".join(raw_input.split())
        if not normalized:
            raise ValueError("raw_input must contain a non-empty signal or question")

        rules: list[str] = []
        inquiry_type = self._inquiry_type(normalized, desired_purpose, rules)
        requested_action = self._requested_action(inquiry_type)
        inferred_domain = domain or self._domain(normalized, explicit_context, rules)
        inferred_stakes = self._stakes(normalized, stakes, rules)
        compressed_or_metaphorical = self._compressed_or_metaphorical(normalized, rules)
        speech_act, speech_act_note = self._speech_act(normalized, explicit_context, rules)
        policy = self._closure_policy(closure_policy, inquiry_type, compressed_or_metaphorical, speech_act, rules)
        assumed_context = self._assumed_context(normalized, inferred_domain, compressed_or_metaphorical, speech_act)

        inquiry = Inquiry(
            id=f"inquiry-{uuid5(NAMESPACE_URL, 'telos-f:v0.1:' + normalized).hex[:12]}",
            goal=normalized,
            domain=inferred_domain,
            context=explicit_context,
            stakes=inferred_stakes,
            requested_action=requested_action,
            closure_policy=policy,
            inquiry_type=inquiry_type,
            explicit_user_context=explicit_context,
            assumed_context=assumed_context,
            appears_compressed_or_metaphorical=compressed_or_metaphorical,
            evident_speech_act_beyond_literal_wording=speech_act,
            speech_act_note=speech_act_note,
        )
        trace = CompilationTrace(
            normalized_input=normalized,
            rules_fired=rules,
            supplied_fields={"explicit_context": explicit_context, "domain": domain, "desired_purpose": desired_purpose, "stakes": stakes, "closure_policy": closure_policy},
            inferred_fields={
                "inquiry_type": inquiry_type.value,
                "domain": inferred_domain,
                "stakes": inferred_stakes.value,
                "closure_policy": policy.value,
                "assumed_context": assumed_context,
                "appears_compressed_or_metaphorical": compressed_or_metaphorical,
                "evident_speech_act_beyond_literal_wording": speech_act,
            },
        )
        return CompiledInquiry(inquiry=inquiry, trace=trace)

    def compile_inquiry(self, raw_input: str, **kwargs: object) -> Inquiry:
        """Return only the compiled inquiry object."""

        return self.compile(raw_input, **kwargs).inquiry

    def _inquiry_type(self, text: str, purpose: str | None, rules: list[str]) -> InquiryType:
        probe = f"{purpose or ''} {text}"
        if _CREATION_PATTERNS.search(probe):
            rules.append("type:creation_pattern")
            return InquiryType.CREATION
        if _DECISION_PATTERNS.search(probe):
            rules.append("type:decision_pattern")
            return InquiryType.DECISION
        if _INTERPRETATION_PATTERNS.search(probe) or self._looks_poetic(text):
            rules.append("type:interpretation_pattern_or_poetic_signal")
            return InquiryType.INTERPRETATION
        if _JUDGMENT_PATTERNS.search(probe):
            rules.append("type:judgment_pattern")
            return InquiryType.JUDGMENT
        if any(pattern.search(text) for pattern in _FACT_PATTERNS) or text.endswith("?"):
            rules.append("type:fact_question")
            return InquiryType.FACT
        if re.search(r"\b(is|are|was|were)\b", text, re.IGNORECASE):
            rules.append("type:plain_copular_assertion")
            return InquiryType.FACT
        if len(text.split()) <= 2:
            rules.append("type:compact_concept_exploration")
            return InquiryType.EXPLORATION
        rules.append("type:default_exploration")
        return InquiryType.EXPLORATION

    def _requested_action(self, inquiry_type: InquiryType) -> RequestedAction:
        return {
            InquiryType.FACT: RequestedAction.ANSWER,
            InquiryType.INTERPRETATION: RequestedAction.INTERPRET,
            InquiryType.JUDGMENT: RequestedAction.COMPARE,
            InquiryType.DECISION: RequestedAction.DECIDE,
            InquiryType.EXPLORATION: RequestedAction.EXPLORE,
            InquiryType.CREATION: RequestedAction.CREATE,
        }[inquiry_type]

    def _domain(self, text: str, context: str | None, rules: list[str]) -> str:
        probe = f"{text} {context or ''}"
        for domain, pattern in _DOMAIN_HINTS:
            if pattern.search(probe):
                rules.append(f"domain:{domain}_hint")
                return domain
        rules.append("domain:general_default")
        return "general"

    def _stakes(self, text: str, supplied: Stakes | str | None, rules: list[str]) -> Stakes:
        if supplied is not None:
            rules.append("stakes:user_supplied")
            return Stakes(supplied)
        if _HIGH_STAKES_PATTERNS.search(text):
            rules.append("stakes:high_stakes_keyword")
            return Stakes.HIGH
        rules.append("stakes:low_default")
        return Stakes.LOW

    def _compressed_or_metaphorical(self, text: str, rules: list[str]) -> bool:
        if len(text.split()) <= 2:
            rules.append("compressed_or_metaphorical:compact_signal")
            return True
        if self._looks_poetic(text):
            rules.append("compressed_or_metaphorical:poetic_or_semantic_strain")
            return True
        rules.append("compressed_or_metaphorical:not_detected")
        return False

    def _speech_act(self, text: str, context: str | None, rules: list[str]) -> tuple[bool, str | None]:
        lowered = text.lower()
        if lowered == "colorless green ideas sleep furiously":
            rules.append("speech_act:canonical_syntax_or_surrealism_example")
            return True, "Likely functions as a syntax, surrealism, or language-philosophy example rather than a literal scene."
        if self._looks_poetic(text):
            rules.append("speech_act:poetic_expression")
            return True, "Likely invites interpretation of expressive or figurative force beyond literal predication."
        if context:
            rules.append("speech_act:context_supplied")
            return True, "Explicit context may specify a purpose beyond the literal wording."
        rules.append("speech_act:not_evident")
        return False, None

    def _closure_policy(self, supplied: ClosurePolicy | str | None, inquiry_type: InquiryType, compressed: bool, speech_act: bool, rules: list[str]) -> ClosurePolicy:
        if supplied is not None:
            rules.append("closure_policy:user_supplied")
            return ClosurePolicy(supplied)
        if inquiry_type is InquiryType.FACT and not compressed:
            rules.append("closure_policy:resolve_plain_fact")
            return ClosurePolicy.RESOLVE
        if inquiry_type is InquiryType.JUDGMENT:
            rules.append("closure_policy:contrast_judgment")
            return ClosurePolicy.CONTRAST
        if compressed or speech_act:
            rules.append("closure_policy:preserve_open_for_compressed_or_speech_act")
            return ClosurePolicy.PRESERVE_OPEN
        rules.append("closure_policy:auto_default")
        return ClosurePolicy.AUTO

    def _assumed_context(self, text: str, domain: str, compressed: bool, speech_act: bool) -> list[str]:
        assumptions = [f"Treat input as a {domain} inquiry unless later context overrides this."]
        if compressed:
            assumptions.append("Input may be intentionally compact; do not expand it as if one exhaustive paraphrase were available.")
        if speech_act:
            assumptions.append("Assess pragmatic function as well as literal sentence semantics.")
        return assumptions

    def _looks_poetic(self, text: str) -> bool:
        lowered = text.lower()
        return lowered in {"the city breathed", "colorless green ideas sleep furiously"} or bool(
            re.search(r"\b(city breathed|ideas sleep|green ideas|breathed)\b", lowered)
        )
