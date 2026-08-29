# ResumeRank Architecture

## High-Level Flow

Organizer
    ↓
FastAPI Backend
    ↓
Screening Workflow
    ↓
Data Pipeline
    ↓
Resume Extraction
    ↓
AI Evaluation
    ↓
Scoring
    ↓
Ranking
    ↓
PostgreSQL
    ↓
Final Excel Export

## Major Components

### Backend
Handles API requests, authentication, orchestration and application logic.

### Data Pipeline
Handles Excel input/output, validation, normalization,
deduplication, resume downloading and text extraction.

### AI
Handles rubric-based evaluation, LLM interaction,
guardrails, validation, scoring and AI evaluation metrics.

### Database
PostgreSQL stores hackathons, domains, candidates,
screenings, evaluations and related information.

### Shared
Contains structures that multiple modules must agree on.

## Important Rule

Each module owns its internal implementation, but communication
between modules should use clearly defined interfaces/schemas.