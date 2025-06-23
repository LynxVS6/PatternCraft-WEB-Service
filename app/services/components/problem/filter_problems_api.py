from ...ropp_service import Result
from app.models import Problem, Solution
from ...mixins.authentication_mixin import AuthenticationMixin
from sqlalchemy import select, cast, String
import json


class FilterProblemsAPI(AuthenticationMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        input_data.update(raw_json)
        return Result.ok(input_data)

    @staticmethod
    def validate_filter_data(input_data) -> Result:
        # Validate filter data
        if "lab_ids" not in input_data or "tags_json" not in input_data:
            return Result.fail(
                error="lab_ids and tags_json are required",
                error_code=400,
            )
        if not isinstance(input_data["lab_ids"], list):
            return Result.fail(error="lab_ids must be a list", error_code=400)
        if not isinstance(input_data["tags_json"], (list, dict)):
            return Result.fail( error="tags_json must be a list or dict", error_code=400
            )

        return Result.ok(input_data)

    @staticmethod
    def execute(input_data) -> Result:
        query = Problem.query
        query = query.filter(Problem.is_hidden == False)
        lab_ids = input_data["lab_ids"]
        tags_json = input_data["tags_json"]
        current_user = input_data["current_user"]

        if tags_json:
            tags_str = json.dumps(tags_json)
            query = query.filter(cast(Problem.tags_json, String) == tags_str)

        if lab_ids:
            query = query.filter(~Problem.id.in_(lab_ids))

        if current_user.is_authenticated:
            problem_hub = select(Solution.problem_id).where(
                Solution.user_id == current_user.id
            )
            query = query.filter(~Problem.id.in_(problem_hub))

        problems = query.all()
        return Result.ok({"problems": problems})

    @staticmethod
    def format(input_data) -> Result:
        problems = input_data["problems"]
        return Result.ok(
            data={
                "problems": [
                    {
                        "id": problem.id,
                        "name": problem.name,
                        "description": problem.description,
                        "tags_json": problem.tags_json,
                        "difficulty": problem.difficulty,
                        "language": problem.language,
                        "status": problem.status,
                        "author_id": problem.author_id,
                        "bookmark_count": problem.bookmark_count,
                        "positive_vote": problem.positive_vote,
                        "negative_vote": problem.negative_vote,
                        "neutral_vote": problem.neutral_vote,
                        "total_votes": problem.total_votes,
                        "satisfaction_percent": problem.satisfaction_percent,
                        "created_at": (
                            problem.created_at.isoformat()
                            if problem.created_at
                            else None
                        ),
                    }
                    for problem in problems
                ]
            },
        )
