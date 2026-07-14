from dataclasses import dataclass

from app.config import Settings
from app.infrastructure.demo_extractor import DemoExtractor
from app.ports.extractor import ProgressExtractor


@dataclass(frozen=True)
class ExtractorSelection:
    name: str
    extractor: ProgressExtractor
    fallback_reason: str | None = None


def select_progress_extractor(settings: Settings) -> ExtractorSelection:
    if not settings.openai_api_key:
        return ExtractorSelection(
            name="demo",
            extractor=DemoExtractor(),
            fallback_reason="OPENAI_API_KEY is not configured",
        )

    return ExtractorSelection(
        name="demo",
        extractor=DemoExtractor(),
        fallback_reason="OpenAI provider is optional P1 and disabled for the P0 demo",
    )
