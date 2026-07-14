from typing import Any

from fastapi import APIRouter, Query, status

from app.api.schemas import (
    ConfirmProposal,
    FeishuReplayEvent,
    MaterialIntake,
    ProgressIntake,
    QuestionRequest,
)
from app.application.dashboard_service import DashboardService
from app.application.intake_service import IntakeService
from app.application.permission_service import PermissionGuard
from app.application.proposal_service import ProposalEngine
from app.application.question_service import QuestionService
from app.infrastructure.fake_feishu_gateway import FakeFeishuEventGateway
from app.ports.repository import DemoRepository


def create_api_router(
    *,
    repository: DemoRepository,
    permission_guard: PermissionGuard,
    intake_service: IntakeService,
    proposal_engine: ProposalEngine,
    question_service: QuestionService,
    dashboard_service: DashboardService,
    feishu_gateway: FakeFeishuEventGateway,
) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.post("/intake/material", status_code=status.HTTP_201_CREATED)
    def intake_material(request: MaterialIntake) -> dict[str, Any]:
        return intake_service.propose_material(
            request.customer_id,
            request.user_id,
            request.filename,
            request.description,
        )

    @router.post("/intake/progress", status_code=status.HTTP_201_CREATED)
    def intake_progress(request: ProgressIntake) -> dict[str, Any]:
        return intake_service.propose_progress(
            request.customer_id, request.user_id, request.text
        )

    @router.post("/proposals/{proposal_id}/confirm")
    def confirm_proposal(proposal_id: str, request: ConfirmProposal) -> dict[str, Any]:
        return proposal_engine.confirm(
            proposal_id, request.customer_id, request.user_id
        )

    @router.post("/questions")
    def ask_question(request: QuestionRequest) -> dict[str, Any]:
        return question_service.answer(
            request.customer_id, request.user_id, request.question
        )

    @router.post(
        "/integrations/feishu/replay", status_code=status.HTTP_201_CREATED
    )
    def replay_feishu_event(request: FeishuReplayEvent) -> dict[str, Any]:
        return feishu_gateway.replay(
            customer_id=request.customer_id,
            user_id=request.user_id,
            event_type=request.event_type,
            intent=request.intent,
            text=request.text,
            filename=request.filename,
            description=request.description,
        )

    @router.get("/dashboard")
    def dashboard(customer_id: str, user_id: str) -> dict[str, Any]:
        return dashboard_service.get(customer_id, user_id)

    @router.get("/customers/{customer_id}/snapshot")
    def customer_snapshot(
        customer_id: str, user_id: str = Query(min_length=1)
    ) -> dict[str, Any]:
        permission_guard.require(customer_id, user_id)
        return repository.customer_snapshot(customer_id)

    return router
