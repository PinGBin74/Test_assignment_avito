from dataclasses import dataclass


@dataclass
class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code


class TeamExistsError(AppError):
    def __init__(self, team_name: str):
        super().__init__(
            "TEAM_EXISTS", f"team '{team_name}' already exists", 400
        )


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            "NOT_FOUND", f"{resource} '{identifier}' not found", 404
        )


class PRExistsError(AppError):
    def __init__(self, pr_id: str):
        super().__init__("PR_EXISTS", f"PR '{pr_id}' already exists", 409)


class PRMergedError(AppError):
    def __init__(self, pr_id: str):
        super().__init__(
            "PR_MERGED", f"cannot modify merged PR '{pr_id}'", 409
        )


class NotAssignedError(AppError):
    def __init__(self, user_id: str, pr_id: str):
        super().__init__(
            "NOT_ASSIGNED",
            f"user '{user_id}' is not assigned to PR '{pr_id}'",
            409,
        )


class NoCandidateError(AppError):
    def __init__(self, team_name: str):
        super().__init__(
            "NO_CANDIDATE",
            f"no active replacement candidate in team '{team_name}'",
            409,
        )
