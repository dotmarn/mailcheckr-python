import hashlib
import hmac
import io
import json
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from mailcheckr import MailCheckrClient, MailCheckrError, VerificationResult, WebhookVerifier


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


class ClientTests(unittest.TestCase):
    def test_verify_sends_auth_json_and_key_and_accepts_pending(self):
        client = MailCheckrClient(api_key="secret")
        with patch("mailcheckr.client.urlopen", return_value=Response({"data": {"id": "abc", "state": "queued"}})) as send:
            result = client.verify("a@example.com", "key-1")
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "https://mailcheckr.app/api/v1/verifications")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        self.assertEqual(request.get_header("Idempotency-key"), "key-1")
        self.assertEqual(json.loads(request.data), {"email": "a@example.com"})
        self.assertTrue(result.is_pending)
        self.assertFalse(result.is_deliverable)

    def test_find_and_completed_status(self):
        client = MailCheckrClient(api_key="secret", base_url="https://example.com/api/v1/")
        with patch("mailcheckr.client.urlopen", return_value=Response({"data": {"id": "a b", "state": "completed", "status": "deliverable"}})) as send:
            result = client.find("a b")
        self.assertEqual(send.call_args.args[0].full_url, "https://example.com/api/v1/verifications/a%20b")
        self.assertTrue(result.is_deliverable)
        self.assertFalse(result.is_pending)

    def test_api_error_and_malformed_success(self):
        client = MailCheckrClient(api_key="secret")
        error = HTTPError("https://example.com", 409, "Conflict", {}, io.BytesIO(b'{"message":"Conflict"}'))
        with patch("mailcheckr.client.urlopen", side_effect=error), self.assertRaises(MailCheckrError) as raised:
            client.verify("a@example.com", "key")
        self.assertEqual(raised.exception.status, 409)
        self.assertEqual(raised.exception.response["message"], "Conflict")
        with patch("mailcheckr.client.urlopen", return_value=Response({})), self.assertRaisesRegex(ValueError, "unexpected response"):
            client.find("abc")
        with self.assertRaises(ValueError):
            client.find("../abc")
        with self.assertRaises(ValueError):
            VerificationResult({"id": "abc"})

    def test_status_requires_completed_state(self):
        for status in ("deliverable", "undeliverable", "risky", "unknown"):
            result = VerificationResult({"id": "abc", "state": "processing", "status": status})
            self.assertFalse(getattr(result, "is_" + status))


class WebhookTests(unittest.TestCase):
    def test_raw_body_signature_and_timestamp(self):
        body = b'{"id":"event_1"}'
        timestamp = str(int(time.time()))
        signature = "v1=" + hmac.new(b"whsec", timestamp.encode() + b"." + body, hashlib.sha256).hexdigest()
        verifier = WebhookVerifier("whsec")
        self.assertTrue(verifier.verify(body, {"x-mailcheckr-timestamp": timestamp, "X-MailCheckr-Signature": signature}))
        self.assertFalse(verifier.verify_payload(b'{"id":"event_2"}', timestamp, signature))
        self.assertFalse(verifier.verify_payload(body, str(int(timestamp) - 301), signature))
        self.assertFalse(verifier.verify_payload(body, timestamp, "v1=bad"))
        self.assertFalse(WebhookVerifier("wrong").verify_payload(body, timestamp, signature))


if __name__ == "__main__":
    unittest.main()
