from .base_service import Result


def validate_user_data(data) -> Result:
    if not data:
        return Result(succes=False, error="No data provided", error_code=400)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not isinstance(username, str) or not (3 <= len(username) <= 32):
        return Result(
            success=False,
            error="Username must be a string between 3 and 32 characters",
            error_code=400,
        )
    if not email or not isinstance(email, str) or "@" not in email:
        return Result(success=False, error="Valid email is required", error_code=400)
    if not password or not isinstance(password, str) or len(password) < 6:
        return Result(
            success=False,
            error="Password must be at least 6 characters",
            error_code=400,
        )
    return Result(success=True)


def validate_task_data(data) -> Result:
    if not data:
        return Result(succes=False, error="No data provided", error_code=400)
    required_fields = [
        "name",
        "description",
        "tags_json",
        "difficulty",
        "language",
        "status",
    ]
    for field in required_fields:
        if field not in data:
            return Result(success=False, error=f"{field} is required", error_code=400)

    if not isinstance(data["name"], str) or not (1 <= len(data["name"]) <= 100):
        return Result(
            success=False,
            error="Name must be a string between 1 and 100 characters",
            error_code=400,
        )
    if not isinstance(data["description"], str) or not (
        1 <= len(data["description"]) <= 2000
    ):
        return Result(
            success=False,
            error="Description must be a string between 1 and 2000 characters",
            error_code=400,
        )
    if not isinstance(data["tags_json"], list):
        return Result(
            success=False, error="tags_json must be a list of strings", error_code=400
        )
    if not all(isinstance(tag, str) for tag in data["tags_json"]):
        return Result(
            success=False,
            error="Each tag in tags_json must be a string",
            error_code=400,
        )
    if not isinstance(data["difficulty"], str):
        return Result(
            success=False, error="Difficulty must be a string", error_code=400
        )
    if not isinstance(data["language"], str):
        return Result(success=False, error="Language must be a string", error_code=400)
    if not isinstance(data["status"], str):
        return Result(success=False, error="Status must be a string", error_code=400)
    return Result(success=True)


def validate_filter_tasks_data(data) -> Result:
    if not data:
        return Result(succes=False, error="No data provided", error_code=400)
    if "lab_ids" not in data or "tags_json" not in data:
        return Result(
            success=False, error="lab_ids and tags_json are required", error_code=400
        )
    if not isinstance(data["lab_ids"], list):
        return Result(success=False, error="lab_ids must be a list", error_code=400)
    if not isinstance(data["tags_json"], (list, dict)):
        return Result(
            success=False, error="tags_json must be a list or dict", error_code=400
        )
    return Result(success=True)


def validate_solution_data(data) -> Result:
    if not data:
        return Result(succes=False, error="No data provided", error_code=400)
    if "server_problem_id" not in data or "solution" not in data:
        return Result(
            success=False,
            error="server_problem_id and solution are required",
            error_code=400,
        )
    if not isinstance(data["server_problem_id"], int):
        return Result(
            success=False, error="server_problem_id must be an integer", error_code=400
        )
    if not isinstance(data["solution"], str) or not data["solution"]:
        return Result(
            success=False, error="solution must be a non-empty string", error_code=400
        )
    return Result(success=True)
