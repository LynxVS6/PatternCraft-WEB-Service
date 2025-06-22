from app.extensions import db
from ...ropp_service import Result
from ...mixins.authentication_mixin import AuthenticationMixin
from app.models import Problem


class CreateProblem(AuthenticationMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        return Result.ok(
            data={
                "name": raw_json["name"],
                "description": raw_json["description"],
                "tags_json": raw_json["tags_json"],
                "difficulty": raw_json["difficulty"],
                "language": raw_json["language"],
                "status": raw_json["status"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    def validate_create_data(input_data) -> Result:
        # Validate task data
        required_fields = [
            "name",
            "description",
            "tags_json",
            "difficulty",
            "language",
            "status",
        ]
        for field in required_fields:
            if field not in input_data:
                return Result(
                    success=False, error=f"{field} is required", error_code=400
                )

        if not isinstance(input_data["name"], str) or not (
            1 <= len(input_data["name"]) <= 100
        ):
            return Result.fail(
                error="Name must be a string between 1 and 100 characters",
                error_code=400,
            )
        if not isinstance(input_data["description"], str) or not (
            1 <= len(input_data["description"]) <= 2000
        ):
            return Result.fail(
                error="Description must be a string between 1 and 2000 characters",
                error_code=400,
            )
        if not isinstance(input_data["tags_json"], list):
            return Result.fail(
                error="tags_json must be a list of strings",
                error_code=400,
            )
        if not all(isinstance(tag, str) for tag in input_data["tags_json"]):
            return Result.fail(
                error="Each tag in tags_json must be a string",
                error_code=400,
            )
        if not isinstance(input_data["difficulty"], str):
            return Result.fail(error="Difficulty must be a string", error_code=400)
        if not isinstance(input_data["language"], str):
            return Result.fail(error="Language must be a string", error_code=400)
        if not isinstance(input_data["status"], str):
            return Result.fail(error="Status must be a string", error_code=400)

        return Result.ok(input_data)

    @staticmethod
    def execute(input_data) -> Result:
        current_user = input_data["current_user"]
        new_problem = Problem(
            name=input_data["name"],
            description=input_data["description"],
            tags_json=input_data["tags_json"],
            difficulty=input_data["difficulty"],
            language=input_data["language"],
            status=input_data["status"],
            author_id=current_user.id,
        )

        db.session.add(new_problem)
        db.session.flush()
        return Result.ok({"problem": new_problem})

    @staticmethod
    def format(input_data) -> Result:
        problem = input_data["problem"]
        return Result.ok(
            data={
                "id": problem.id,
                "name": problem.name,
                "description": problem.description,
                "tags_json": problem.tags_json,
                "difficulty": problem.difficulty,
                "language": problem.language,
                "status": problem.status,
                "author_id": problem.author_id,
                "bookmark_count": problem.bookmark_count,
                "created_at": (
                    problem.created_at.isoformat() if problem.created_at else None
                ),
            },
        )
