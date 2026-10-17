# Contributing to MailCheckr for Python

Bug reports, documentation fixes, tests, and code changes are welcome. Search existing issues and pull requests before opening a new one. For a change to the public API or verification behavior, open an issue first so the proposed contract can be discussed.

## Set up locally

Use Python 3.9 or newer. From the repository root:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

On Windows, activate the environment with `.venv\Scripts\activate` instead. The package has no runtime dependencies. To check that it can be packaged, run `python -m pip wheel . --no-deps -w dist`.

## Make a change

- Keep pull requests focused and explain the behavior changed, why it changed, and how you tested it.
- Add or update tests for behavior changes. Mock HTTP calls and use fixed webhook payloads; tests should not need an API key, network access, or a MailCheckr account.
- Preserve the API contract: `verify()` sends an idempotency key, HTTP 202 can be pending, and only a completed `deliverable` result is deliverable.
- Verify webhook signatures against the exact raw request body. Do not parse and reserialize it before verification.
- Keep support for every Python version in the CI matrix, and update the README when public behavior changes.

Never commit API keys, webhook secrets, or customer email addresses. Report suspected vulnerabilities using [SECURITY.md](SECURITY.md), not a public issue.

Contributions are made under this repository's [MIT License](LICENSE).
