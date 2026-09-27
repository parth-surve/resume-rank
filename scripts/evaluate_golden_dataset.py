"""Evaluate labeled JSONL cases and emit measured agreement metrics."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from ai.evaluation import compare_rankings, compare_scores, classification_metrics
from ai.evaluator import evaluate_candidate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--provider", choices=("groq", "gemini", "ollama"), default="groq")
    parser.add_argument("--prompt-version", default="v1")
    parser.add_argument("--positive-threshold", type=float)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cases = [
        json.loads(line)
        for line in args.dataset.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not cases:
        parser.error("dataset must contain at least one case")
    case_ids = [case["case_id"] for case in cases]
    if len(set(case_ids)) != len(case_ids):
        parser.error("case_id values must be unique")

    measured = []
    metadata = None
    for case in cases:
        result = evaluate_candidate(
            resume_text=case["resume_text"],
            rubric=case["rubric"],
            domain_requirements=case["domain_requirements"],
            prompt_version=args.prompt_version,
            provider=args.provider,
        )
        measured.append({
            "case_id": case["case_id"],
            "predicted_score": result["scores"]["total_score"],
            "human_score": case.get("human_score"),
            "human_positive": case.get("human_positive"),
            "human_rank": case.get("human_rank"),
        })
        metadata = result["metadata"]

    labeled_scores = [row for row in measured if row["human_score"] is not None]
    metrics = {}
    if labeled_scores:
        metrics["score_agreement"] = compare_scores(
            [row["human_score"] for row in labeled_scores],
            [row["predicted_score"] for row in labeled_scores],
        )

    labeled_binary = [row for row in measured if row["human_positive"] is not None]
    if labeled_binary and args.positive_threshold is not None:
        metrics["classification"] = classification_metrics(
            {row["case_id"]: bool(row["human_positive"]) for row in labeled_binary},
            {
                row["case_id"]: row["predicted_score"] >= args.positive_threshold
                for row in labeled_binary
            },
        )

    ranked_groups: dict[str, list[dict]] = {}
    for case in cases:
        if case.get("ranking_group") is not None and case.get("human_rank") is not None:
            ranked_groups.setdefault(case["ranking_group"], []).append(case)
    if ranked_groups:
        score_by_id = {row["case_id"]: row["predicted_score"] for row in measured}
        ranking_results = {}
        for group, group_cases in ranked_groups.items():
            if len(group_cases) < 2:
                continue
            human_order = [
                row["case_id"] for row in sorted(group_cases, key=lambda row: row["human_rank"])
            ]
            predicted_order = sorted(
                human_order, key=lambda case_id: score_by_id[case_id], reverse=True
            )
            ranking_results[group] = compare_rankings(human_order, predicted_order)
        if ranking_results:
            metrics["ranking_agreement_by_group"] = ranking_results

    args.output.write_text(json.dumps({
        "run_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata,
        "case_count": len(measured),
        "labeled_score_case_count": len(labeled_scores),
        "labeled_binary_case_count": len(labeled_binary),
        "metrics": metrics,
        "cases": measured,
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
