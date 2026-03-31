import asyncio
import importlib
import os
import sys
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from AI_Model.generatesQuestionFromai import generate_gemini_agent_response
# from AI_Model.screening_pipeline import build_pipeline_from_env

ROOT_DIR = Path(__file__).resolve().parent
SERVICES_DIR = ROOT_DIR / "services"

load_dotenv(str(ROOT_DIR / ".env"), override=False)


@dataclass(slots=True)
class LoadedService:
    key: str
    connect_db: Callable[[], Awaitable[None]] | None
    close_db: Callable[[], Awaitable[None]] | None


_loaded_services: list[LoadedService] = []
_registered_static_mounts: set[str] = set()


def _clear_colliding_modules() -> None:
    for module_name in list(sys.modules.keys()):
        if module_name.startswith(("database", "models", "routes", "schemas", "services", "utils")):
            sys.modules.pop(module_name, None)


@contextmanager
def _service_import_context(service_dir: Path):
    service_dir_str = str(service_dir)
    load_dotenv(str(service_dir / ".env"), override=False)
    _clear_colliding_modules()

    inserted_path = service_dir_str not in sys.path
    if inserted_path:
        sys.path.insert(0, service_dir_str)

    try:
        yield
    finally:
        if inserted_path:
            sys.path.remove(service_dir_str)


def _load_service_bundle(
    monolith_app: FastAPI,
    *,
    service_key: str,
    service_dir: Path,
    route_modules: tuple[str, ...],
    database_module: str | None = None,
    mount_uploads: bool = False,
) -> LoadedService:
    with _service_import_context(service_dir):
        db_module = importlib.import_module(database_module) if database_module else None

        for module_name in route_modules:
            route_module = importlib.import_module(module_name)
            router = getattr(route_module, "router", None)
            if router is None:
                raise RuntimeError(f"No APIRouter named 'router' found in {module_name}")
            monolith_app.include_router(router)

        if mount_uploads:
            uploads_dir = service_dir / "uploads"
            if uploads_dir.exists() and "/uploads" not in _registered_static_mounts:
                monolith_app.mount(
                    "/uploads",
                    StaticFiles(directory=str(uploads_dir)),
                    name="uploads",
                )
                _registered_static_mounts.add("/uploads")

    return LoadedService(
        key=service_key,
        connect_db=getattr(db_module, "connect_db", None) if db_module else None,
        close_db=getattr(db_module, "close_db", None) if db_module else None,
    )


def _load_distribution_service_module() -> Any:
    with _service_import_context(SERVICES_DIR / "distribution-service"):
        return importlib.import_module("services.distribution_service")


distribution_service_module = _load_distribution_service_module()


# async def _ai_cron_loop(app: FastAPI, interval_seconds: int) -> None:
#     while True:
#         pipeline = getattr(app.state, "ai_pipeline", None)
#         if pipeline is not None:
#             summary = await pipeline.run_once()
#             app.state.ai_last_summary = summary
#             app.state.ai_last_run_at = datetime.utcnow().isoformat()
#
#         await asyncio.sleep(interval_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # AI screening pipeline temporarily disabled.
    # app.state.ai_pipeline = None
    # app.state.ai_cron_task = None
    # app.state.ai_last_summary = None
    # app.state.ai_last_run_at = None

    for service in _loaded_services:
        connect_fn = service.connect_db
        if connect_fn is not None:
            await connect_fn()
            print(f"[monolith] {service.key}-service database connected")

    # AI screening pipeline startup temporarily disabled.
    # ai_pipeline = build_pipeline_from_env(ROOT_DIR)
    # if ai_pipeline is None:
    #     print("[monolith] AI screening cron disabled (OPENAI_API_KEY not set)")
    # else:
    #     interval_seconds = int(os.getenv("AI_CRON_INTERVAL_SECONDS", "3600"))
    #     app.state.ai_pipeline = ai_pipeline
    #     app.state.ai_cron_task = asyncio.create_task(_ai_cron_loop(app, interval_seconds))
    #     print(f"[monolith] AI screening cron started (interval={interval_seconds}s)")

    yield

    # ai_task = getattr(app.state, "ai_cron_task", None)
    # if ai_task is not None:
    #     ai_task.cancel()
    #     try:
    #         await ai_task
    #     except asyncio.CancelledError:
    #         pass

    # ai_pipeline = getattr(app.state, "ai_pipeline", None)
    # if ai_pipeline is not None:
    #     await ai_pipeline.close()
    #     print("[monolith] AI screening pipeline stopped")

    for service in reversed(_loaded_services):
        close_fn = service.close_db
        if close_fn is not None:
            await close_fn()
            print(f"[monolith] {service.key}-service database disconnected")


