from pydantic import BaseModel


class StatsResponse(BaseModel):
    assignments_by_user: dict[str, int]
    total_prs: int
    open_prs: int
    merged_prs: int
