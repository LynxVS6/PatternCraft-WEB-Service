from app.extensions import db
from .base_service import BaseService, Result
from app.models import Problem, Solution, User
from sqlalchemy import select, cast, String, func, desc, asc, and_
import json


class ProblemService(BaseService):
    @staticmethod
    def filter_problems_api(raw_data, current_user) -> Result:
        """API endpoint for backend filtering (used by AJAX requests)"""
        input_data = {
            "raw_data": raw_data,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            ProblemService._parse_filter_data,
            ProblemService._validate_filter_data,
            ProblemService._handle_filter,
            ProblemService._send_filter_data,
        )

    @staticmethod
    def filter_problems_frontend(
        search_query,
        order_by,
        language,
        status,
        progress,
        difficulties,
        selected_tags,
        page,
        per_page,
        current_user,
    ) -> Result:
        """Frontend filtering for problem hub page"""
        input_data = {
            "search_query": search_query,
            "order_by": order_by,
            "language": language,
            "status": status,
            "progress": progress,
            "difficulties": difficulties,
            "selected_tags": selected_tags,
            "page": page,
            "per_page": per_page,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            ProblemService._parse_frontend_filter_data,
            ProblemService._validate_frontend_filter_data,
            ProblemService._handle_frontend_filter,
            ProblemService._send_frontend_filter_data,
        )

    @staticmethod
    def create_problem(raw_data, current_user) -> Result:
        input_data = {
            "raw_data": raw_data,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            ProblemService._parse_create_data,
            ProblemService._validate_create_data,
            ProblemService._handle_create,
            ProblemService._send_create_data,
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_filter_data(input_data):
        raw_data = input_data["raw_data"]
        return Result(
            True,
            data={
                "lab_ids": raw_data.get("lab_ids", []),
                "tags_json": raw_data.get("tags_json", {}),
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_frontend_filter_data(input_data):
        return Result(True, data=input_data)

    @staticmethod
    @BaseService._parse_errors
    def _parse_create_data(input_data):
        raw_data = input_data["raw_data"]
        return Result(
            True,
            data={
                "name": raw_data["name"],
                "description": raw_data["description"],
                "tags_json": raw_data["tags_json"],
                "difficulty": raw_data["difficulty"],
                "language": raw_data["language"],
                "status": raw_data["status"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    @BaseService._handle_errors
    def _validate_filter_data(input_data) -> Result:
        if not input_data["current_user"].is_authenticated:
            return Result(
                success=False,
                error="User must be authenticated",
                error_code=401,
            )

        # Validate filter data
        if "lab_ids" not in input_data or "tags_json" not in input_data:
            return Result(
                success=False, error="lab_ids and tags_json are required", error_code=400
            )
        if not isinstance(input_data["lab_ids"], list):
            return Result(success=False, error="lab_ids must be a list", error_code=400)
        if not isinstance(input_data["tags_json"], (list, dict)):
            return Result(
                success=False, error="tags_json must be a list or dict", error_code=400
            )

        return Result(success=True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _validate_frontend_filter_data(input_data) -> Result:
        if not input_data["current_user"].is_authenticated:
            return Result(
                success=False,
                error="User must be authenticated",
                error_code=401,
            )
        return Result(success=True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _handle_filter(input_data) -> Result:
        query = Problem.query
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
        return Result(success=True, data={"problems": problems})

    @staticmethod
    @BaseService._handle_errors
    def _handle_frontend_filter(input_data) -> Result:
        query = (
            Problem.query.join(User, Problem.author_id == User.id)
            .add_columns(
                Problem.id,
                Problem.name,
                Problem.description,
                Problem.difficulty,
                Problem.author_id,
                Problem.bookmark_count,
                Problem.created_at,
                Problem.tags_json,
                Problem.language,
                func.count(Solution.id).label("completed_count"),
                (
                    Problem.positive_vote + Problem.negative_vote + Problem.neutral_vote
                ).label("total_votes"),
                func.round(
                    func.coalesce(
                        (Problem.positive_vote * 100.0)
                        / func.nullif(
                            Problem.positive_vote
                            + Problem.negative_vote
                            + Problem.neutral_vote,
                            0,
                        ),
                        0,
                    )
                ).label("satisfaction_percent"),
            )
            .outerjoin(Solution, Problem.id == Solution.problem_id)
            .group_by(
                Problem.id,
                Problem.name,
                Problem.description,
                Problem.difficulty,
                Problem.author_id,
                Problem.bookmark_count,
                Problem.created_at,
                Problem.language,
                Problem.tags_json,
                Problem.positive_vote,
                Problem.negative_vote,
                Problem.neutral_vote,
            )
        )

        # Apply filters
        if input_data["selected_tags"]:
            tag_conditions = []
            for tag in input_data["selected_tags"]:
                condition = func.json_contains(Problem.tags_json, f'"{tag}"')
                tag_conditions.append(condition)
            query = query.filter(and_(*tag_conditions))

        if input_data["search_query"]:
            query = query.filter(
                (Problem.name.ilike(f"%{input_data['search_query']}%"))
                | (Problem.description.ilike(f"%{input_data['search_query']}%"))
            )

        if input_data["language"] and input_data["language"] != "all":
            if input_data["language"] == "my-languages":
                user_languages = input_data["current_user"].preferred_languages or []
                if user_languages:
                    query = query.filter(Problem.language.in_(user_languages))
            else:
                query = query.filter(Problem.language == input_data["language"])

        if input_data["status"] != "all":
            query = query.filter(Problem.status == input_data["status"])

        if input_data["progress"] != "all":
            completed_problems = (
                db.session.query(Problem.id)
                .join(
                    Solution,
                    (Solution.problem_id == Problem.id)
                    & (Solution.user_id == input_data["current_user"].id),
                )
                .subquery()
            )

            if input_data["progress"] == "completed":
                query = query.filter(Problem.id.in_(completed_problems))
            elif input_data["progress"] == "not_completed":
                query = query.filter(~Problem.id.in_(completed_problems))

        if input_data["difficulties"]:
            query = query.filter(Problem.difficulty.in_(input_data["difficulties"]))

        # Apply sorting
        if input_data["order_by"] == "sort_date desc":
            query = query.order_by(desc(Problem.created_at))
        elif input_data["order_by"] == "sort_date asc":
            query = query.order_by(asc(Problem.created_at))
        elif input_data["order_by"] == "popularity desc":
            query = query.order_by(
                desc(func.count(Solution.id)),
                desc(Problem.bookmark_count),
            )
        elif input_data["order_by"] == "satisfaction_percent desc,total_completed desc":
            query = query.order_by(
                desc(
                    func.round(
                        func.coalesce(
                            (Problem.positive_vote * 100.0)
                            / func.nullif(
                                Problem.positive_vote
                                + Problem.negative_vote
                                + Problem.neutral_vote,
                                0,
                            ),
                            0,
                        )
                    )
                ),
                desc(func.count(Solution.id)),
            )
        elif input_data["order_by"] == "satisfaction_percent asc":
            query = query.order_by(
                asc(
                    func.round(
                        func.coalesce(
                            (Problem.positive_vote * 100.0)
                            / func.nullif(
                                Problem.positive_vote
                                + Problem.negative_vote
                                + Problem.neutral_vote,
                                0,
                            ),
                            0,
                        )
                    )
                ),
                desc(func.count(Solution.id)),
            )
        elif input_data["order_by"] == "name asc":
            query = query.order_by(asc(Problem.name))

        # Get total count for pagination
        total_problems = query.count()
        total_pages = (total_problems + input_data["per_page"] - 1) // input_data[
            "per_page"
        ]

        # Get paginated problems
        problems_query = query.paginate(
            page=input_data["page"],
            per_page=input_data["per_page"],
            error_out=False,
        )
        problems = problems_query.items

        return Result(
            success=True,
            data={
                "problems": problems,
                "total_problems": total_problems,
                "total_pages": total_pages,
                "pagination": {
                    "page": input_data["page"],
                    "per_page": input_data["per_page"],
                    "total": total_problems,
                    "total_pages": total_pages,
                    "has_next": problems_query.has_next,
                    "has_prev": problems_query.has_prev,
                    "next_num": problems_query.next_num,
                    "prev_num": problems_query.prev_num,
                    "iter_pages": problems_query.iter_pages,
                },
            },
        )

    @staticmethod
    @BaseService._handle_errors
    def _handle_create(input_data) -> Result:
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
        return Result(success=True, data={"problem": new_problem})

    @staticmethod
    def _send_filter_data(input_data) -> Result:
        problems = input_data["problems"]
        return Result(
            success=True,
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

    @staticmethod
    def _send_frontend_filter_data(input_data) -> Result:
        problems = input_data["problems"]
        processed_problems = []
        for problem in problems:
            author = User.query.get(problem.author_id)
            processed_problems.append(
                {
                    "id": problem.id,
                    "name": problem.name,
                    "description": problem.description,
                    "difficulty": problem.difficulty,
                    "language": problem.language,
                    "language_icon": ProblemService._process_language_for_devicon(
                        problem.language
                    ),
                    "author": author.username if author else None,
                    "completed_count": problem.completed_count or 0,
                    "satisfaction_percent": round(problem.satisfaction_percent or 0),
                    "total_votes": problem.total_votes or 0,
                    "bookmark_count": problem.bookmark_count or 0,
                    "solutions": Solution.query.filter_by(problem_id=problem.id).all(),
                    "tags": problem.tags_json,
                }
            )

        return Result(
            success=True,
            data={
                "problems": processed_problems,
                "total_problems": input_data["total_problems"],
                "total_pages": input_data["total_pages"],
                "pagination": input_data["pagination"],
            },
        )

    @staticmethod
    def _send_create_data(input_data) -> Result:
        problem = input_data["problem"]
        return Result(
            success=True,
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

    @staticmethod
    def _process_language_for_devicon(language):
        """Convert language names to devicon-compatible format."""
        language_map = {
            "c++": "cplusplus",
            "c#": "csharp",
            "csharp": "csharp",
            "cpp": "cplusplus",
            "js": "javascript",
            "typescript": "typescript",
            "ts": "typescript",
            "python": "python",
            "java": "java",
            "ruby": "ruby",
            "php": "php",
            "go": "go",
            "rust": "rust",
            "swift": "swift",
            "kotlin": "kotlin",
        }
        return language_map.get(language.lower(), language.lower())

    @staticmethod
    @BaseService._handle_errors
    def _validate_create_data(input_data) -> Result:
        if not input_data["current_user"].is_authenticated:
            return Result(
                success=False,
                error="User must be authenticated",
                error_code=401,
            )

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
                return Result(success=False, error=f"{field} is required", error_code=400)

        if not isinstance(input_data["name"], str) or not (1 <= len(input_data["name"]) <= 100):
            return Result(
                success=False,
                error="Name must be a string between 1 and 100 characters",
                error_code=400,
            )
        if not isinstance(input_data["description"], str) or not (
            1 <= len(input_data["description"]) <= 2000
        ):
            return Result(
                success=False,
                error="Description must be a string between 1 and 2000 characters",
                error_code=400,
            )
        if not isinstance(input_data["tags_json"], list):
            return Result(
                success=False, error="tags_json must be a list of strings", error_code=400
            )
        if not all(isinstance(tag, str) for tag in input_data["tags_json"]):
            return Result(
                success=False,
                error="Each tag in tags_json must be a string",
                error_code=400,
            )
        if not isinstance(input_data["difficulty"], str):
            return Result(
                success=False, error="Difficulty must be a string", error_code=400
            )
        if not isinstance(input_data["language"], str):
            return Result(success=False, error="Language must be a string", error_code=400)
        if not isinstance(input_data["status"], str):
            return Result(success=False, error="Status must be a string", error_code=400)

        return Result(success=True, data=input_data)
