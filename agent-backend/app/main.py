from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import create_api_router
from app.application.dashboard_service import DashboardService
from app.application.demo_service import DemoService
from app.application.intake_service import IntakeService
from app.application.permission_service import PermissionGuard
from app.application.proposal_service import ProposalEngine
from app.application.question_service import QuestionService
from app.config import Settings
from app.domain.errors import ConflictError, NotFound, PermissionDenied
from app.infrastructure.extractor_provider import select_progress_extractor
from app.infrastructure.fake_feishu_gateway import FakeFeishuEventGateway
from app.infrastructure.sqlite_repository import SQLiteDemoRepository
from app.logging import configure_logging

DEMO_PAGE = Path(__file__).resolve().parent / "demo" / "index.html"


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings()
    repository = SQLiteDemoRepository(resolved_settings.database_path)
    permission_guard = PermissionGuard(repository)
    demo_service = DemoService(repository)
    extractor_selection = select_progress_extractor(resolved_settings)
    intake_service = IntakeService(
        repository, permission_guard, extractor_selection.extractor
    )
    proposal_engine = ProposalEngine(repository, permission_guard)
    question_service = QuestionService(repository, permission_guard)
    dashboard_service = DashboardService(repository, permission_guard)
    feishu_gateway = FakeFeishuEventGateway(intake_service, question_service)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        repository.initialize()
        yield

    app = FastAPI(title="XERP Demo", version="0.1.0", lifespan=lifespan)
    app.state.settings = resolved_settings
    app.state.repository = repository
    app.state.extractor_provider = extractor_selection.name
    app.mount(
        "/demo/assets",
        StaticFiles(directory=DEMO_PAGE.parent),
        name="demo-assets",
    )

    @app.exception_handler(PermissionDenied)
    async def permission_denied(_: Request, error: PermissionDenied) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(error)}
        )

    @app.exception_handler(NotFound)
    async def not_found(_: Request, error: NotFound) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(error)}
        )

    @app.exception_handler(ConflictError)
    async def conflict(_: Request, error: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"detail": str(error)}
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "service": resolved_settings.service_name,
            "mode": resolved_settings.app_mode,
            "extractor_provider": extractor_selection.name,
        }

    @app.get("/demo", include_in_schema=False)
    def demo() -> FileResponse:
        return FileResponse(DEMO_PAGE)

    @app.post("/api/demo/reset")
    def reset_demo() -> dict[str, object]:
        return demo_service.reset()

    app.include_router(
        create_api_router(
            repository=repository,
            permission_guard=permission_guard,
            intake_service=intake_service,
            proposal_engine=proposal_engine,
            question_service=question_service,
            dashboard_service=dashboard_service,
            feishu_gateway=feishu_gateway,
        )
    )
    return app


app = create_app()
