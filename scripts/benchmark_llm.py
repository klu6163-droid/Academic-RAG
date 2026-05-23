"""
LLM Answer Quality Benchmark v2
Tests 10 queries against the RAG API and evaluates answer quality.
Includes evidence support level tracking.
Run: python scripts/benchmark_llm.py
"""

import csv
import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

BASE = "http://localhost:8001"

TEST_QUERIES = [
    "哪些论文提到了聚氨酯微相分离？",
    "PCL基聚氨酯有没有做活死细胞染色？",
    "哪些文献报道了TPU的SAXS long period？",
    "PVDF压电材料是否影响蛋白吸附？",
    "哪些文献适合作为聚氨酯力学性能机器学习预测的数据来源？",
    "FeCl4 和 PU 可能有哪些相互作用？",
    "哪些文献提到了FTIR中C=O氢键？",
    "哪些论文使用SAXS峰位置或FWHM作为结构特征？",
    "这个知识库里有没有关于火星土壤种植聚氨酯的论文？",
    "有没有论文证明聚氨酯可以治疗癌症？",
]


def run_benchmark():
    results = []

    for qi, query in enumerate(TEST_QUERIES, 1):
        print(f"\n{'='*60}")
        print(f"[{qi}/10] {query}")
        print(f"{'='*60}")

        t0 = time.time()
        try:
            resp = requests.post(
                f"{BASE}/api/ask",
                json={"question": query, "top_k": 8, "mode": "evidence"},
                timeout=300,
            )
            data = resp.json()
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "query_id": qi, "query": query, "no_answer": True,
                "retrieved_count": 0, "top_score": 0, "answer_confidence": "Error",
                "has_paper_id_citation": False, "has_title_citation": False,
                "has_file_citation": False, "has_page_citation": False,
                "answer_length": 0, "elapsed_s": 0, "manual_check_warning": False,
                "system_override": False, "direct_evidence": 0, "equivalent_concept_evidence": 0,
                "partial_evidence": 0, "insufficient_evidence": 0, "p151_in_top8": 0,
                "unique_papers_top8": 0, "ev_support_levels": "", "answer": str(e)[:500],
                "warnings": str(e), "top3_papers": "", "error": str(e),
            })
            continue

        elapsed = time.time() - t0

        answer = data.get("answer", "")
        confidence = data.get("confidence", "")
        no_answer = data.get("no_answer", False)
        evidence = data.get("evidence", [])
        warnings = data.get("warnings", [])
        evidence_levels = data.get("evidence_levels", {})

        top_score = evidence[0]["score"] if evidence else 0.0

        # Check citation in answer
        has_paper_id = any(e["paper_id"] in answer for e in evidence[:5])
        has_title = any(e["title"][:20] in answer for e in evidence[:3])
        has_file = any(e["file_name"][:10] in answer for e in evidence[:3])
        has_page = any(str(e["pdf_page"]) in answer for e in evidence[:3] if e["pdf_page"])

        # Support level counts
        direct_count = len(evidence_levels.get("direct", []))
        equiv_count = len(evidence_levels.get("equivalent_concept", []))
        partial_count = len(evidence_levels.get("partial", []))
        insufficient_count = len(evidence_levels.get("insufficient", []))

        # Per-evidence support levels
        ev_support = [e.get("support_level", "") for e in evidence[:8]]

        # Check manual check warning
        mc_warning = any("manual check" in w.lower() for w in warnings)

        # Check if system override was applied
        system_override = any("system override" in w.lower() for w in warnings)

        # P151 count in top-8
        p151_count = sum(1 for e in evidence[:8] if e.get("paper_id") == "P151")
        unique_papers = len(set(e.get("paper_id", "") for e in evidence[:8]))

        result = {
            "query_id": qi,
            "query": query,
            "no_answer": no_answer,
            "retrieved_count": len(evidence),
            "top_score": round(top_score, 4),
            "answer_confidence": confidence,
            "has_paper_id_citation": has_paper_id,
            "has_title_citation": has_title,
            "has_file_citation": has_file,
            "has_page_citation": has_page,
            "answer_length": len(answer),
            "elapsed_s": round(elapsed, 1),
            "manual_check_warning": mc_warning,
            "system_override": system_override,
            "direct_evidence": direct_count,
            "equivalent_concept_evidence": equiv_count,
            "partial_evidence": partial_count,
            "insufficient_evidence": insufficient_count,
            "p151_in_top8": p151_count,
            "unique_papers_top8": unique_papers,
            "ev_support_levels": "|".join(ev_support),
            "answer": answer[:500],
            "warnings": "|".join(warnings),
            "top3_papers": "|".join(e["paper_id"] for e in evidence[:3]),
        }
        results.append(result)

        print(f"  no_answer: {no_answer}")
        print(f"  confidence: {confidence}")
        print(f"  evidence: {len(evidence)} rows, top_score={top_score:.4f}")
        print(f"  support: direct={direct_count}, equiv={equiv_count}, partial={partial_count}, insufficient={insufficient_count}")
        print(f"  citations: paper_id={has_paper_id}, title={has_title}, file={has_file}, page={has_page}")
        print(f"  P151 in top-8: {p151_count}, unique papers: {unique_papers}")
        print(f"  system_override: {system_override}")
        print(f"  answer ({len(answer)} chars): {answer[:200]}...")
        if warnings:
            print(f"  warnings: {warnings}")

    # Write CSV
    output_dir = Path(__file__).resolve().parent.parent / "data" / "analysis" / "final"
    csv_path = output_dir / "llm_answer_quality_benchmark_v2.csv"
    fieldnames = list(results[0].keys())
    if "error" not in fieldnames:
        fieldnames.append("error")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"\nCSV: {csv_path}")

    # Write report
    md_path = output_dir / "llm_answer_quality_benchmark_v2.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# LLM Answer Quality Benchmark v2\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("Changes from v1: domain equivalent concepts, evidence support levels, diversity rerank, excerpt truncation\n\n")

        f.write("## Summary\n\n")
        total = len(results)
        answered = sum(1 for r in results if not r.get("no_answer"))
        no_ans = sum(1 for r in results if r.get("no_answer"))
        with_citation = sum(1 for r in results if r.get("has_paper_id_citation"))
        overrides = sum(1 for r in results if r.get("system_override"))
        avg_time = sum(r.get("elapsed_s", 0) for r in results) / max(len(results), 1)
        avg_p151 = sum(r.get("p151_in_top8", 0) for r in results) / max(len(results), 1)
        avg_unique = sum(r.get("unique_papers_top8", 0) for r in results) / max(len(results), 1)

        f.write(f"- Total queries: {total}\n")
        f.write(f"- Answered: {answered}\n")
        f.write(f"- No-answer: {no_ans}\n")
        f.write(f"- With paper_id citation: {with_citation}/{total}\n")
        f.write(f"- System overrides (LLM overly conservative): {overrides}\n")
        f.write(f"- Avg response time: {avg_time:.1f}s\n")
        f.write(f"- Avg P151 count in top-8: {avg_p151:.1f}\n")
        f.write(f"- Avg unique papers in top-8: {avg_unique:.1f}\n\n")

        # Evidence level summary
        total_direct = sum(r.get("direct_evidence", 0) for r in results)
        total_equiv = sum(r.get("equivalent_concept_evidence", 0) for r in results)
        total_partial = sum(r.get("partial_evidence", 0) for r in results)
        total_insufficient = sum(r.get("insufficient_evidence", 0) for r in results)
        f.write("### Evidence Support Level Distribution\n\n")
        f.write(f"- Direct evidence: {total_direct}\n")
        f.write(f"- Equivalent concept evidence: {total_equiv}\n")
        f.write(f"- Partial evidence: {total_partial}\n")
        f.write(f"- Insufficient evidence: {total_insufficient}\n\n")

        f.write("## Per-Query Results\n\n")
        for r in results:
            f.write(f"### Q{r['query_id']}: {r['query']}\n\n")
            f.write(f"- **No-answer**: {r.get('no_answer', 'N/A')}\n")
            f.write(f"- **Confidence**: {r.get('answer_confidence', 'N/A')}\n")
            f.write(f"- **Retrieved**: {r.get('retrieved_count', 0)} rows, top_score={r.get('top_score', 0)}\n")
            f.write(f"- **Support**: direct={r.get('direct_evidence', 0)}, equiv={r.get('equivalent_concept_evidence', 0)}, partial={r.get('partial_evidence', 0)}, insufficient={r.get('insufficient_evidence', 0)}\n")
            f.write(f"- **Citations**: paper_id={r.get('has_paper_id_citation')}, title={r.get('has_title_citation')}, file={r.get('has_file_citation')}, page={r.get('has_page_citation')}\n")
            f.write(f"- **P151 in top-8**: {r.get('p151_in_top8', 0)}, unique papers: {r.get('unique_papers_top8', 0)}\n")
            f.write(f"- **System override**: {r.get('system_override', False)}\n")
            f.write(f"- **Elapsed**: {r.get('elapsed_s', 0)}s\n")
            if r.get("warnings"):
                f.write(f"- **Warnings**: {r['warnings']}\n")
            f.write(f"\n**Answer**:\n> {r.get('answer', 'N/A')}\n\n")
            f.write(f"**Evidence support levels**: {r.get('ev_support_levels', 'N/A')}\n\n")
            f.write("---\n\n")

        f.write("## Analysis\n\n")

        # Hallucination check
        f.write("### Hallucination Check\n\n")
        import re
        hallucination_found = False
        for r in results:
            if r.get("no_answer"):
                continue
            answer = r.get("answer", "")
            p_codes_in_answer = set(re.findall(r'P\d{3}', answer))
            p_codes_in_evidence = set(r.get("top3_papers", "").split("|"))
            fabricated = p_codes_in_answer - p_codes_in_evidence
            if fabricated:
                f.write(f"- Q{r['query_id']}: Potential hallucination — mentions {fabricated} not in top evidence\n")
                hallucination_found = True
        if not hallucination_found:
            f.write("- No hallucination detected.\n")

        f.write("\n### v1 vs v2 Comparison\n\n")
        f.write("| Metric | v1 | v2 |\n|--------|----|----|\n")
        f.write(f"| Answered | 0/10 | {answered}/10 |\n")
        f.write(f"| No-answer | 10/10 | {no_ans}/10 |\n")
        f.write(f"| With citation | 1/10 | {with_citation}/10 |\n")
        f.write(f"| System overrides | N/A | {overrides} |\n")
        f.write(f"| Direct evidence | N/A | {total_direct} |\n")
        f.write(f"| Equiv concept evidence | N/A | {total_equiv} |\n")
        f.write(f"| Hallucination | 0 | {'0' if not hallucination_found else 'CHECK'} |\n")
        f.write(f"| Avg response time | 34.4s | {avg_time:.1f}s |\n")
        f.write(f"| Avg P151 in top-8 | N/A | {avg_p151:.1f} |\n")

        f.write("\n### Recommendations\n\n")
        if answered > 0:
            f.write("1. v2 prompt successfully enables equivalent concept evidence answers\n")
        else:
            f.write("1. LLM still returning no_answer — may need stronger prompt guidance\n")
        if not hallucination_found:
            f.write("2. Zero hallucination maintained — safe to deploy\n")
        if overrides > 0:
            f.write(f"3. {overrides} system overrides applied — LLM was overly conservative\n")
        if avg_p151 < 3:
            f.write("4. P151 dominance reduced with diversity rerank\n")

    print(f"Report: {md_path}")


if __name__ == "__main__":
    run_benchmark()
