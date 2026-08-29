# Contributing

## Branches

Do not push directly to `main`.

Use:

- `feature/<name>`
- `fix/<name>`
- `refactor/<name>`

Example:

`feature/resume-downloader`

## Commits

Use clear commit messages.

Examples:

- `feat: add excel validation`
- `fix: handle invalid resume url`
- `refactor: simplify candidate schema`

## Pull Requests

Before opening a PR:

- Test your changes locally
- Make sure existing tests pass
- Do not commit `.env`
- Keep changes focused
- Update documentation if required

## Code Ownership

- DATA → `data_pipeline/`
- SQL → `backend/app/db/`
- BACKEND 1 → core FastAPI/application layer
- BACKEND 2 → workflows/integrations
- ME → `ai/`

Ownership means responsibility, not exclusive access.

## Important

If your change affects another team's module or a shared schema,
discuss it with the relevant owner before changing it.