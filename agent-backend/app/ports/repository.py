from typing import Any, Protocol


class DemoRepository(Protocol):
    def initialize(self) -> None: ...

    def reset_demo(self) -> dict[str, Any]: ...

    def customer_exists(self, customer_id: str) -> bool: ...

    def user_can_access(self, customer_id: str, user_id: str) -> bool: ...

    def create_proposal(
        self,
        *,
        proposal_id: str,
        customer_id: str,
        created_by: str,
        proposal_type: str,
        changes: list[dict[str, Any]],
        conflicts: list[dict[str, Any]],
        missing_fields: list[str],
        original_input: dict[str, Any],
    ) -> dict[str, Any]: ...

    def get_proposal(self, proposal_id: str) -> dict[str, Any] | None: ...

    def detect_conflicts(
        self, customer_id: str, changes: list[dict[str, Any]]
    ) -> list[dict[str, Any]]: ...

    def confirm_proposal(
        self, proposal_id: str, customer_id: str, user_id: str
    ) -> dict[str, Any]: ...

    def customer_snapshot(self, customer_id: str) -> dict[str, Any]: ...

    def dashboard(self, customer_id: str) -> dict[str, Any]: ...
