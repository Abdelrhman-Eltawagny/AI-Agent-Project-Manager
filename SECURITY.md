# Security Policy

## Reporting a vulnerability

Please do **not** open a public issue for security problems. Use GitHub's **private vulnerability reporting** (Security tab, "Report a vulnerability") for this repository, and include steps to reproduce and the affected version.

## Notes for operators

- The planning pipeline runs against a **local** Ollama server; project documents are not sent to external services by this code.
- The web service (`server.py`) protects `/ask` with a shared API key (`API_KEY`, sent as `x-api-key`). Always set it when the service is reachable from a network, and serve it behind HTTPS (for example a reverse proxy).
- Keep `.env` out of version control (it is git-ignored). Use `.env.example` as the template.
- The assistant answers only from the generated plan; do not place secrets in project documents.
