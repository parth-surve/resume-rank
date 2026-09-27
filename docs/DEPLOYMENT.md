# Deployment preparation

ResumeRank currently has no container or deployment manifests. The backend
expects PostgreSQL and environment-provided configuration; deployment must be
configured for the hosting platform and database chosen by the project team.

## Required settings

- `DATABASE_URL`: SQLAlchemy PostgreSQL connection URL.
- `SECRET_KEY`: high-entropy private signing key for JWTs; do not commit it.
- `ALGORITHM`: JWT algorithm, default `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: token lifetime, default 480.
- `GROQ_API_KEY`, `GEMINI_API_KEY`: set only for the providers in use.
- `GROQ_MODEL`, `GEMINI_MODEL`, `OLLAMA_MODEL`, `OLLAMA_URL`: optional provider
  configuration; defaults are defined in `ai/providers.py`.

The existing settings loader reads `backend/app/.env` for local development.
Production should inject secrets through the platform's secret manager and
must not package a developer `.env` file. Keep `APP_ENV` and `LOG_LEVEL`
consistent with platform conventions; they are documented in `.env.example`
but are not currently consumed by backend settings.

## Before a production release

1. Provide a dependency manifest and pinned, reviewed runtime dependencies.
2. Configure a production PostgreSQL instance, backups, TLS, and connection
   limits; apply Alembic migrations as a release step.
3. Run the API behind a production ASGI server and TLS-terminating proxy.
4. Set trusted origins, ingress limits, health checks, and secret rotation in
   the selected hosting environment. CORS and deployment health checks are not
   currently configured by the application.
5. Verify the provider credentials and model access from the deployment
   environment without printing secret values.
6. Restrict `/metrics` to trusted monitoring networks at the ingress layer.

No deployment has been performed and no benchmark measurements are included
in this repository.
