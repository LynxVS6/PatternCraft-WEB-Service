from app.extensions import db
from ...ropp_service import Result
from app.utils.process_language_for_devicon import process_language_for_devicon
from app.models import Problem, Solution, User
from ...mixins.authentication_mixin import AuthenticationMixin
from sqlalchemy import func, desc, asc, and_


class FilterProblemsFrontend(AuthenticationMixin):
    @staticmethod
    def execute(input_data) -> Result:
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

        query = query.filter((Problem.is_hidden == False) | (Problem.author_id == input_data["current_user"].id))

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



        return Result.ok(
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
    def format(input_data) -> Result:
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
                    "language_icon": process_language_for_devicon(
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

        return Result.ok(
            data={
                "problems": processed_problems,
                "total_problems": input_data["total_problems"],
                "total_pages": input_data["total_pages"],
                "pagination": input_data["pagination"],
            },
        )
