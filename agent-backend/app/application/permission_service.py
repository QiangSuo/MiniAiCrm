from app.domain.errors import PermissionDenied
from app.ports.repository import DemoRepository


class PermissionGuard:
    def __init__(self, repository: DemoRepository):
        self.repository = repository

    def require(self, customer_id: str, user_id: str) -> None:
        if not self.repository.user_can_access(customer_id, user_id):
            raise PermissionDenied("无权访问该客户")
