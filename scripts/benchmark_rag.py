"""
RAG Benchmark: test query quality across retrieval modes.
Run: python scripts/benchmark_rag.py
"""

import csv
import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag.service import get_service

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

MODES = ["evidence"]  # Add "full_paper" and "hybrid" when available


def run_benchmark():
    svc = get_service()
    svc.initialize()

    results = []
    print(f"RAG Benchmark — {len(TEST_QUERIES)} queries x {len(MODES)} modes")
    print(f"Evidence rows: {len(svc.evidence)}")
    print(f"FAISS vectors: {svc.vector_store.num_vectors}")
    print(f"BM25 ready: {svc.bm25.is_ready}")
    print("=" * 80)

    for qi, query in enumerate(TEST_QUERIES, 1):
        for mode in MODES:
            t0 = time.time()
            rows, warnings = svc.retrieve(query, top_k=8, mode=mode)
            elapsed = time.time() - t0

            top_score = rows[0]["score"] if rows else 0.0
            top_papers = [r["paper_id"] for r in rows[:5]]
            top_titles = [r["title"][:50] for r in rows[:5]]
            top_pages = [r["pdf_page"] for r in rows[:5]]

            # Check no-answer gate
            no_answer, no_answer_reason = svc.answer_generator.check_no_answer(rows, top_score)

            result = {
                "query_id": qi,
                "query": query,
                "mode": mode,
                "retrieved_count": len(rows),
                "top_score": round(top_score, 4),
                "no_answer": no_answer,
                "no_answer_reason": no_answer_reason,
                "top5_papers": "|".join(top_papers),
                "top5_titles": "|".join(top_titles),
                "top5_pages": "|".join(top_pages),
                "warnings": "|".join(warnings),
                "elapsed_ms": round(elapsed * 1000),
            }
            results.append(result)

            status = "NO-ANSWER" if no_answer else "OK"
            print(f"[{qi}] {mode:10s} | {status:10s} | score={top_score:.4f} | {len(rows)} rows | {elapsed:.1f}s | {query[:40]}...")
            if rows:
                for i, r in enumerate(rows[:3]):
                    print(f"     [{i+1}] {r['paper_id']} | {r['score']:.4f} | {r['title'][:50]}")

    # Write results CSV
    output_dir = Path(__file__).resolve().parent.parent / "data" / "analysis" / "final"
    csv_path = output_dir / "rag_benchmark_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nCSV: {csv_path}")

    # Write report
    report_path = output_dir / "rag_benchmark_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# RAG Benchmark Report\n\n")
        f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write("## Configuration\n\n")
        f.write(f"- Evidence rows: {len(svc.evidence)}\n")
        f.write(f"- FAISS vectors: {svc.vector_store.num_vectors}\n")
        f.write(f"- BM25: k1={svc.config.bm25.k1}, b={svc.config.bm25.b}\n")
        f.write(f"- RRF k: {svc.config.hybrid.rrf_k}\n")
        f.write(f"- Embedding model: {svc.config.embedding.model}\n")
        f.write(f"- No-answer threshold: {svc.config.answering.no_answer_threshold}\n")
        f.write(f"- Min retrieval score: {svc.config.answering.min_retrieval_score}\n\n")

        f.write("## Score Distribution\n\n")
        scores = [r["top_score"] for r in results]
        relevant_scores = [r["top_score"] for r in results if not r["no_answer"]]
        no_answer_scores = [r["top_score"] for r in results if r["no_answer"]]

        f.write(f"- All queries: min={min(scores):.4f}, max={max(scores):.4f}, mean={sum(scores)/len(scores):.4f}\n")
        if relevant_scores:
            f.write(f"- Relevant (answered): min={min(relevant_scores):.4f}, max={max(relevant_scores):.4f}, mean={sum(relevant_scores)/len(relevant_scores):.4f}\n")
        if no_answer_scores:
            f.write(f"- No-answer: min={min(no_answer_scores):.4f}, max={max(no_answer_scores):.4f}, mean={sum(no_answer_scores)/len(no_answer_scores):.4f}\n")

        f.write("\n## Per-Query Results\n\n")
        f.write("| # | Query | Mode | Score | Count | No-Answer | Top Papers |\n")
        f.write("|---|-------|------|-------|-------|-----------|------------|\n")
        for r in results:
            na = "YES" if r["no_answer"] else "no"
            f.write(f"| {r['query_id']} | {r['query'][:30]}... | {r['mode']} | {r['top_score']:.4f} | {r['retrieved_count']} | {na} | {r['top5_papers'][:30]} |\n")

        f.write("\n## Threshold Analysis\n\n")
        f.write("Current thresholds:\n")
        f.write(f"- no_answer_threshold: {svc.config.answering.no_answer_threshold}\n")
        f.write(f"- min_retrieval_score: {svc.config.answering.min_retrieval_score}\n\n")

        if relevant_scores and no_answer_scores:
            gap = min(relevant_scores) - max(no_answer_scores)
            f.write(f"Score gap between lowest relevant and highest no-answer: {gap:.4f}\n\n")
            if gap > 0:
                suggested = max(no_answer_scores) + gap * 0.5
                f.write(f"Suggested no_answer_threshold: {suggested:.4f}\n")
            else:
                f.write("WARNING: Score distributions overlap. Current threshold may cause false positives/negatives.\n")
                f.write("Consider using evidence quality signals (claim_type, confidence) in addition to score.\n")

        f.write("\n## Recommendations\n\n")
        f.write("1. evidence mode is the default and recommended mode for curated, high-quality evidence.\n")
        f.write("2. full_paper mode should be enabled when a 37K-chunk FAISS index is built from extracted texts.\n")
        f.write("3. hybrid mode will automatically fall back to full_paper when evidence is insufficient.\n")

    print(f"Report: {report_path}")


if __name__ == "__main__":
    run_benchmark()
