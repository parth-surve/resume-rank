"""Run real labeled/case inputs repeatedly and report score consistency."""

import argparse
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

from ai.evaluator import evaluate_candidate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="JSONL cases; see docs/AI_EVALUATION.md")
    parser.add_argument("--provider", choices=("groq", "gemini", "ollama"), default="groq")
    parser.add_argument("--prompt-version", default="v1")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.repeats < 2:
        parser.error("--repeats must be at least 2")

    cases = [
        json.loads(line)
        for line in args.dataset.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not cases:
        parser.error("dataset must contain at least one case")

    reports = []
    for case in cases:
        totals = []
        for _ in range(args.repeats):
            result = evaluate_candidate(
                resume_text=case["resume_text"],
                rubric=case["rubric"],
                domain_requirements=case["domain_requirements"],
                prompt_version=args.prompt_version,
                provider=args.provider,
            )
            totals.append(result["scores"]["total_score"])
            metadata = result["metadata"]
        reports.append({
            "case_id": case["case_id"],
            "scores": totals,
            "exact_score_consistency": len(set(totals)) == 1,
            "score_range": max(totals) - min(totals),
            "score_standard_deviation": statistics.pstdev(totals),
        })

    args.output.write_text(json.dumps({
        "run_at": datetime.now(timezone.utc).isoformat(),
        "repeats": args.repeats,
        "metadata": metadata,
        "cases": reports,
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
