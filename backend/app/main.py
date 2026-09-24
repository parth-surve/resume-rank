from fastapi import FastAPI

from app.api.v1.hackathons import router as hackathon_router
from app.api.v1.domains import router as domain_router
from app.api.v1.domains import nested_router as domain_nested_router
from app.api.v1.imports import router as import_router
from app.api.v1.auth import router as auth_router
from app.api.v1.candidates import router as candidates_router
from app.api.v1.resumes import router as resumes_router


app = FastAPI(title="ResumeRank Backend")


app.include_router(hackathon_router)
app.include_router(domain_router)
app.include_router(domain_nested_router)
app.include_router(import_router)
app.include_router(auth_router)
app.include_router(candidates_router)
app.include_router(resumes_router)


@app.get("/")
def root():
    return {"message": "ResumeRank Backend is running"}