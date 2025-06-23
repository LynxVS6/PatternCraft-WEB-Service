from app.extensions import db
from ...ropp_service import Result
from ...mixins.authentication_mixin import AuthenticationMixin
from app.models import Solution


class SubmitSolution(AuthenticationMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        input_data["target_id"] = raw_json["server_problem_id"]
        input_data.update(raw_json)
        return Result.ok(input_data)

    @staticmethod
    def validate_solution_data(input_data) -> Result:
        # Validate solution data
        if "solution" not in input_data:
            return Result.fail(
                error="server_problem_id and solution are required",
                error_code=400,
            )
        if not isinstance(input_data["solution"], str) or not input_data["solution"]:
            return Result.fail(
                error="solution must be a non-empty string", error_code=400
            )
        return Result.ok(data=input_data)

    @staticmethod
    def execute(input_data) -> Result:
        current_user = input_data["current_user"]
        target = input_data["target"]
        solution = input_data["solution"]

        # Check if solution already exists for this user and problem
        existing_solution = Solution.query.filter_by(
            user_id=current_user.id,
            problem_id=target.id,
            solution=solution
        ).first()

        if existing_solution:
            return Result.fail(
                error="Такое решение уже существует",
                error_code=409
            )

        new_solution = Solution(
            user_id=current_user.id,
            problem_id=target.id,
            solution=solution,
        )

        db.session.add(new_solution)
        db.session.commit()
        print("-"*50)
        return Result.ok(
            data={
                "solution": new_solution,
                "target": target,
                "current_user": current_user,
            },
        )

    @staticmethod
    def format(input_data) -> Result:
        solution = input_data["solution"]
        target = input_data["target"]
        current_user = input_data["current_user"]
        return Result.ok(
            data={
                "id": solution.id,
                "solution": solution.solution,
                "user_id": current_user.id,
                "problem": {
                    "id": target.id,
                    "name": target.name,
                    "difficulty": target.difficulty,
                },
                "likes_count": solution.votes_count,
                "comments": [],
                "created_at": (
                    solution.created_at.isoformat()
                    if hasattr(solution, "created_at")
                    else None
                ),
            },
        )
