def validate_comment_data(data):
    comment = data.get("comment")
    if comment is None:
        return False, "Comment is required"
    if not isinstance(comment, str):
        return False, "Comment must be a string"
    if not (1 <= len(comment) <= 1000):
        return False, "Comment must be between 1 and 1000 characters"
    return True, ""


def validate_vote_type(data, allowed_types):
    vote_type = data.get("vote_type")
    if vote_type is None:
        return False, "Vote type is required"
    if vote_type not in allowed_types:
        return False, f"Invalid vote type. Allowed: {allowed_types}"
    return True, ""


def validate_user_data(data):
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    if not username or not isinstance(username, str) or not (3 <= len(username) <= 32):
        return False, "Username must be a string between 3 and 32 characters"
    if not email or not isinstance(email, str) or "@" not in email:
        return False, "Valid email is required"
    if not password or not isinstance(password, str) or len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, ""


def validate_task_data(data):
    required_fields = ["name", "description", "tags_json", "difficulty", "language", "status"]
    for field in required_fields:
        if field not in data:
            return False, f"{field} is required"
    if not isinstance(data["name"], str) or not (1 <= len(data["name"]) <= 100):
        return False, "Name must be a string between 1 and 100 characters"
    if not isinstance(data["description"], str) or not (1 <= len(data["description"]) <= 2000):
        return False, "Description must be a string between 1 and 2000 characters"
    if not isinstance(data["tags_json"], list):
        return False, "tags_json must be a list of strings"
    if not all(isinstance(tag, str) for tag in data["tags_json"]):
        return False, "Each tag in tags_json must be a string"
    if not isinstance(data["difficulty"], str):
        return False, "Difficulty must be a string"
    if not isinstance(data["language"], str):
        return False, "Language must be a string"
    if not isinstance(data["status"], str):
        return False, "Status must be a string"
    return True, ""


def validate_filter_tasks_data(data):
    if "lab_ids" not in data or "tags_json" not in data:
        return False, "lab_ids and tags_json are required"
    if not isinstance(data["lab_ids"], list):
        return False, "lab_ids must be a list"
    if not isinstance(data["tags_json"], (list, dict)):
        return False, "tags_json must be a list or dict"
    return True, ""


def validate_solution_data(data):
    if "server_problem_id" not in data or "solution" not in data:
        return False, "server_problem_id and solution are required"
    if not isinstance(data["server_problem_id"], int):
        return False, "server_problem_id must be an integer"
    if not isinstance(data["solution"], str) or not data["solution"]:
        return False, "solution must be a non-empty string"
    return True, ""
