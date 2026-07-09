# PR Reviewer Assignment Service

Automatically assigns reviewers to pull requests based on team membership and activity.

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy (async)
- Alembic
- Docker
- pytest (testcontainers)

## Getting Started

```bash
cp .env.example .env
docker compose up --build
```

The service will be available at `http://localhost:8080`. Migrations run automatically on startup.

## Local Development

```bash
poetry install

```

## Testing

```bash
poetry install --with test
poetry run pytest -v
```

The test suite uses a temporary PostgreSQL container (testcontainers) and creates tables automatically (via `Base.metadata.create_all`).

## Lint

```bash
make lint
```


## Build

```bash
make run
```
Configured in `pyproject.toml` via ruff.

## API

| Method | Path | Description |
|---|---|---|
| POST | `/team/add` | Create a team with members |
| GET | `/team/get?team_name=` | Get team by name |
| POST | `/team/deactivate` | Deactivate all team members + reassign open PRs |
| POST | `/users/setIsActive` | Set user active/inactive flag |
| GET | `/users/getReview?user_id=` | Get PRs assigned to user as reviewer |
| POST | `/pullRequest/create` | Create PR (auto-assigns reviewers) |
| POST | `/pullRequest/merge` | Merge PR (idempotent) |
| POST | `/pullRequest/reassign` | Reassign a reviewer |
| GET | `/stats` | Assignment statistics |

## Project Structure

```
├── alembic/          – DB migration scripts
├── src/              – Application code
│   ├── infrastructure/ – DB engine, session, Base model
│   ├── team/         – Team management (handlers, service, repository, schema)
│   ├── users/        – User management
│   ├── pull_requests/– PR lifecycle (create, merge, reassign)
│   └── stats/        – Review assignment stats
├── tests/            – Integration test suite
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── .env.example
```

## Key Files

- `handlers.py` – FastAPI route endpoints
- `service.py` – Business logic
- `repository.py` – SQLAlchemy database interactions
- `schema.py` – Pydantic models for request/response validation
- `models.py` – SQLAlchemy ORM models
