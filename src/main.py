from fastapi import FastAPI

from src.exceptions import AppError
from src.pull_requests.handlers import router as pr_router
from src.stats.handlers import router as stats_router
from src.team.handlers import router as team_router
from src.users.handlers import router as user_router
from src.utils import app_error_handler

app = FastAPI(title="PR Reviewer Assignment Service")

app.include_router(team_router)
app.include_router(user_router)
app.include_router(pr_router)
app.include_router(stats_router)

app.add_exception_handler(AppError, app_error_handler)
