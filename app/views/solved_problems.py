from flask import Blueprint, render_template, request
from app.models.problem import Problem
from app.models.solution import Solution
from flask_login import login_required
from sqlalchemy import func
from app.models.user import User

bp = Blueprint("solved_problems", __name__)


def process_language_for_devicon(language):
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


def get_problem_query():
    """Returns a base query for Problem model with aggregated columns."""
    return (
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


@bp.route("/solved-problems")
@login_required
def solved_problems():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    # Get total count for pagination
    total_problems = get_problem_query().count()
    total_pages = (total_problems + per_page - 1) // per_page

    # Get paginated problems
    problems_query = get_problem_query().paginate(
        page=page, per_page=per_page, error_out=False
    )
    problems = problems_query.items

    # Process the problems to include solutions and format the data
    processed_problems = []
    for problem in problems:
        # Get the author's username
        author = User.query.get(problem.author_id)

        problem_dict = {
            "id": problem.id,
            "name": problem.name,
            "description": problem.description,
            "difficulty": problem.difficulty,
            "language": problem.language,
            "language_icon": process_language_for_devicon(problem.language),
            "author": author.username if author else None,
            "completed_count": problem.completed_count or 0,
            "satisfaction_percent": round(problem.satisfaction_percent or 0),
            "total_votes": problem.total_votes or 0,
            "bookmark_count": problem.bookmark_count or 0,
            "solutions": Solution.query.filter_by(problem_id=problem.id).all(),
            "tags": problem.tags_json,
        }
        processed_problems.append(problem_dict)

    # Get languages and tags for filters
    languages = [
        {"code": "python", "name": "Python"},
        {"code": "java", "name": "Java"},
        {"code": "javascript", "name": "JavaScript"},
        {"code": "cplusplus", "name": "C++"},
        {"code": "csharp", "name": "C#"},
    ]

    # Get unique tags from all problems
    all_tags = set()
    for problem in Problem.query.all():
        if problem.tags_json:
            all_tags.update(problem.tags_json)

    tags = [
        {
            "name": tag,
            "count": Problem.query.filter(Problem.tags_json.contains([tag])).count(),
            "selected": False,
        }
        for tag in sorted(all_tags)
    ]

    return render_template(
        "solved_problems.html",
        problems=processed_problems,
        pagination={
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "total_problems": total_problems,
        },
        languages=languages,
        max=max,
        min=min,
        tags=tags,
    )
