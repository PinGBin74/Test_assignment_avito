from fastapi import APIRouter, Depends, Query

from src.dependencies import get_team_service
from src.team.schema import DeactivateRequest, Team
from src.team.service import TeamService

router = APIRouter(tags=["Teams"])


@router.post("/team/add", status_code=201)
async def add_team(
    body: Team,
    service: TeamService = Depends(get_team_service),
) -> Team:
    team = await service.add_team(body.team_name, body.members)
    return team


@router.post("/team/deactivate")
async def deactivate_team(
    body: DeactivateRequest,
    service: TeamService = Depends(get_team_service),
) -> dict:
    return await service.deactivate_team(body.team_name)


@router.get("/team/get")
async def get_team(
    team_name: str = Query(),
    service: TeamService = Depends(get_team_service),
) -> Team:
    return await service.get_team(team_name)
