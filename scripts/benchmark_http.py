"""Run an opt-in HTTP load sample against a live ResumeRank instance."""

import argparse
import concurrent.futures
import json
import time
import urllib.error
import urllib.request


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) - 1) * fraction)))
    return ordered[index]


def request_once(url: str) -> tuple[float, int]:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        status = exc.code
        exc.read()
    return time.perf_counter() - started, status


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Read-only endpoint URL, e.g. http://localhost:8000/")
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--workers", type=int, default=5)
    args = parser.parse_args()
    if args.requests < 1 or args.workers < 1:
        parser.error("--requests and --workers must be positive")

    wall_started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(lambda _: request_once(args.url), range(args.requests)))
    elapsed = time.perf_counter() - wall_started
    durations = [duration for duration, _ in results]
    statuses: dict[str, int] = {}
    for _, status in results:
        statuses[str(status)] = statuses.get(str(status), 0) + 1
    print(json.dumps({
        "url": args.url,
        "request_count": len(results),
        "worker_count": args.workers,
        "elapsed_seconds": elapsed,
        "throughput_requests_per_second": len(results) / elapsed,
        "latency_seconds": {
            "p50": percentile(durations, 0.50),
            "p95": percentile(durations, 0.95),
            "max": max(durations),
        },
        "status_counts": statuses,
    }, indent=2))


if __name__ == "__main__":
    main()
