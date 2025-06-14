from flask import Blueprint, render_template, request, current_app
from app.models import Problem, Solution, User
from flask_login import login_required, current_user
from sqlalchemy import func, desc, asc, or_, and_
from flask_sqlalchemy import SQLAlchemy
from app.forms.forms import ProblemsSearchForm
from app.services.problem_service import ProblemService

bp = Blueprint("problem_hub", __name__)
db = SQLAlchemy()


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


@bp.route("/problem-hub", methods=["GET"])
@login_required
def problem_hub():
    search_form = ProblemsSearchForm()
    page = request.args.get("page", 1, type=int)
    per_page = 10

    # Get search parameters from form
    search_query = request.args.get("search_input", "").strip()
    order_by = request.args.get("order_by", "sort_date desc")
    language = request.args.get("language_filter", "all")
    status = request.args.get("status_filter", "all")
    progress = request.args.get("ids_filter", "all")
    difficulties = request.args.getlist("ranks_filter")
    selected_tags = request.args.getlist("tags_filter")

    # Populate form with current values
    search_form.search_input.data = search_query
    search_form.order_by.data = order_by
    search_form.language_filter.data = language
    search_form.status_filter.data = status
    search_form.ids_filter.data = progress
    search_form.ranks_filter.data = difficulties[0] if difficulties else "all"
    search_form.tags_filter.data = selected_tags

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

    # After creating the tags list with counts
    search_form.tags_filter.choices = [
        (tag["name"], f"{tag['name']} ({tag['count']})") for tag in tags
    ]

    # Use ProblemService to filter problems
    result = ProblemService.filter_problems_frontend(
        search_query=search_query,
        order_by=order_by,
        language=language,
        status=status,
        progress=progress,
        difficulties=difficulties,
        selected_tags=selected_tags,
        page=page,
        per_page=per_page,
        current_user=current_user,
    )

    if not result.success:
        current_app.logger.error(f"Error filtering problems: {result.error}")
        return render_template(
            "problem_hub.html",
            problems=[],
            pagination={},
            languages=[],
            tags=tags,
            current_filters={},
            max_page=1,
            min_page=1,
            search_form=search_form,
        )

    # Get languages for filters
    languages = [
        {"code": "python", "name": "Python"},
        {"code": "java", "name": "Java"},
        {"code": "javascript", "name": "JavaScript"},
        {"code": "cplusplus", "name": "C++"},
        {"code": "csharp", "name": "C#"},
    ]

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

    return render_template(
        "problem_hub.html",
        problems=result.data["problems"],
        pagination=result.data["pagination"],
        languages=languages,
        tags=tags,
        current_filters=current_filters,
        max_page=result.data["total_pages"],
        min_page=1,
        search_form=search_form,
    )
