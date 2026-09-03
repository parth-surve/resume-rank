from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import hackathons

app = FastAPI(title=settings.APP_NAME)

app.include_router(hackathons.router)