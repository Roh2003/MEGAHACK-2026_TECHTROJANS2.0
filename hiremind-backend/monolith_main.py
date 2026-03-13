import importlib.util
import asyncio
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.routing import Mount

from AI_Model.generatesQuestionFromai import generate_gemini_agent_response
from AI_Model.screening_pipeline import build_pipeline_from_env

ROOT_DIR = Path(__file__).resolve().parent
SERVICES_DIR = ROOT_DIR / "services"

# Service folders with unique runtime identifiers.
SERVICE_FOLDERS: list[tuple[str, Path]] = [
    ("auth", SERVICES_DIR / "auth-service"),
    ("job", SERVICES_DIR / "job-service"),
    ("application", SERVICES_DIR / "application-service"),
    ("distribution", SERVICES_DIR / "distribution-service"),
]                                                                       

# These module names are reused across service folders, so we clear them
# before loading the next service to avoid cross-service import collisions.
COLLIDING_MODULE_PREFIXES = (
    "database",
    "models",
    "routes",
    "schemas",
    "services",
    "utils",
)

EXCLUDED_SERVICE_ROUTES = {
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
    "/health",
}


_loaded_services: list[tuple[str, object, FastAPI]] = []
_registered_static_mounts: set[str] = set()


async def _ai_cron_loop(app: FastAPI, interval_seconds: int) -> None:
    while True:
        pipeline = getattr(app.state, "ai_pipeline", None)
        if pipeline is not None:
            summary = await pipeline.run_once()
            app.state.ai_last_summary = summary
            app.state.ai_last_run_at = datetime.utcnow().isoformat()

        await asyncio.sleep(interval_seconds)


def _clear_colliding_modules() -> None:
    for module_name in list(sys.modules.keys()):
        if module_name.startswith(COLLIDING_MODULE_PREFIXES):
            sys.modules.pop(module_name, None)


def _load_service_app(service_key: str, service_dir: Path) -> tuple[object, FastAPI]:
    env_path = service_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)

    _clear_colliding_modules()

    service_dir_str = str(service_dir)
    if service_dir_str in sys.path:
        sys.path.remove(service_dir_str)
    sys.path.insert(0, service_dir_str)

    module_path = service_dir / "main.py"
    spec = importlib.util.spec_from_file_location(f"{service_key}_service_main", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load service main module from: {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    service_app = getattr(module, "app", None)
    if not isinstance(service_app, FastAPI):
        raise RuntimeError(f"No FastAPI app found in: {module_path}")

    return module, service_app


def _register_service_routes(monolith_app: FastAPI, service_app: FastAPI) -> None:
    for route in service_app.routes:
        if isinstance(route, APIRoute):
            if route.path in EXCLUDED_SERVICE_ROUTES:
                continue
            monolith_app.router.routes.append(route)
            continue

        if isinstance(route, Mount) and route.path == "/uploads":
            if route.path not in _registered_static_mounts:
                monolith_app.mount(route.path, route.app, name=route.name)
                _registered_static_mounts.add(route.path)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ai_pipeline = None
    app.state.ai_cron_task = None
    app.state.ai_last_summary = None
    app.state.ai_last_run_at = None

    for service_key, service_module, _ in _loaded_services:
        connect_fn = getattr(service_module, "connect_db", None)
        if connect_fn is not None:
            await connect_fn()
            print(f"[monolith] {service_key}-service database connected")

    ai_pipeline = build_pipeline_from_env(ROOT_DIR)
    if ai_pipeline is None:
        print("[monolith] AI screening cron disabled (OPENAI_API_KEY not set)")
    else:
        interval_seconds = int(os.getenv("AI_CRON_INTERVAL_SECONDS", "3600"))
        app.state.ai_pipeline = ai_pipeline
        app.state.ai_cron_task = asyncio.create_task(_ai_cron_loop(app, interval_seconds))
        print(f"[monolith] AI screening cron started (interval={interval_seconds}s)")

    yield

    ai_task = getattr(app.state, "ai_cron_task", None)
    if ai_task is not None:
        ai_task.cancel()
        try:
            await ai_task
        except asyncio.CancelledError:
            pass

    ai_pipeline = getattr(app.state, "ai_pipeline", None)
    if ai_pipeline is not None:
        await ai_pipeline.close()
        print("[monolith] AI screening pipeline stopped")

    for service_key, service_module, _ in reversed(_loaded_services):
        close_fn = getattr(service_module, "close_db", None)
        if close_fn is not None:
            await close_fn()
            print(f"[monolith] {service_key}-service database disconnected")


app = FastAPI(
    title="HireMind Monolith API",
    description="Single-server monolithic API combining auth, job, application, and distribution domains.",
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

for service_key, service_dir in SERVICE_FOLDERS:
    service_module, service_app = _load_service_app(service_key, service_dir)
    _loaded_services.append((service_key, service_module, service_app))
    _register_service_routes(app, service_app)


class AIInterviewQuestionRequest(BaseModel):
    job_description: dict[str, Any]
    questions_per_level: int = Field(default=5, ge=1)
    model: str | None = None


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "hiremind-monolith",
        "version": "2.0.0",
        "mode": "single-server",
        "domains": [key for key, _ in SERVICE_FOLDERS],
    }


@app.get("/ai-screening/status", tags=["AI Screening"])
async def ai_screening_status():
    pipeline_enabled = getattr(app.state, "ai_pipeline", None) is not None
    return {
        "enabled": pipeline_enabled,
        "interval_seconds": int(os.getenv("AI_CRON_INTERVAL_SECONDS", "3600")),
        "last_run_at": getattr(app.state, "ai_last_run_at", None),
        "last_summary": getattr(app.state, "ai_last_summary", None),
    }


@app.post("/ai-screening/run-now", tags=["AI Screening"])
async def run_ai_screening_now():
    pipeline = getattr(app.state, "ai_pipeline", None)
    if pipeline is None:
        return {
            "success": False,
            "message": "AI screening is disabled. Set OPENAI_API_KEY to enable.",
        }

    summary = await pipeline.run_once()
    app.state.ai_last_summary = summary
    app.state.ai_last_run_at = datetime.utcnow().isoformat()
    return {"success": True, "summary": summary}


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
     