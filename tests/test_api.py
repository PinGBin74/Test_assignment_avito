import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/stats")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_and_get_team(client: AsyncClient):
    payload = {
        "team_name": "backend",
        "members": [
            {"user_id": "u1", "username": "Alice", "is_active": True},
            {"user_id": "u2", "username": "Bob", "is_active": True},
        ],
    }
    resp = await client.post("/team/add", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["team_name"] == "backend"
    assert len(data["members"]) == 2

    resp = await client.get("/team/get", params={"team_name": "backend"})
    assert resp.status_code == 200
    assert resp.json()["team_name"] == "backend"


@pytest.mark.asyncio
async def test_create_duplicate_team(client: AsyncClient):
    payload = {
        "team_name": "payments",
        "members": [
            {"user_id": "u3", "username": "Charlie", "is_active": True},
        ],
    }
    resp = await client.post("/team/add", json=payload)
    assert resp.status_code == 201

    resp = await client.post("/team/add", json=payload)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "TEAM_EXISTS"


@pytest.mark.asyncio
async def test_get_nonexistent_team(client: AsyncClient):
    resp = await client.get("/team/get", params={"team_name": "nonexistent"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_set_is_active(client: AsyncClient):
    payload = {
        "team_name": "frontend",
        "members": [
            {"user_id": "u10", "username": "Dave", "is_active": True},
            {"user_id": "u11", "username": "Eve", "is_active": True},
        ],
    }
    await client.post("/team/add", json=payload)

    resp = await client.post(
        "/users/setIsActive", json={"user_id": "u10", "is_active": False}
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_set_is_active_not_found(client: AsyncClient):
    resp = await client.post(
        "/users/setIsActive",
        json={"user_id": "nonexistent", "is_active": False},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_pr(client: AsyncClient):
    team = {
        "team_name": "ml",
        "members": [
            {"user_id": "u20", "username": "Frank", "is_active": True},
            {"user_id": "u21", "username": "Grace", "is_active": True},
            {"user_id": "u22", "username": "Henry", "is_active": True},
        ],
    }
    await client.post("/team/add", json=team)

    resp = await client.post(
        "/pullRequest/create",
        json={
            "pull_request_id": "pr-1",
            "pull_request_name": "Add inference",
            "author_id": "u20",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["pull_request_id"] == "pr-1"
    assert data["status"] == "OPEN"
    assert data["author_id"] == "u20"
    assert len(data["assigned_reviewers"]) == 2
    assert "u20" not in data["assigned_reviewers"]


@pytest.mark.asyncio
async def test_create_duplicate_pr(client: AsyncClient):
    resp = await client.post(
        "/pullRequest/create",
        json={
            "pull_request_id": "pr-1",
            "pull_request_name": "Duplicate",
            "author_id": "u20",
        },
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "PR_EXISTS"


@pytest.mark.asyncio
async def test_merge_pr(client: AsyncClient):
    resp = await client.post(
        "/pullRequest/merge", json={"pull_request_id": "pr-1"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "MERGED"


@pytest.mark.asyncio
async def test_merge_idempotent(client: AsyncClient):
    resp = await client.post(
        "/pullRequest/merge", json={"pull_request_id": "pr-1"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "MERGED"


@pytest.mark.asyncio
async def test_cannot_reassign_merged(client: AsyncClient):
    resp = await client.post(
        "/pullRequest/reassign",
        json={"pull_request_id": "pr-1", "old_user_id": "u21"},
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "PR_MERGED"


@pytest.mark.asyncio
async def test_reassign(client: AsyncClient):
    team = {
        "team_name": "qa",
        "members": [
            {"user_id": "u30", "username": "Iris", "is_active": True},
            {"user_id": "u31", "username": "Jack", "is_active": True},
            {"user_id": "u32", "username": "Kate", "is_active": True},
            {"user_id": "u33", "username": "Leo", "is_active": True},
        ],
    }
    await client.post("/team/add", json=team)

    await client.post(
        "/pullRequest/create",
        json={
            "pull_request_id": "pr-2",
            "pull_request_name": "Fix bugs",
            "author_id": "u30",
        },
    )

    pr = await client.post(
        "/pullRequest/create",
        json={
            "pull_request_id": "pr-3",
            "pull_request_name": "Refactor",
            "author_id": "u30",
        },
    )
    reviewers = pr.json()["assigned_reviewers"]
    old_reviewer = reviewers[0]

    resp = await client.post(
        "/pullRequest/reassign",
        json={"pull_request_id": "pr-3", "old_user_id": old_reviewer},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["pr"]["status"] == "OPEN"
    assert data["replaced_by"] != old_reviewer
    assert len(data["pr"]["assigned_reviewers"]) == 2
    assert data["replaced_by"] in data["pr"]["assigned_reviewers"]


@pytest.mark.asyncio
async def test_reassign_not_assigned(client: AsyncClient):
    resp = await client.post(
        "/pullRequest/reassign",
        json={"pull_request_id": "pr-2", "old_user_id": "u99"},
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "NOT_ASSIGNED"


@pytest.mark.asyncio
async def test_get_review(client: AsyncClient):
    resp = await client.get("/users/getReview", params={"user_id": "u21"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "u21"
    assert isinstance(data["pull_requests"], list)


@pytest.mark.asyncio
async def test_inactive_user_not_assigned(client: AsyncClient):
    team = {
        "team_name": "inactive-team",
        "members": [
            {"user_id": "u40", "username": "Leo", "is_active": True},
            {"user_id": "u41", "username": "Mike", "is_active": False},
            {"user_id": "u42", "username": "Nina", "is_active": True},
        ],
    }
    await client.post("/team/add", json=team)

    resp = await client.post(
        "/pullRequest/create",
        json={
            "pull_request_id": "pr-inactive",
            "pull_request_name": "Test inactive",
            "author_id": "u40",
        },
    )
    assert resp.status_code == 201
    reviewers = resp.json()["assigned_reviewers"]
    assert "u41" not in reviewers


@pytest.mark.asyncio
async def test_stats(client: AsyncClient):
    resp = await client.get("/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "assignments_by_user" in data
    assert "total_prs" in data
    assert "open_prs" in data
    assert "merged_prs" in data


@pytest.mark.asyncio
async def test_deactivate_team(client: AsyncClient):
    team = {
        "team_name": "to-deactivate",
        "members": [
            {"user_id": "u50", "username": "Oscar", "is_active": True},
            {"user_id": "u51", "username": "Paul", "is_active": True},
        ],
    }
    await client.post("/team/add", json=team)

    await client.post(
        "/pullRequest/create",
        json={
            "pull_request_id": "pr-deact",
            "pull_request_name": "To be reassigned",
            "author_id": "u50",
        },
    )

    resp = await client.post(
        "/team/deactivate", json={"team_name": "to-deactivate"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["deactivated"] == 2


@pytest.mark.asyncio
async def test_deactivate_nonexistent_team(client: AsyncClient):
    resp = await client.post(
        "/team/deactivate", json={"team_name": "no-such-team"}
    )
    assert resp.status_code == 404
