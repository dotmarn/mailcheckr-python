"""MailCheckr API errors."""

from typing import Any, Dict


class MailCheckrError(Exception):
    """An unsuccessful HTTP response from MailCheckr."""

    def __init__(self, status: int, response: Dict[str, Any]) -> None:
        self.status = status
        self.response = response
        message = response.get("message") or response.get("code") or "MailCheckr request failed."
        super().__init__(str(message))
