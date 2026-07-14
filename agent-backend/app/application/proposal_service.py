from typing import Any

from app.application.permission_service import PermissionGuard
from app.domain.errors import PermissionDenied
from app.ports.repository import DemoRepository


class ProposalEngine:
    def __init__(self, repository: DemoRepository, permission_guard: PermissionGuard):
        self.repository = repository
        self.permission_guard = permission_guard

    def confirm(self, proposal_id: str, customer_id: str, user_id: str) -> dict[str, Any]:
        self.permission_guard.require(customer_id, user_id)
        proposal = self.repository.get_proposal(proposal_id)
        if proposal is None or proposal["customer_id"] != customer_id:
            raise PermissionDenied("无权访问该客户")
        return self.repository.confirm_proposal(proposal_id, customer_id, user_id)