app = FastAPI(
    title="HireMind Monolith API",
    description="Single-server monolithic API combining auth, job, application, distribution, and AI workflows.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_loaded_services.extend(
    [
        _load_service_bundle(
            app,
            service_key="auth",
            service_dir=SERVICES_DIR / "auth-service",
            route_modules=("routes.auth", "routes.organization"),
            database_module="database",
        ),
        _load_service_bundle(
            app,
            service_key="job",
            service_dir=SERVICES_DIR / "job-service",
            route_modules=("routes.jobs", "routes.job_post"),
            database_module="database",
        ),
        _load_service_bundle(
            app,
            service_key="application",
            service_dir=SERVICES_DIR / "application-service",
            route_modules=("routes.applications", "routes.job_application"),
            database_module="database",
            mount_uploads=True,
        ),
    ]
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "hiremind-monolith",
        "version": "2.0.0",
        "mode": "single-server",
        "domains": ["auth", "job", "application", "distribution"],
    }


# @app.get("/ai-screening/status", tags=["AI Screening"])
# async def ai_screening_status():
#     pipeline_enabled = getattr(app.state, "ai_pipeline", None) is not None
#     return {
#         "enabled": pipeline_enabled,
#         "interval_seconds": int(os.getenv("AI_CRON_INTERVAL_SECONDS", "3600")),
#         "last_run_at": getattr(app.state, "ai_last_run_at", None),
#         "last_summary": getattr(app.state, "ai_last_summary", None),
#     }


# @app.post("/ai-screening/run-now", tags=["AI Screening"])
# async def run_ai_screening_now():
#     pipeline = getattr(app.state, "ai_pipeline", None)
#     if pipeline is None:
#         return {
#             "success": False,
#             "message": "AI screening is disabled. Set OPENAI_API_KEY to enable.",
#         }

#     summary = await pipeline.run_once()
#     app.state.ai_last_summary = summary
#     app.state.ai_last_run_at = datetime.utcnow().isoformat()
#     return {"success": True, "summary": summary}


@app.post("/distribute-job/{jobid}", tags=["Distribution"])
async def distribute_job_to_platforms(jobid: str):
    """
    Generate share links for a job on LinkedIn, Twitter/X, and WhatsApp.
    No authentication required — links are public by design.
    """
    return await distribution_service_module.distribute_job(jobid)


class AIInterviewQuestionRequest(BaseModel):
    job_description: dict[str, Any]
    questions_per_level: int = Field(default=5, ge=1)
    model: str | None = None


@app.post("/ai-interview/questions", tags=["AI Interview"])
async def generate_ai_interview_questions(payload: AIInterviewQuestionRequest):
    effective_questions_per_level = max(5, payload.questions_per_level)

    try:
        result = generate_gemini_agent_response(
            job_description=payload.job_description,
            questions_per_level=effective_questions_per_level,
            model=payload.model or "gemini-1.5-flash",
        )
    except Exception as exc:
        return {
            "success": False,
            "message": f"Failed to generate interview questions: {exc}",
        }

    return {
        "success": True,
        "questions_per_level": effective_questions_per_level,
        "data": result,
    }
