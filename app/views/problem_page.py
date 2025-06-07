from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from app.models.bookmark import Bookmark
from app.models import Problem, ProblemVote
from app.models import Solution, SolutionVote
from app.models.solution_comment import Comment, CommentVote
from app.models.discourse_comment import DiscourseComment, DiscourseVote
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from .problem_hub import get_problem_query, process_language_for_devicon
from app.models.user import User
from app.utils.validators import validate_comment_data, validate_vote_type
from app.forms.forms import CommentForm
from app.services.vote_service import (
    EmojiVoteService,
    ArrowVoteService,
    LikeVoteService,
)

bp = Blueprint("problems", __name__)


def get_vote_type(allowed_types: list[str]):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    is_valid, error = validate_vote_type(data, allowed_types)
    if not is_valid:
        return jsonify({"error": error}), 400

    return data.get("vote_type"), 200


def handle_vote_service_response(result):
    if not result.success:
        if result.error_code == "NOT_FOUND":
            return jsonify({"error": result.error}), 404
        return jsonify({"error": result.error}), 400

    return None, 200


@bp.route("/problem/<int:problem_id>")
@login_required
def problem_page(problem_id):
    problem = get_problem_query().filter(Problem.id == problem_id).first_or_404()
    solutions = Solution.query.filter_by(problem_id=problem_id).all()
    discourse_comments = DiscourseComment.query.filter_by(problem_id=problem_id).all()

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


@bp.route("/api/solutions/<int:solution_id>/like", methods=["POST"])
@login_required
def toggle_solution_like(solution_id):
    print("getting request")
    try:
        vote_type, response_code = get_vote_type(["like", "dislike"])
        print("processing response_code")
        if response_code != 200:
            print("error")
            return vote_type

        result = LikeVoteService.submit_vote(
            Solution, SolutionVote, current_user.id, solution_id, vote_type
        )
        print("3-"*30)
        response, response_code = handle_vote_service_response(result)
        if response_code != 200:
            return response
        print("4-"*30)
        return jsonify({
            "likes": result.data["likes"],
            "liked": result.data["liked"]
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except SQLAlchemyError:
        return jsonify({"error": "Database error occurred"}), 500


@bp.route("/api/solutions/<int:solution_id>/comments", methods=["POST"])
@login_required
def add_solution_comment(solution_id):
    data = request.get_json()
    is_valid, error = validate_comment_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    comment_text = data.get("comment")

    comment = Comment(
        comment=comment_text,
        user_id=current_user.id,
        solution_id=solution_id,
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify(
        {
            "id": comment.id,
            "comment": comment.comment,
            "username": current_user.username,
            "user_id": current_user.id,
        }
    )


@bp.route("/api/comments/<int:comment_id>", methods=["PUT"])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    is_valid, error = validate_comment_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    new_comment_text = data.get("comment")

    comment.comment = new_comment_text
    db.session.commit()

    return jsonify(
        {
            "id": comment.id,
            "comment": comment.comment,
            "username": comment.user.username,
        }
    )


@bp.route("/api/comments/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id):
    try:
        comment = Comment.query.get_or_404(comment_id)

        if comment.user_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403

        # Delete associated votes first
        CommentVote.query.filter_by(comment_id=comment_id).delete()

        # Then delete the comment
        db.session.delete(comment)
        db.session.commit()

        return jsonify({"message": "Comment deleted successfully"})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting comment: {str(e)}")  # For debugging
        return jsonify({"error": "Failed to delete comment"}), 500


@bp.route("/api/problems/<int:problem_id>/discourse/comments", methods=["POST"])
@login_required
def add_discourse_comment(problem_id):
    print(f"Adding discourse comment for problem {problem_id}")
    data = request.get_json()
    is_valid, error = validate_comment_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    comment_text = data.get("comment")
    print(f"Comment text: {comment_text}")

    if not comment_text:
        return jsonify({"error": "Comment is required"}), 400

    Problem.query.get_or_404(problem_id)  # Verify problem exists
    comment = DiscourseComment(
        user_id=current_user.id, problem_id=problem_id, comment=comment_text
    )

    db.session.add(comment)
    db.session.commit()
    print(f"Created comment with ID: {comment.id}")

    response_data = {
        "id": comment.id,
        "comment": comment.comment,
        "username": current_user.username,
        "user_id": current_user.id,
        "vote_count": comment.vote_count,
    }
    print(f"Sending response: {response_data}")
    return jsonify(response_data)


@bp.route("/api/problems/discourse/comments/<int:comment_id>", methods=["PUT"])
@login_required
def edit_discourse_comment(comment_id):
    comment = DiscourseComment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    is_valid, error = validate_comment_data(data)
    if not is_valid:
        return jsonify({"error": error}), 400
    new_comment_text = data.get("comment")

    if not new_comment_text:
        return jsonify({"error": "Comment is required"}), 400

    comment.comment = new_comment_text
    db.session.commit()

    return jsonify(
        {
            "id": comment.id,
            "comment": comment.comment,
            "username": comment.user.username,
        }
    )


@bp.route("/api/problems/discourse/comments/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_discourse_comment(comment_id):
    try:
        comment = DiscourseComment.query.get_or_404(comment_id)

        if comment.user_id != current_user.id:
            return jsonify({"error": "Unauthorized"}), 403

        # Delete associated votes first
        DiscourseVote.query.filter_by(comment_id=comment_id).delete()

        # Then delete the comment
        db.session.delete(comment)
        db.session.commit()

        return jsonify({"message": "Comment deleted successfully"})
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting discourse comment: {str(e)}")  # For debugging
        return jsonify({"error": "Failed to delete comment"}), 500


@bp.route("/api/problems/discourse/comments/<int:comment_id>/vote", methods=["POST"])
@login_required
def vote_discourse_comment(comment_id):
    vote_type, response_code = get_vote_type(["up", "down"])
    if response_code != 200:
        return vote_type

    result = ArrowVoteService.submit_vote(
        DiscourseComment, DiscourseVote, current_user.id, comment_id, vote_type
    )

    response, response_code = handle_vote_service_response(result)
    if response_code != 200:
        return response

    print(f"Vote result: {result}")
    return jsonify({"vote_count": result.data["vote_count"]})


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


@bp.route("/api/problems/<int:problem_id>/vote", methods=["POST"])
@login_required
def vote_problem(problem_id):
    try:
        vote_type, response_code = get_vote_type(["positive", "neutral", "negative"])
        if response_code != 200:
            return vote_type
        result = EmojiVoteService.submit_vote(
            Problem, ProblemVote, current_user.id, problem_id, vote_type
        )

        response, response_code = handle_vote_service_response(result)
        if response_code != 200:
            return response

        return jsonify(
            {
                "vote_type": result.data["vote_type"],
                "satisfaction_percent": result.data["satisfaction_percent"],
                "total_votes": result.data["total_votes"],
                "action": result.data["action"],
            }
        )
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error: {str(e)}")  # For debugging
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # For debugging
        return jsonify({"error": str(e)}), 500


@bp.route("/api/comments/<int:comment_id>/vote", methods=["POST"])
@login_required
def vote_solution_comment(comment_id):
    vote_type, response_code = get_vote_type(["up", "down"])
    if response_code != 200:
        return vote_type

    result = ArrowVoteService.submit_vote(
        Comment, CommentVote, current_user.id, comment_id, vote_type
    )

    response, response_code = handle_vote_service_response(result)
    if response_code != 200:
        return response

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
