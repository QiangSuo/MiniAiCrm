from typing import Any

from app.ports.repository import DemoRepository


class DemoService:
    def __init__(self, repository: DemoRepository):
        self.repository = repository

    def reset(self) -> dict[str, Any]:
        return self.repository.reset_demo()
