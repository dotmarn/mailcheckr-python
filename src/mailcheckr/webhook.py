"""Webhook signature verification."""

import hashlib
import hmac
import os
import re
import time
from typing import Mapping, Optional, Union


class WebhookVerifier:
    """Verify MailCheckr's v1 HMAC signature over timestamp and raw body."""

    def __init__(self, secret: Optional[str] = None, tolerance: int = 300) -> None:
        if isinstance(tolerance, bool) or not isinstance(tolerance, int) or tolerance < 0:
            raise ValueError("tolerance must be a nonnegative number of seconds.")
        self.secret = secret if secret is not None else os.getenv("MAILCHECKR_WEBHOOK_SECRET")
        self.tolerance = tolerance

    def verify_payload(self, body: Union[bytes, str], timestamp: Optional[str],
                       signature: Optional[str]) -> bool:
        if (not isinstance(self.secret, str) or not self.secret
                or not isinstance(body, (bytes, str))
                or not isinstance(timestamp, str) or not re.fullmatch(r"[0-9]{1,20}", timestamp)
                or not isinstance(signature, str) or not re.fullmatch(r"v1=[a-fA-F0-9]{64}", signature)):
            return False
        if abs(time.time() - int(timestamp)) > self.tolerance:
            return False
        raw_body = body.encode("utf-8") if isinstance(body, str) else body
        signed = timestamp.encode("ascii") + b"." + raw_body
        expected = hmac.new(self.secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature[3:].lower())

    def verify(self, body: Union[bytes, str], headers: Mapping[str, str]) -> bool:
        """Read signature headers case insensitively and verify the exact raw body."""
        normalized = {key.lower(): value for key, value in headers.items()}
        return self.verify_payload(body, normalized.get("x-mailcheckr-timestamp"),
                                   normalized.get("x-mailcheckr-signature"))
