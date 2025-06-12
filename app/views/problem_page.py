from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from app.models.bookmark import Bookmark
from app.models import Problem, ProblemVote
from app.models import Solution, SolutionVote
from app.models.solution_comment import Comment, CommentVote
from app.models.discourse_comment import DiscourseComment, DiscourseVote
from app.extensions import db
from .problem_hub import get_problem_query, process_language_for_devicon
from app.models.user import User
from app.utils.validators import validate_comment_data, validate_vote_type
from app.forms.forms import CommentForm
from app.services.comment_service import CommentService
from app.services.vote_service import (
    EmojiVoteService,
    ArrowVoteService,
    LikeVoteService,
)

bp = Blueprint("problems", __name__)


def parse_vote_request(allowed_types: list[str]):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    is_valid, error = validate_vote_type(data, allowed_types)
    if not is_valid:
        return jsonify({"error": error}), 400

    return data.get("vote_type"), 200


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
    data = request.get_json()
    is_valid, error = validate_comment_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    comment_text = data.get("comment")

    result = CommentService.submit_comment(
        Solution, Comment, solution_id, current_user, comment_text
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(
        {
            "id": result.data["comment_id"],
            "comment": result.data["comment"],
            "username": result.data["username"],
            "user_id": result.data["user_id"],
        }
    )


@bp.route("/api/comments/<int:comment_id>", methods=["PUT"])
@login_required
def edit_comment(comment_id):
    data = request.get_json()
    is_valid, error = validate_comment_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    new_comment_text = data.get("comment")

    result = CommentService.edit_comment(
        Comment, comment_id, current_user, new_comment_text
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify({
        "id": result.data["comment_id"],
        "comment": result.data["comment"],
        "username": result.data["username"],
    })


@bp.route("/api/comments/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id):
    result = CommentService.delete_comment(
        Comment, comment_id, current_user
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(
        {"message": result.data["message"]}
    )



@bp.route("/api/problems/<int:problem_id>/discourse/comments", methods=["POST"])
@login_required
def add_discourse_comment(problem_id):
    data = request.get_json()
    is_valid, error = validate_comment_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    comment_text = data.get("comment")

    result = CommentService.submit_comment(
        Problem, DiscourseComment, problem_id, current_user, comment_text
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify({
        "id": result.data["comment_id"],
        "comment": result.data["comment"],
        "username": result.data["username"],
        "user_id": result.data["user_id"],
    })


@bp.route("/api/problems/discourse/comments/<int:comment_id>", methods=["PUT"])
@login_required
def edit_discourse_comment(comment_id):
    data = request.get_json()
    is_valid, error = validate_comment_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    new_comment_text = data.get("comment")

    result = CommentService.edit_comment(
        DiscourseComment, comment_id, current_user, new_comment_text
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify({
        "id": result.data["comment_id"],
        "comment": result.data["comment"],
        "username": result.data["username"],
    })


@bp.route("/api/problems/discourse/comments/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_discourse_comment(comment_id):
    result = CommentService.delete_comment(
        DiscourseComment, comment_id, current_user
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(
        {"message": result.data["message"]}
    )


@bp.route("/api/problems/<int:problem_id>/bookmark", methods=["POST"])
@login_required
def toggle_bookmark(problem_id):
    try:
        # Verify the problem exists
        problem = Problem.query.get_or_404(problem_id)

        # Check for existing bookmark
        bookmark = Bookmark.query.filter_by(
            user_id=current_user.id, problem_id=problem_id
        ).first()

        if bookmark:
            db.session.delete(bookmark)
            problem.bookmark_count = max(
                0, problem.bookmark_count - 1
            )  # Prevent negative count
            bookmarked = False
        else:
            bookmark = Bookmark(user_id=current_user.id, problem_id=problem_id)
            db.session.add(bookmark)
            problem.bookmark_count += 1
            bookmarked = True

        db.session.commit()

        return jsonify(
            {"bookmarked": bookmarked, "bookmark_count": problem.bookmark_count}
        )

    except Exception as e:
        db.session.rollback()
        print(f"Bookmark error: {str(e)}")  # For debugging
        return jsonify({"error": "Failed to update bookmark"}), 500


@bp.route("/api/solutions/<int:solution_id>/like", methods=["POST"])
@login_required
def toggle_solution_like(solution_id):
    vote_type, response_code = parse_vote_request(["like", "dislike"])

    if response_code != 200:
        return vote_type

    result = LikeVoteService.submit_vote(
        Solution, SolutionVote, current_user.id, solution_id, vote_type
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify({"likes": result.data["likes"], "liked": result.data["liked"]})


@bp.route("/api/problems/discourse/comments/<int:comment_id>/vote", methods=["POST"])
@login_required
def vote_discourse_comment(comment_id):
    vote_type, response_code = parse_vote_request(["up", "down"])
    if response_code != 200:
        return vote_type

    result = ArrowVoteService.submit_vote(
        DiscourseComment, DiscourseVote, current_user.id, comment_id, vote_type
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    print(f"Vote result: {result}")
    return jsonify({"vote_count": result.data["vote_count"]})


@bp.route("/api/problems/<int:problem_id>/vote", methods=["POST"])
@login_required
def vote_problem(problem_id):
    vote_type, response_code = parse_vote_request(["positive", "neutral", "negative"])
    if response_code != 200:
        return vote_type
    result = EmojiVoteService.submit_vote(
        Problem, ProblemVote, current_user.id, problem_id, vote_type
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(
        {
            "vote_type": result.data["vote_type"],
            "satisfaction_percent": result.data["satisfaction_percent"],
            "total_votes": result.data["total_votes"],
            "action": result.data["action"],
        }
    )


@bp.route("/api/comments/<int:comment_id>/vote", methods=["POST"])
@login_required
def vote_solution_comment(comment_id):
    vote_type, response_code = parse_vote_request(["up", "down"])
    if response_code != 200:
        return vote_type

    result = ArrowVoteService.submit_vote(
        Comment, CommentVote, current_user.id, comment_id, vote_type
    )
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify({"vote_count": result.data["vote_count"]})


@bp.route("/api/problems/<int:problem_id>/description", methods=["PUT"])
@login_required
def update_problem_description(problem_id):
    try:
        # Get the problem
        problem = Problem.query.get_or_404(problem_id)

        # Check if user is the author
        if problem.author_id != current_user.id:
            return jsonify({"error": "Only the author can update the description"}), 403

        # Get the new description from request
        data = request.get_json()
        if not data or "description" not in data:
            return jsonify({"error": "Description is required"}), 400

        # Update the description
        problem.description = data["description"]
        db.session.commit()

        return jsonify({"message": "Description updated successfully"})

    except Exception as e:
        db.session.rollback()
        print(f"Error updating description: {str(e)}")
        return jsonify({"error": "Failed to update description"}), 500


@bp.route("/api/problems/<int:problem_id>/description", methods=["GET"])
@login_required
def check_description_edit_auth(problem_id):
    try:
        # Get the problem
        problem = Problem.query.get_or_404(problem_id)

        # Check if user is the author
        if problem.author_id != current_user.id:
            return jsonify({"error": "Only the author can edit the description"}), 403

        return jsonify({"message": "Authorized to edit description"})

    except Exception as e:
        print(f"Error checking description edit authorization: {str(e)}")
        return jsonify({"error": "Failed to check authorization"}), 500
