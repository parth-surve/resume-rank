from time import perf_counter
import re

from fastapi import FastAPI, Request
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


app = FastAPI(title="ResumeRank Backend")


setup_logging()


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
