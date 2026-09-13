from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import hackathons,domains,imports,screenings,candidates

app = FastAPI(title=settings.APP_NAME)

app.include_router(hackathons.router)

app.include_router(domains.router)
app.include_router(domains.nested_router)
app.include_router(imports.router)
app.include_router(screenings.router)
app.include_router(candidates.router)