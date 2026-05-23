"""
Citation formatting for RAG answers.
"""


def format_evidence_row(idx: int, row: dict, score: float = 0.0, support_level: str = "") -> dict:
    """Format an evidence row into the standard citation structure."""
    return {
        "evidence_id": f"ev_{idx:04d}",
        "paper_id": row.get("paper_id", ""),
        "title": row.get("display_title") or row.get("title", ""),
        "file_name": row.get("file_name", ""),
        "pdf_page": row.get("page_est", ""),
        "category": row.get("category", ""),
        "claim_type": row.get("claim_type", ""),
        "relevance": row.get("relevance", ""),
        "confidence": row.get("confidence", ""),
        "excerpt": row.get("evidence_text", ""),
        "score": round(score, 4),
        "needs_manual_check": row.get("needs_manual_check", "").lower() == "true",
        "support_level": support_level,
    }


def format_citation_text(evidence_rows: list[dict]) -> str:
    """Format evidence as readable citation text."""
    lines = []
    for i, r in enumerate(evidence_rows, 1):
        mc = " [MANUAL CHECK]" if r.get("needs_manual_check") else ""
        lines.append(
            f"[{i}] {r.get('paper_id', '?')} — {r.get('title', 'Untitled')} "
            f"(p.{r.get('pdf_page', '?')}, {r.get('category', '')}){mc}"
        )
    return "\n".join(lines)
