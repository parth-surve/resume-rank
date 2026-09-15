from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import hackathons,domains
from app.api.v1.auth import router as auth_router
app.include_router(auth_router)

app = FastAPI(title=settings.APP_NAME)

app.include_router(hackathons.router)

app.include_router(domains.router)
app.include_router(domains.nested_router)