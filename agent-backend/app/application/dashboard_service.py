from typing import Any

from app.application.permission_service import PermissionGuard
from app.ports.repository import DemoRepository


class DashboardService:
    def __init__(self, repository: DemoRepository, permission_guard: PermissionGuard):
        self.repository = repository
        self.permission_guard = permission_guard

    def get(self, customer_id: str, user_id: str) -> dict[str, Any]:
        self.permission_guard.require(customer_id, user_id)
        return self.repository.dashboard(customer_id)
