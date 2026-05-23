"""
Prompt construction for RAG answer generation.
Supports evidence support levels: direct, equivalent_concept, partial.
"""

COMPLEX_QUERY_KEYWORDS = [
    "fecl4", "fecl₄", "tetrachloroferrate", "ionogel", "coordination",
    "hydrogen bonding", "ftir", "c=o", "carbonyl", "saxs", "fwhm",
    "machine learning", "deep learning", "regression", "prediction",
    "相互作用", "氢键", "红外", "羰基", "散射", "机器学习", "预测",
]


def is_complex_query(question: str) -> bool:
    """Check if query is likely complex (cross-topic, may timeout)."""
    q = question.lower()
    return any(kw in q for kw in COMPLEX_QUERY_KEYWORDS)


def build_answer_prompt(question: str, evidence_rows: list[dict], domain_hints: str = "", style: str = "concise") -> list[dict]:
    """Build OpenAI-compatible messages for answer generation.

    Args:
        question: User question
        evidence_rows: Retrieved evidence with excerpt, paper_id, title, etc.
        domain_hints: Optional domain synonym/equivalent hints for the query
    """
    evidence_block = ""
    for i, r in enumerate(evidence_rows, 1):
        mc = " [NEEDS MANUAL CHECK]" if r.get("needs_manual_check") else ""
        excerpt = r.get("excerpt", "")
        evidence_block += (
            f"\n[{i}] paper_id={r['paper_id']} | {r['title']} | "
            f"file={r['file_name']} | page={r.get('pdf_page', '')} | "
            f"category={r['category']} | confidence={r.get('confidence', '')} | "
            f"score={r.get('score', 0)}{mc}\n"
            f"Excerpt: {excerpt}\n"
        )

    hints_section = ""
    if domain_hints:
        hints_section = (
            "\n## Domain Concept Equivalents\n"
            "The following terms are conceptually equivalent or highly related in the "
            "polyurethane materials science domain. Evidence containing these terms MAY "
            "support the query concept even if the exact search term is absent:\n"
            f"{domain_hints}\n"
        )

    # Shared rules
    core_rules = (
        "## Core Rules\n"
        "- Answer based ONLY on the provided evidence excerpts.\n"
        "- NEVER fabricate paper IDs, page numbers, figures, tables, or data.\n"
        "- Respond in the same language as the question.\n\n"
        "## Evidence Support Levels\n"
        "Classify each piece of evidence:\n"
        "- **direct_evidence**: Excerpt explicitly contains query terms.\n"
        "- **equivalent_concept_evidence**: Excerpt contains domain-equivalent concepts "
        "(use Domain Concept Equivalents section below).\n"
        "- **partial_evidence**: Only supports part of the question.\n"
        "- **insufficient_evidence**: Not relevant.\n\n"
        "## How to Answer\n"
        "- direct_evidence → confidence=High.\n"
        "- equivalent_concept (2+) → confidence=Medium, explain equivalence.\n"
        "- 1 equivalent/partial → confidence=Low.\n"
        "- ALL insufficient → no_answer=true, explain what evidence DOES contain.\n"
        "- NEVER set no_answer=true just because exact term is absent — check equivalents first.\n"
    )

    if style == "concise":
        system = (
            "You are a scientific literature assistant for a polyurethane materials research corpus.\n\n"
            + core_rules +
            "## CONCISE MODE\n"
            "- Answer in 300-600 Chinese characters maximum.\n"
            "- Maximum 3 core conclusions, each tied to specific evidence.\n"
            "- No lengthy explanations or review-style writing.\n"
            "- Cite evidence by [number]. State support level for each.\n"
            "- If evidence rows need manual check, mention briefly.\n\n"
            "## Response Format (JSON)\n"
            '{"answer": "...(300-600 chars max)...", '
            '"confidence": "High|Medium|Low", '
            '"no_answer": false, '
            '"evidence_levels": {"direct": [], "equivalent_concept": [], "partial": [], "insufficient": []}, '
            '"cited_evidence": [1, 2], '
            '"warnings": ["..."]}'
        )
    else:
        system = (
            "You are a scientific literature assistant for a polyurethane materials research corpus.\n\n"
            + core_rules +
            "## Citation Format\n"
            "- Cite evidence by [number] matching the evidence list.\n"
            "- For each cited evidence, state its support level.\n"
            "- If evidence rows need manual check, mention this as a warning.\n\n"
            "## Response Format (JSON)\n"
            '{"answer": "...", '
            '"confidence": "High|Medium|Low", '
            '"no_answer": false, '
            '"evidence_levels": {"direct": [1,2], "equivalent_concept": [3,4], "partial": [5], "insufficient": [6,7,8]}, '
            '"cited_evidence": [1, 2, 3, 4], '
            '"warnings": ["..."]}'
        )

    user = f"Question: {question}\n\nEvidence excerpts:\n{evidence_block}{hints_section}"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_query_expansion_prompt(question: str, max_expansions: int = 3) -> list[dict]:
    """Build prompt for query expansion."""
    system = (
        "You are a scientific literature search assistant. "
        "Given a research question, generate alternative phrasings that would help find relevant papers. "
        'Return a JSON object: {"expansions": ["alt1", "alt2", ...]}'
    )
    user = (
        f"Original question: {question}\n\n"
        f"Generate up to {max_expansions} alternative search queries that cover different aspects or synonyms."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
