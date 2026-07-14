from typing import Any, Protocol


class ProgressExtractor(Protocol):
    def extract_progress(self, text: str) -> dict[str, Any]: ...
