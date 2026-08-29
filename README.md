# ResumeRank

AI-powered resume screening and ranking system for hackathons.

## Purpose

ResumeRank processes domain-specific participant Excel files,
downloads and extracts resume content, evaluates candidates using
an AI-based scoring rubric, ranks candidates, and generates a
final Excel containing the original participant data plus screening
results.

## Project Structure

- `backend/` — FastAPI backend and application logic
- `data_pipeline/` — Excel processing and resume handling
- `ai/` — AI evaluation, scoring, guardrails and AI evaluation metrics
- `shared/` — Shared schemas, enums and constants
- `scripts/` — Development/testing utilities
- `tests/` — Automated and integration tests
- `docs/` — Project documentation

## Status

🚧 Under development