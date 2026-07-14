from enum import StrEnum


class ProposalStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class ProposalType(StrEnum):
    MATERIAL = "material"
    PROGRESS = "progress"


class EvidenceConfidence(StrEnum):
    CONFIRMED = "confirmed"
    SINGLE_SOURCE = "single_source"
    INFERRED = "inferred"
