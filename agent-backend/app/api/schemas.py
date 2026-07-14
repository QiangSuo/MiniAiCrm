from typing import Literal

from pydantic import BaseModel, Field, model_validator


class RequestContext(BaseModel):
    customer_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)


class MaterialIntake(RequestContext):
    filename: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ProgressIntake(RequestContext):
    text: str = Field(min_length=1)


class ConfirmProposal(RequestContext):
    pass


class QuestionRequest(RequestContext):
    question: str = Field(min_length=1)


class FeishuReplayEvent(RequestContext):
    event_type: Literal["message.text", "file.received"]
    intent: Literal["progress", "material", "question"]
    text: str | None = None
    filename: str | None = None
    description: str | None = None

    @model_validator(mode="after")
    def validate_event_content(self) -> "FeishuReplayEvent":
        if self.intent in {"progress", "question"} and not self.text:
            raise ValueError("text is required for progress and question events")
        if self.intent == "material" and (not self.filename or not self.description):
            raise ValueError("filename and description are required for material events")
        if self.intent == "material" and self.event_type != "file.received":
            raise ValueError("material intent requires file.received event_type")
        if self.intent != "material" and self.event_type != "message.text":
            raise ValueError("message intents require message.text event_type")
        return self
