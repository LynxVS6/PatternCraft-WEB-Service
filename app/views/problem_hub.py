from flask import Blueprint, render_template, request, current_app
from app.models.problem import Problem
from app.models.solution import Solution
from flask_login import login_required, current_user
from sqlalchemy import func, desc, asc, or_, and_
from app.models.user import User
from flask_sqlalchemy import SQLAlchemy

bp = Blueprint("problem_hub", __name__)
db = SQLAlchemy()


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


@bp.route("/problem-hub")
@login_required
def problem_hub():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    # Get search parameters
    search_query = request.args.get("q", "").strip()
    order_by = request.args.get("order_by", "sort_date desc")
    language = request.args.get("language", "all")
    status = request.args.get("status", "all")
    progress = request.args.get("xids", "all")
    difficulties = request.args.getlist("r")
    selected_tags = request.args.getlist("tags")

    current_app.logger.info(
        f"Search parameters: query='{search_query}', order_by='{order_by}', "
        f"language='{language}', status='{status}', progress='{progress}', "
        f"difficulties={difficulties}, tags={selected_tags}"
    )

    # Get unique tags and their counts from ALL problems before any filtering
    all_tags = set()
    tag_counts = {}
    for problem in Problem.query.all():
        if problem.tags_json:
            all_tags.update(problem.tags_json)
            # Count each tag for this problem
            for tag in problem.tags_json:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # Create tags list with accurate counts
    tags = [
        {
            "name": tag,
            "count": tag_counts[tag],
            "selected": tag in selected_tags,
        }
        for tag in sorted(all_tags)
    ]

    # Start with base query
    query = get_problem_query()
    current_app.logger.info(f"Initial query count: {query.count()}")

    # Apply all filters to the base query
    if selected_tags:
        # Use MySQL's JSON functions to check for tag presence
        tag_conditions = []
        for tag in selected_tags:
            # Use MySQL's JSON_CONTAINS function to check if the tag exists in the array
            condition = func.json_contains(Problem.tags_json, f'"{tag}"')
            tag_conditions.append(condition)

        # Combine all tag conditions with AND (all selected tags must be present)
        query = query.filter(and_(*tag_conditions))

    if search_query:
        query = query.filter(
            (Problem.name.ilike(f"%{search_query}%"))
            | (Problem.description.ilike(f"%{search_query}%"))
        )
        current_app.logger.info(f"After search filter count: {query.count()}")

    if language and language != "all":
        if language == "my-languages":
            user_languages = current_user.preferred_languages or []
            if user_languages:
                query = query.filter(Problem.language.in_(user_languages))
        else:
            query = query.filter(Problem.language == language)
        current_app.logger.info(f"After language filter count: {query.count()}")

    if status != "all":
        query = query.filter(Problem.status == status)
        current_app.logger.info(f"After status filter count: {query.count()}")

    if progress != "all":
        completed_problems = (
            db.session.query(Problem.id)
            .join(
                Solution,
                (Solution.problem_id == Problem.id)
                & (Solution.user_id == current_user.id),
            )
            .subquery()
        )

        if progress == "completed":
            query = query.filter(Problem.id.in_(completed_problems))
            current_app.logger.info("Filtering for completed problems")
        elif progress == "not_completed":
            query = query.filter(~Problem.id.in_(completed_problems))
            current_app.logger.info("Filtering for not completed problems")

        current_app.logger.info(f"After progress filter count: {query.count()}")

    if difficulties:
        query = query.filter(Problem.difficulty.in_(difficulties))
        current_app.logger.info(f"After difficulty filter count: {query.count()}")

    # Create current_filters object for template
    current_filters = {
        "search": search_query,
        "order_by": order_by,
        "language": language,
        "status": status,
        "progress": progress,
        "difficulties": difficulties,
        "tags": selected_tags,
    }

    # Apply sorting
    if order_by == "sort_date desc":
        query = query.order_by(desc(Problem.created_at))
    elif order_by == "sort_date asc":
        query = query.order_by(asc(Problem.created_at))
    elif order_by == "popularity desc":
        query = query.order_by(
            desc(func.count(Solution.id)),  # Primary sort by completed_count
            desc(Problem.bookmark_count),  # Secondary sort by bookmark_count
        )
    elif order_by == "satisfaction_percent desc,total_completed desc":
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
    elif order_by == "satisfaction_percent asc":
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
    elif order_by == "name asc":
        query = query.order_by(asc(Problem.name))

    # Get total count for pagination
    total_problems = query.count()
    total_pages = (total_problems + per_page - 1) // per_page
    current_app.logger.info(f"Total problems after all filters: {total_problems}")

    # Get paginated problems
    problems_query = query.paginate(page=page, per_page=per_page, error_out=False)
    problems = problems_query.items
    current_app.logger.info(f"Retrieved {len(problems)} problems for page {page}")

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

    # Create pagination object with required attributes
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total_problems,
        "total_pages": total_pages,
        "has_next": problems_query.has_next,
        "has_prev": problems_query.has_prev,
        "next_num": problems_query.next_num,
        "prev_num": problems_query.prev_num,
        "iter_pages": problems_query.iter_pages,
    }

    return render_template(
        "problem_hub.html",
        problems=processed_problems,
        pagination=pagination,
        languages=languages,
        tags=tags,
        current_filters=current_filters,
        max_page=total_pages,
        min_page=1,
    )
