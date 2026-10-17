"""Server-side client for the MailCheckr API."""

from .client import MailCheckrClient
from .exceptions import MailCheckrError
from .result import VerificationResult
from .webhook import WebhookVerifier

__all__ = ["MailCheckrClient", "MailCheckrError", "VerificationResult", "WebhookVerifier"]
