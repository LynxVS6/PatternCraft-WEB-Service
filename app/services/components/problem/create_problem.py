from app.extensions import db
from ...ropp_service import Result
from ...mixins.authentication_mixin import AuthenticationMixin
from app.models import Problem


class CreateProblem(AuthenticationMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]

        # Validate task data
        required_fields = [
            "name",
            "description",
            "difficulty",
            "language",
            "tags",
            "tests",
        ]
        for field in required_fields:
            if field not in raw_json:
                return Result(
                    success=False, error=f"{field} is required", error_code=400
                )

        input_data["status"] = "beta"  # remove when status logic added
        input_data.update(raw_json)

        return Result.ok(
            data={
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    def validate_create_data(input_data) -> Result:
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

        # Handle tags_json - make it optional
        tags_json = input_data.get("tags_json", [])
        if not isinstance(tags_json, str):
            return Result.fail(
                error="tags_json must be a string",
                error_code=400,
            )
        input_data["tags_json"] = tags_json.split(",")
        if not isinstance(input_data["difficulty"], str):
            return Result.fail(error="Difficulty must be a string", error_code=400)
        if not isinstance(input_data["language"], str):
            return Result.fail(error="Language must be a string", error_code=400)

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
            tests=input_data["tests"],
            author_id=current_user.id,
        )

        db.session.add(new_problem)
        db.session.commit()
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
                "tests": problem.tests,
                "author_id": problem.author_id,
                "bookmark_count": problem.bookmark_count,
                "created_at": (
                    problem.created_at.isoformat() if problem.created_at else None
                ),
            },
        )
