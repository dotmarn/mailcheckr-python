# MailCheckr for Python

Server-side Python client for the [MailCheckr API](https://mailcheckr.app/docs). Requires Python 3.9 or newer and has no runtime dependencies.

## Install

```sh
pip install mailcheckr
```

Set `MAILCHECKR_API_KEY` in your server environment. Keep it out of browser code and source control.

## Verify an email

```python
from mailcheckr import MailCheckrClient

client = MailCheckrClient()
result = client.verify("person@example.com", "verify-user-123")

if result.is_pending:
    # Save result.id and poll later, or handle a webhook.
    result = client.find(result.id)

if result.is_deliverable:
    # A completed verification marked this address deliverable.
    pass
```

Use a stable idempotency key for each verification. Reuse it for retries of the same email; using it for another email receives HTTP 409. HTTP 200 and 202 both return `VerificationResult`. Pending states are `queued`, `processing`, and `retry_scheduled`. Completed statuses include `deliverable`, `undeliverable`, `risky`, and `unknown`. Only a completed `deliverable` result passes `is_deliverable`.

`VerificationResult` also exposes `id`, `state`, `status`, `is_completed`, `is_failed`, `is_undeliverable`, `is_risky`, `is_unknown`, and `to_dict()`. `find()` retrieves a result by ID. Do not poll in a tight loop.

The client accepts `api_key`, `base_url` (default `https://mailcheckr.app/api/v1`), and `timeout` in seconds (default 30). Non-success HTTP responses raise `MailCheckrError` with `status` and `response` fields. Network and timeout errors are raised by Python's `urllib`.

## Verify webhooks

Verify the exact raw request body before parsing JSON:

```python
import json
from mailcheckr import WebhookVerifier

verifier = WebhookVerifier()  # Reads MAILCHECKR_WEBHOOK_SECRET

def handle_webhook(raw_body: bytes, headers: dict[str, str]) -> None:
    if not verifier.verify(raw_body, headers):
        raise ValueError("Invalid MailCheckr webhook signature")
    event = json.loads(raw_body)
    # Persist and deduplicate event["id"] before applying effects.
```

`verify_payload(raw_body, timestamp, signature)` is also available. The default timestamp tolerance is 300 seconds and can be changed with `WebhookVerifier(tolerance=...)`. Valid deliveries may be retried, so deduplicate event IDs in persistent storage.

## Development

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python -m pip wheel . --no-deps -w dist
```

## License

MIT. See [LICENSE](LICENSE).
