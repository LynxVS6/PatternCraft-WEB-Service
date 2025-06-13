from app.extensions import db
from .base_service import BaseService, Result
from app.models import Problem, Solution, User


class SolutionService(BaseService):
    @staticmethod
    def submit_solution(raw_data, current_user) -> Result:
        input_data = {
            "raw_data": raw_data,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            SolutionService._parse_submit_data,
            SolutionService._validate_submit_data,
            SolutionService._handle_submit,
            SolutionService._send_submit_data,
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_submit_data(input_data):
        raw_data = input_data["raw_data"]
        return Result(
            True,
            data={
                "problem_id": raw_data["server_problem_id"],
                "solution": raw_data["solution"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    @BaseService._handle_errors
    def _validate_submit_data(input_data) -> Result:
        if not input_data["current_user"].is_authenticated:
            return Result(
                success=False,
                error="User must be authenticated",
                error_code=401,
            )

        # Validate solution data
        if "server_problem_id" not in input_data or "solution" not in input_data:
            return Result(
                success=False,
                error="server_problem_id and solution are required",
                error_code=400,
            )
        if not isinstance(input_data["server_problem_id"], int):
            return Result(
                success=False, error="server_problem_id must be an integer", error_code=400
            )
        if not isinstance(input_data["solution"], str) or not input_data["solution"]:
            return Result(
                success=False, error="solution must be a non-empty string", error_code=400
            )

        problem = Problem.query.get(input_data["server_problem_id"])
        if not problem:
            return Result(
                success=False,
                error=f"Problem {input_data['server_problem_id']} not found",
                error_code=404,
            )

        input_data["problem"] = problem
        return Result(success=True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _handle_submit(input_data) -> Result:
        current_user = input_data["current_user"]
        problem = input_data["problem"]
        solution = input_data["solution"]

        new_solution = Solution(
            user_id=current_user.id,
            problem_id=problem.id,
            solution=solution,
        )

        db.session.add(new_solution)
        db.session.flush()
        return Result(
            success=True,
            data={
                "solution": new_solution,
                "problem": problem,
                "user": current_user,
            },
        )

    @staticmethod
    def _send_submit_data(input_data) -> Result:
        solution = input_data["solution"]
        problem = input_data["problem"]
        user = input_data["user"]

        return Result(
            success=True,
            data={
                "id": solution.id,
                "solution": solution.solution,
                "user": {
                    "id": user.id,
                    "username": user.username,
                },
                "problem": {
                    "id": problem.id,
                    "name": problem.name,
                    "difficulty": problem.difficulty,
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
