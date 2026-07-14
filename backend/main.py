from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import init_db
from routes import (
    auth,
    leads,
    qualification,
    emails,
    followups,
    pipeline,
    analytics,
    recommendations,
    settings as settings_routes,
)

app_settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=app_settings.app_name,
    version=app_settings.app_version,
    description="AI-powered sales assistant for lead qualification, email drafting, and pipeline management.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(leads.router)
app.include_router(qualification.router)
app.include_router(emails.router)
app.include_router(followups.router)
app.include_router(pipeline.router)
app.include_router(analytics.router)
app.include_router(recommendations.router)
app.include_router(settings_routes.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": app_settings.app_name,
        "version": app_settings.app_version,
        "ai_enabled": app_settings.has_ai_key,
    }
