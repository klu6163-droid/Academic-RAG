"""
Answer generator: orchestrates retrieval + LLM call + no-answer gate.
Supports evidence levels: direct, equivalent_concept, partial, insufficient.
"""

import json
from pathlib import Path

import yaml

from src.rag.prompt_builder import build_answer_prompt, build_query_expansion_prompt, is_complex_query

DOMAIN_EQUIV_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "domain_equivalents.yaml"


def load_domain_equivalents() -> dict:
    """Load domain equivalents from YAML config."""
    if not DOMAIN_EQUIV_PATH.exists():
        return {}
    with open(DOMAIN_EQUIV_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_domain_hints(query_concept: str, domain_eq: dict) -> str:
    """Build domain hint text for a query concept.

    Matches query against query_keywords in domain equivalent categories and returns
    formatted hint text for the LLM prompt.
    """
    if not domain_eq:
        return ""

    query_lower = query_concept.lower()
    hints = []

    for concept_key, terms in domain_eq.items():
        query_keywords = terms.get("query_keywords", [])
        direct = terms.get("direct_terms", [])
        equiv = terms.get("equivalent_terms", [])

        # Match query against query_keywords for this concept
        matched = any(kw.lower() in query_lower or query_lower in kw.lower() for kw in query_keywords)
        if not matched:
            # Fallback: check if any query word appears in keywords
            for kw in query_keywords:
                if any(w in kw.lower() for w in query_lower.split() if len(w) > 1):
                    matched = True
                    break
        if not matched:
            continue

        hint_lines = [f"### {concept_key}"]
        if direct:
            hint_lines.append(f"Direct terms: {', '.join(direct)}")
        if equiv:
            hint_lines.append(f"Equivalent concepts: {', '.join(equiv)}")
        hints.append("\n".join(hint_lines))

    return "\n\n".join(hints)


class AnswerGenerator:
    def __init__(self, llm_client, config):
        self.llm = llm_client
        self.cfg = config.answering
        self.qe_cfg = config.query_expansion
        self.domain_eq = load_domain_equivalents()

    def expand_query(self, question: str) -> list[str]:
        """Expand query using LLM. Returns list of alternative queries."""
        if not self.qe_cfg.enabled or not self.llm.is_available:
            return []
        try:
            messages = build_query_expansion_prompt(question, self.qe_cfg.max_expansions)
            result = self.llm.chat_json(messages)
            return result.get("expansions", [])[:self.qe_cfg.max_expansions]
        except Exception:
            return []

    def check_no_answer(self, evidence_rows: list[dict], top_score: float) -> tuple[bool, str]:
        """Deterministic no-answer gate. Returns (no_answer, reason)."""
        if len(evidence_rows) == 0:
            return True, "No evidence retrieved."

        if top_score < self.cfg.no_answer_threshold:
            return True, f"Top retrieval score ({top_score:.3f}) below threshold ({self.cfg.no_answer_threshold})."

        effective = [r for r in evidence_rows if r.get("score", 0) >= self.cfg.min_retrieval_score]
        if len(effective) < self.cfg.min_evidence_chunks:
            return True, f"Only {len(effective)} evidence chunks above minimum score threshold."

        return False, ""

    def generate(self, question: str, evidence_rows: list[dict], answer_style: str = "concise") -> dict:
        """Generate answer from question and evidence. Returns structured response."""
        # No-answer gate
        top_score = evidence_rows[0]["score"] if evidence_rows else 0.0
        no_answer, reason = self.check_no_answer(evidence_rows, top_score)

        if no_answer:
            return {
                "answer": "当前知识库中没有足够证据支持该回答。",
                "confidence": "Low",
                "no_answer": True,
                "evidence_levels": {"direct": [], "equivalent_concept": [], "partial": [], "insufficient": list(range(1, len(evidence_rows) + 1))},
                "cited_evidence": [],
                "warnings": [reason],
            }

        if not self.llm.is_available:
            return {
                "answer": "",
                "confidence": "Low",
                "no_answer": True,
                "evidence_levels": {"direct": [], "equivalent_concept": [], "partial": [], "insufficient": []},
                "cited_evidence": [],
                "warnings": ["LLM API key not configured. Set LLM_API_KEY or OPENAI_API_KEY in .env"],
            }

        # Build domain hints for the prompt
        domain_hints = build_domain_hints(question, self.domain_eq)

        # Auto-detect: complex queries use concise mode to avoid timeout
        effective_style = answer_style
        if answer_style == "detailed" and is_complex_query(question):
            effective_style = "concise"

        # LLM answer generation — concise mode uses top-5, detailed uses top-8
        max_chunks = 5 if effective_style == "concise" else self.cfg.max_context_chunks
        context = evidence_rows[:max_chunks]
        total_excerpt_chars = sum(len(r.get("excerpt", "")) for r in context)
        if total_excerpt_chars > 2500:
            context = evidence_rows[:5]

        try:
            messages = build_answer_prompt(question, context, domain_hints=domain_hints, style=effective_style)
            parsed = self.llm.chat_json(messages)

            # Post-process: if LLM returned no_answer but has substantive answer, override
            #
            # OVERRIDE GUARDRAILS:
            # ALLOWED: LLM set no_answer=true due to missing exact term, but answer discusses
            #          evidence relationships and evidence has valid paper_id + excerpt.
            # BLOCKED: - top_score < 0.017 (handled by deterministic gate above, never reaches here)
            #          - answer < 100 chars (not substantive)
            #          - evidence lacks paper_id or excerpt (invalid metadata)
            #          - answer contains no evidence discussion keywords
            #          - nonsense queries (Q9/Q10) are blocked by gate, never reach override
            llm_no_answer = parsed.get("no_answer", False) or False
            evidence_levels = parsed.get("evidence_levels") or {}
            equiv_count = len(evidence_levels.get("equivalent_concept", []))
            answer_text = parsed.get("answer") or ""
            confidence = parsed.get("confidence") or "Low"

            if llm_no_answer and len(answer_text) > 100:
                # Verify evidence quality before override
                has_valid_evidence = any(
                    r.get("paper_id") and r.get("excerpt")
                    for r in context
                )
                if has_valid_evidence:
                    answer_lower = answer_text.lower()
                    has_evidence_discussion = any(
                        kw in answer_lower for kw in [
                            "但", "虽然", "涉及", "相关", "支持", "证据", "摘录",
                            "however", "although", "讨论", "提及",
                            "but discuss", "related to", "supports",
                        ]
                    )
                    if has_evidence_discussion:
                        llm_no_answer = False
                        if not parsed.get("warnings"):
                            parsed["warnings"] = []
                        parsed["warnings"].append(
                            "System override: LLM provided substantive evidence analysis but marked no_answer. "
                            "Answer restored based on evidence discussion in response."
                        )
                        if equiv_count == 0 and confidence.lower() == "high":
                            confidence = "Medium"

            return {
                "answer": answer_text,
                "confidence": confidence,
                "no_answer": llm_no_answer,
                "evidence_levels": evidence_levels,
                "cited_evidence": parsed.get("cited_evidence") or [],
                "warnings": parsed.get("warnings") or [],
            }
        except Exception as e:
            # On timeout or error, return retrieve-only result with evidence
            is_timeout = isinstance(e, TimeoutError) or "timeout" in type(e).__name__.lower() or "timeout" in str(e).lower()
            if is_timeout:
                return {
                    "answer": "LLM 回答超时。以下为检索到的相关证据，请基于 evidence cards 人工判断。",
                    "confidence": "Low",
                    "no_answer": False,
                    "evidence_levels": {"direct": [], "equivalent_concept": [], "partial": [], "insufficient": list(range(1, len(evidence_rows) + 1))},
                    "cited_evidence": [],
                    "warnings": ["LLM answer timed out; retrieved evidence shown below."],
                }
            return {
                "answer": "",
                "confidence": "Low",
                "no_answer": True,
                "evidence_levels": {"direct": [], "equivalent_concept": [], "partial": [], "insufficient": list(range(1, len(evidence_rows) + 1))},
                "cited_evidence": [],
                "warnings": [f"LLM error: {type(e).__name__}: {str(e)[:200]}"],
            }
