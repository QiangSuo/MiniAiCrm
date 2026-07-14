from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.enums import ProposalStatus, ProposalType


@dataclass(frozen=True)
class RequestContext:
    customer_id: str
    user_id: str


@dataclass(frozen=True)
class Customer:
    customer_id: str
    name: str
    owner_user_id: str


@dataclass
class Proposal:
    proposal_id: str
    customer_id: str
    created_by: str
    proposal_type: ProposalType
    status: ProposalStatus
    payload: dict[str, Any]
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    created_at: datetime | None = None
