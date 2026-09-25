from fastapi import FastAPI

from app.core.config import settings
from app.api.v1 import hackathons, domains, screenings
from app.api.v1.imports import router as import_router
from app.api.v1.auth import router as auth_router


app = FastAPI(
    title=settings.APP_NAME,
)


app.include_router(hackathons.router)
app.include_router(domains.router)
app.include_router(domains.nested_router)
app.include_router(import_router)
app.include_router(auth_router)
app.include_router(screenings.router)

@app.get("/")
def root():
    return {"message": "ATS Backend is running"}