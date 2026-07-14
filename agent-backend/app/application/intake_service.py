from typing import Any
from uuid import uuid4

from app.application.permission_service import PermissionGuard
from app.ports.extractor import ProgressExtractor
from app.ports.repository import DemoRepository


class IntakeService:
    def __init__(
        self,
        repository: DemoRepository,
        permission_guard: PermissionGuard,
        extractor: ProgressExtractor,
    ):
        self.repository = repository
        self.permission_guard = permission_guard
        self.extractor = extractor

    def propose_material(
        self, customer_id: str, user_id: str, filename: str, description: str
    ) -> dict[str, Any]:
        self.permission_guard.require(customer_id, user_id)
        changes = [
            {
                "entity_type": "material",
                "operation": "create",
                "data": {
                    "material_id": f"MAT-{uuid4().hex[:12].upper()}",
                    "filename": filename,
                    "description": description,
                    "submitted_by": user_id,
                    "processing_status": "archived",
                },
            }
        ]
        return self.repository.create_proposal(
            proposal_id=f"PROP-{uuid4().hex[:12].upper()}",
            customer_id=customer_id,
            created_by=user_id,
            proposal_type="material",
            changes=changes,
            conflicts=[],
            missing_fields=[],
            original_input={"filename": filename, "description": description},
        )

    def propose_progress(self, customer_id: str, user_id: str, text: str) -> dict[str, Any]:
        self.permission_guard.require(customer_id, user_id)
        extraction = self.extractor.extract_progress(text)
        conflicts = self.repository.detect_conflicts(customer_id, extraction["changes"])
        return self.repository.create_proposal(
            proposal_id=f"PROP-{uuid4().hex[:12].upper()}",
            customer_id=customer_id,
            created_by=user_id,
            proposal_type="progress",
            changes=extraction["changes"],
            conflicts=conflicts,
            missing_fields=extraction["missing_fields"],
            original_input={"text": text},
        )
