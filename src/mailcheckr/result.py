"""Verification result model."""

from typing import Any, Dict, Optional


class VerificationResult:
    """A verification returned by the API, including pending results."""

    def __init__(self, data: Dict[str, Any]) -> None:
        if (not isinstance(data, dict) or not isinstance(data.get("id"), str)
                or not data["id"] or not isinstance(data.get("state"), str)
                or not data["state"]):
            raise ValueError("A verification result requires an ID and state.")
        self._data = data.copy()

    @property
    def id(self) -> str:
        return self._data["id"]

    @property
    def state(self) -> str:
        return self._data["state"]

    @property
    def status(self) -> Optional[str]:
        value = self._data.get("status")
        return value if isinstance(value, str) else None

    @property
    def is_completed(self) -> bool:
        return self.state == "completed"

    @property
    def is_pending(self) -> bool:
        return self.state in ("queued", "processing", "retry_scheduled")

    @property
    def is_failed(self) -> bool:
        return self.state == "failed"

    @property
    def is_deliverable(self) -> bool:
        return self.is_completed and self.status == "deliverable"

    @property
    def is_undeliverable(self) -> bool:
        return self.is_completed and self.status == "undeliverable"

    @property
    def is_risky(self) -> bool:
        return self.is_completed and self.status == "risky"

    @property
    def is_unknown(self) -> bool:
        return self.is_completed and self.status == "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Return a shallow copy of the original API data."""
        return self._data.copy()
