from typing import Any

from app.application.intake_service import IntakeService
from app.application.question_service import QuestionService


class FakeFeishuEventGateway:
    def __init__(self, intake_service: IntakeService, question_service: QuestionService):
        self._intake_service = intake_service
        self._question_service = question_service

    def replay(
        self,
        *,
        customer_id: str,
        user_id: str,
        event_type: str,
        intent: str,
        text: str | None = None,
        filename: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        if intent == "progress":
            result = self._intake_service.propose_progress(customer_id, user_id, text or "")
        elif intent == "material":
            result = self._intake_service.propose_material(
                customer_id,
                user_id,
                filename or "",
                description or "",
            )
        else:
            result = self._question_service.answer(customer_id, user_id, text or "")

        return {
            "adapter": "fake-feishu",
            "event_type": event_type,
            "intent": intent,
            "result": result,
        }
