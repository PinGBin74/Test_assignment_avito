import asyncio
import os
from typing import AsyncIterator, Iterator, List

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db"
)
os.environ.setdefault("DISABLE_SCHEDULERS", "1")

from src.infrastructure.database import get_db_session
from src.infrastructure.models import Base
from src.main import app


@pytest.fixture(scope="session")
def pg_container() -> Iterator[PostgresContainer]:
    with PostgresContainer("postgis/postgis:16-3.4") as container:
        container.start()
        yield container


@pytest.fixture(scope="session")
def database_url(pg_container: PostgresContainer) -> str:
    conn_url = pg_container.get_connection_url()
    if conn_url.startswith("postgresql+psycopg2://"):
        return conn_url.replace(
            "postgresql+psycopg2://",
            "postgresql+asyncpg://",
            1,
        )
    if conn_url.startswith("postgresql://"):
        return conn_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return conn_url


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_engine(database_url: str) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(
        database_url,
        future=True,
        echo=False,
        poolclass=NullPool,
    )
    os.environ["DATABASE_URL"] = database_url
    os.environ["DISABLE_SCHEDULERS"] = "1"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture()
async def session_factory(
    async_engine: AsyncEngine,
) -> AsyncIterator[async_sessionmaker]:
    """
    Return async_sessionmaker, associated with the engine.
    Each test/request will take its own session from it.
    """
    AsyncSessionFactory = async_sessionmaker(
        bind=async_engine, expire_on_commit=False, autoflush=False
    )
    yield AsyncSessionFactory


@pytest.fixture()
async def db_session(
    session_factory: async_sessionmaker,
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


async def _get_table_list(engine: AsyncEngine) -> List[str]:
    query = (
        "SELECT table_name "
        "FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type='BASE TABLE';"
    )
    async with engine.connect() as conn:
        res = await conn.execute(text(query))
        rows = res.fetchall()
    return [r[0] for r in rows]


@pytest.fixture(autouse=True, scope="session")
async def flush_db_between_tests(async_engine: AsyncEngine):
    """
    Before each test, we ensure a clean DB:
    TRUNCATE all tables in public CASCADE;
    """
    tables = await _get_table_list(async_engine)
    if tables:
        async with async_engine.begin() as conn:
            names = ", ".join(f'"{t}"' for t in tables)
            await conn.execute(text(f"TRUNCATE {names} CASCADE;"))
    yield
    tables = await _get_table_list(async_engine)
    if tables:
        async with async_engine.begin() as conn:
            names = ", ".join(f'"{t}"' for t in tables)
            await conn.execute(text(f"TRUNCATE {names} CASCADE;"))


@pytest.fixture(autouse=True)
def override_db_dependency(session_factory: async_sessionmaker):
    """
    Override get_db_session so that each request of the application
    received its own AsyncSession created from session_factory.
    """

    async def _override():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db_session] = _override
    yield
    app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture()
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as c:
        yield c
