from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from .problem_hub import get_problem_query
from app.utils.process_language_for_devicon import process_language_for_devicon
from app.forms.forms import CommentForm
from app.models import (
    User,
    Bookmark,
    Problem,
    ProblemVote,
    Solution,
    SolutionVote,
    Comment,
    CommentVote,
    DiscourseComment,
    DiscourseVote,
)
from app.services import (
    DescriptionService,
    BookmarkService,
    CommentService,
    VoteService,
)

bp = Blueprint("problems", __name__)


@bp.route("/problem/<int:problem_id>")
@login_required
def problem_page(problem_id):
    problem = get_problem_query().filter(Problem.id == problem_id).first_or_404()
    solutions = Solution.query.filter_by(problem_id=problem_id).all()
    discourse_comments = DiscourseComment.query.filter_by(target_id=problem_id).all()

    comment_form = CommentForm()

    # Get the author's username
    author = User.query.get(problem.author_id)

    # Format the problem data to handle null values consistently
    problem_data = {
        "id": problem.id,
        "name": problem.name,
        "description": problem.description,
        "difficulty": problem.difficulty,
        "language": problem.language,
        "language_icon": process_language_for_devicon(problem.language),
        "author": author.username if author else None,
        "author_id": problem.author_id,
        "completed_count": problem.completed_count or 0,
        "satisfaction_percent": round(problem.satisfaction_percent or 0),
        "total_votes": problem.total_votes or 0,
        "bookmark_count": problem.bookmark_count or 0,
        "created_at": (
            problem.created_at.strftime("%Y-%m-%d %H:%M")
            if problem.created_at
            else None
        ),
    }

    return render_template(
        "problem_page.html",
        problem=problem_data,
        solutions=solutions,
        discourse_comments=discourse_comments,
        comment_form=comment_form,
    )


@bp.route("/api/problems/<int:problem_id>/solutions")
@login_required
def get_more_solutions(problem_id):
    offset = request.args.get("offset", default=3, type=int)
    solutions = (
        Solution.query.filter_by(problem_id=problem_id).offset(offset).limit(3).all()
    )

    return jsonify(
        [
            {
                "id": solution.id,
                "solution": solution.solution,
                "likes": solution.votes,
                "username": solution.user.username,
            }
            for solution in solutions
        ]
    )


@bp.route("/api/solutions/<int:solution_id>/comments", methods=["POST"])
@login_required
def add_solution_comment(solution_id):
    raw_json = request.get_json()
    result = CommentService.submit_comment(
        Solution, Comment, raw_json, solution_id, current_user
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/comments/<int:comment_id>", methods=["PUT"])
@login_required
def edit_comment(comment_id):
    raw_json = request.get_json()
    result = CommentService.edit_comment(Comment, raw_json, comment_id, current_user)
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/comments/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id):
    result = CommentService.delete_comment(Comment, comment_id, current_user)
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/problems/<int:problem_id>/discourse/comments", methods=["POST"])
@login_required
def add_discourse_comment(problem_id):
    raw_json = request.get_json()
    result = CommentService.submit_comment(
        Problem, DiscourseComment, raw_json, problem_id, current_user
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/problems/discourse/comments/<int:comment_id>", methods=["PUT"])
@login_required
def edit_discourse_comment(comment_id):
    raw_json = request.get_json()
    result = CommentService.edit_comment(
        DiscourseComment, raw_json, comment_id, current_user
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/problems/discourse/comments/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_discourse_comment(comment_id):
    result = CommentService.delete_comment(DiscourseComment, comment_id, current_user)
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/problems/<int:problem_id>/bookmark", methods=["POST"])
@login_required
def toggle_bookmark(problem_id):
    result = BookmarkService.submit_bookmark(
        Problem, Bookmark, problem_id, current_user
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/solutions/<int:solution_id>/like", methods=["POST"])
@login_required
def toggle_solution_like(solution_id):
    raw_json = request.get_json()
    result = VoteService.submit_vote(
        Solution, SolutionVote, raw_json, solution_id, current_user, vote_class="like"
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/problems/discourse/comments/<int:comment_id>/vote", methods=["POST"])
@login_required
def vote_discourse_comment(comment_id):
    raw_json = request.get_json()
    result = VoteService.submit_vote(
        DiscourseComment,
        DiscourseVote,
        raw_json,
        comment_id,
        current_user,
        vote_class="arrow",
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/problems/<int:problem_id>/vote", methods=["POST"])
@login_required
def vote_problem(problem_id):
    raw_json = request.get_json()
    result = VoteService.submit_vote(
        Problem, ProblemVote, raw_json, problem_id, current_user, vote_class="emoji"
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/comments/<int:comment_id>/vote", methods=["POST"])
@login_required
def vote_solution_comment(comment_id):
    raw_json = request.get_json()
    result = VoteService.submit_vote(
        Comment, CommentVote, raw_json, comment_id, current_user, vote_class="arrow"
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/problems/<int:problem_id>/description", methods=["PUT"])
@login_required
def update_problem_description(problem_id):
    raw_json = request.get_json()
    result = DescriptionService.submit_description(
        Problem, raw_json, problem_id, current_user
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)


@bp.route("/api/problems/<int:problem_id>/description", methods=["GET"])
@login_required
def check_description_edit_auth(problem_id):
    result = DescriptionService.check_edit_auth(Problem, problem_id, current_user)
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data)
