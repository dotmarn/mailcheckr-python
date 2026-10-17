"""Synchronous MailCheckr HTTP client using the Python standard library."""

import json
import os
from typing import Any, Dict, Optional
from urllib.error import HTTPError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from .exceptions import MailCheckrError
from .result import VerificationResult


class MailCheckrClient:
    """Verify addresses and retrieve verification results."""

    def __init__(self, api_key: Optional[str] = None,
                 base_url: str = "https://mailcheckr.app/api/v1",
                 timeout: float = 30) -> None:
        parsed = urlsplit(base_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.query or parsed.fragment:
            raise ValueError("base_url must be an HTTP(S) URL without a query or fragment.")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout < float("inf"):
            raise ValueError("timeout must be a positive finite number of seconds.")
        self.api_key = api_key if api_key is not None else os.getenv("MAILCHECKR_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def verify(self, email: str, idempotency_key: str) -> VerificationResult:
        """Start a verification, reusing the key for retries of the same email."""
        if not isinstance(email, str) or not email.strip() or not isinstance(idempotency_key, str) or not idempotency_key.strip():
            raise ValueError("Email and idempotency key are required.")
        return self._request("POST", "verifications", {"email": email}, idempotency_key)

    def find(self, verification_id: str) -> VerificationResult:
        """Fetch a verification by its ID."""
        if (not isinstance(verification_id, str) or not verification_id
                or any(char in verification_id for char in "/?#")):
            raise ValueError("A valid verification ID is required.")
        return self._request("GET", "verifications/" + quote(verification_id, safe=""))

    def _request(self, method: str, path: str, body: Optional[Dict[str, str]] = None,
                 idempotency_key: Optional[str] = None) -> VerificationResult:
        if not isinstance(self.api_key, str) or not self.api_key:
            raise ValueError("Configure MAILCHECKR_API_KEY before making requests.")
        headers = {"Accept": "application/json", "Authorization": "Bearer " + self.api_key}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if idempotency_key is not None:
            headers["Idempotency-Key"] = idempotency_key
        request = Request(self.base_url + "/" + path,
                          data=json.dumps(body).encode("utf-8") if body is not None else None,
                          headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = response.read()
        except HTTPError as error:
            try:
                parsed = json.loads(error.read())
            except (ValueError, UnicodeError):
                parsed = None
            raise MailCheckrError(error.code, parsed if isinstance(parsed, dict) else {}) from error
        try:
            parsed = json.loads(payload)
        except (ValueError, UnicodeError) as error:
            raise ValueError("MailCheckr returned an unexpected response.") from error
        if not isinstance(parsed, dict) or not isinstance(parsed.get("data"), dict):
            raise ValueError("MailCheckr returned an unexpected response.")
        return VerificationResult(parsed["data"])
