from contextlib import asynccontextmanager
from time import perf_counter
import logging
import re
import threading

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.core.logging import setup_logging
from app.api.v1.hackathons import router as hackathon_router
from app.api.v1.domains import router as domain_router
from app.api.v1.domains import nested_router as domain_nested_router
from app.api.v1.imports import router as import_router
from app.api.v1.auth import router as auth_router
from app.api.v1.candidates import router as candidates_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.screenings import router as screenings_router
from app.core.metrics import HTTP_REQUESTS, HTTP_REQUEST_DURATION, metrics_response

logger = logging.getLogger(__name__)


def _resume_interrupted_screenings() -> None:
    """
    Called once at startup in a background thread.

    Finds all screenings that were IN_PROGRESS when the server last shut down,
    resets any stuck PROCESSING candidates back to PENDING, then re-queues
    the screening as a background thread so it continues from where it left off.

    No DB model changes required — uses existing status fields.
    """
    from app.db.database import SessionLocal
    from app.db.models import (
        CandidateProcessing,
        CandidateProcessingStatus,
        Screening,
        ScreeningStatus,
    )
    from app.workflows.screening_workflow import run_screening

    db = SessionLocal()
    try:
        # Only resume the SINGLE most recent IN_PROGRESS screening.
        # Running multiple screenings concurrently exhausts the DB connection
        # pool and hammers the GPU simultaneously. One at a time is correct.
        screening = (
            db.query(Screening)
            .filter(Screening.status == ScreeningStatus.IN_PROGRESS)
            .order_by(Screening.id.desc())
            .first()
        )

        if not screening:
            logger.info("Startup resume: no interrupted screenings found.")
            return

        logger.warning(
            "Startup resume: found interrupted screening %s — resuming.",
            screening.id,
        )

        # Reset any candidates stuck in PROCESSING -> PENDING
        stuck = (
            db.query(CandidateProcessing)
            .filter(
                CandidateProcessing.screening_id == screening.id,
                CandidateProcessing.status == CandidateProcessingStatus.PROCESSING,
            )
            .all()
        )

        if stuck:
            logger.info(
                "Startup resume: resetting %d stuck candidate(s) "
                "in screening %s -> PENDING",
                len(stuck),
                screening.id,
            )
            for cp in stuck:
                cp.status = CandidateProcessingStatus.PENDING
            db.commit()

        pending_count = (
            db.query(CandidateProcessing)
            .filter(
                CandidateProcessing.screening_id == screening.id,
                CandidateProcessing.status == CandidateProcessingStatus.PENDING,
            )
            .count()
        )

        if pending_count == 0:
            logger.info(
                "Startup resume: screening %s has no pending candidates — skipping.",
                screening.id,
            )
            return

        logger.info(
            "Startup resume: re-queuing screening %s (%d pending candidates).",
            screening.id,
            pending_count,
        )

        screening_id = screening.id

        def _run(sid: int) -> None:
            bg_db = SessionLocal()
            try:
                run_screening(sid, bg_db)
            except Exception:
                logger.exception(
                    "Startup resume: screening %s failed during auto-resume.", sid
                )
            finally:
                bg_db.close()

        t = threading.Thread(
            target=_run,
            args=(screening_id,),
            name=f"auto-resume-screening-{screening_id}",
            daemon=True,
        )
        t.start()

    except Exception:
        logger.exception("Startup resume: unexpected error during auto-resume check.")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: auto-resume interrupted screenings on startup."""
    setup_logging()
    # Run resume check in a thread so it doesn't block server startup
    t = threading.Thread(
        target=_resume_interrupted_screenings,
        name="startup-resume-check",
        daemon=True,
    )
    t.start()
    yield
    # (shutdown logic goes here if needed)


app = FastAPI(title="ResumeRank Backend", lifespan=lifespan)


# Setup CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.middleware("http")
async def record_http_metrics(request: Request, call_next) -> Response:
    if request.url.path == "/metrics":
        return await call_next(request)

    started = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        route = request.scope.get("route")
        path = getattr(route, "path", None)
        if path is None:
            raw_path = request.url.path
            path = re.sub(r"/\d+(?=/|$)", "/{id}", raw_path)
            if path != "/" and not path.startswith("/api/"):
                path = "other"
        HTTP_REQUESTS.labels(request.method, path, str(status_code)).inc()
        HTTP_REQUEST_DURATION.labels(request.method, path).observe(
            perf_counter() - started
        )


@app.get("/metrics", include_in_schema=False)
def prometheus_metrics():
    return metrics_response()


@app.get("/health", tags=["system"])
def health_check():
    return {
        "status": "healthy",
        "service": "ResumeRank",
    }


app.include_router(hackathon_router)
app.include_router(domain_router)
app.include_router(domain_nested_router)
app.include_router(import_router)
app.include_router(auth_router)
app.include_router(candidates_router)
app.include_router(resumes_router)
app.include_router(screenings_router)


@app.get("/")
def root():
    return {"message": "ResumeRank Backend is running"}

