from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from app.models.bookmark import Bookmark
from app.models.problem import Problem
from app.models.solution import Solution
from app.models.comment import Comment, CommentVote
from app.models.discourse import DiscourseComment, DiscourseVote
from app.models.problem_vote import ProblemVote
from app.extensions import db
from app.services.like_service import LikeService
from sqlalchemy.exc import SQLAlchemyError
from .problem_hub import get_problem_query, process_language_for_devicon
from app.models.user import User
from app.utils.validators import validate_comment_data, validate_vote_type

bp = Blueprint("problems", __name__)


def handle_vote(vote_model, user_id, target_id, vote_type):
    """Generic vote handling function for comments only."""
    existing_vote = vote_model.query.filter_by(
        user_id=user_id, comment_id=target_id
    ).first()

    # Check both comment types
    comment = DiscourseComment.query.get(target_id) or Comment.query.get(target_id)
    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            db.session.delete(existing_vote)
        else:
            existing_vote.vote_type = vote_type
    else:
        new_vote = vote_model(
            user_id=user_id, comment_id=target_id, vote_type=vote_type
        )
        db.session.add(new_vote)

    db.session.commit()
    return jsonify({"vote_count": comment.vote_count})


@bp.route("/problem/<int:problem_id>")
@login_required
def problem_page(problem_id):
    problem = get_problem_query().filter(Problem.id == problem_id).first_or_404()
    solutions = Solution.query.filter_by(problem_id=problem_id).all()
    discourse_comments = DiscourseComment.query.filter_by(problem_id=problem_id).all()

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
                "likes": solution.likes,
                "username": solution.user.username,
            }
            for solution in solutions
        ]
    )


@bp.route("/api/solutions/<int:solution_id>/like", methods=["POST"])
@login_required
def toggle_solution_like(solution_id):
    try:
        likes_count, liked = LikeService.toggle_like(current_user.id, solution_id)
        return jsonify({"likes": likes_count, "liked": liked})
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
    print(f"Voting on discourse comment {comment_id}")
    data = request.get_json()
    is_valid, error = validate_vote_type(data, ["up", "down"])
    if not is_valid:
        return jsonify({"error": error}), 400
    vote_type = data.get("vote_type")
    print(f"Vote type: {vote_type}")

    comment = DiscourseComment.query.get_or_404(comment_id)
    print(f"Found comment: {comment.id} by user {comment.user_id}")

    result = handle_vote(DiscourseVote, current_user.id, comment_id, vote_type)
    print(f"Vote result: {result}")
    return result


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
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        is_valid, error = validate_vote_type(data, ["positive", "neutral", "negative"])
        if not is_valid:
            return jsonify({"error": error}), 400
        vote_type = data.get("vote_type")

        problem = Problem.query.get_or_404(problem_id)
        existing_vote = ProblemVote.query.filter_by(
            user_id=current_user.id, problem_id=problem_id
        ).first()

        # If there's an existing vote, remove it first
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # If clicking the same vote type, remove the vote
                db.session.delete(existing_vote)
                vote_type = None
            else:
                # Update the vote type
                existing_vote.vote_type = vote_type
        else:
            # Create new vote
            new_vote = ProblemVote(
                user_id=current_user.id, problem_id=problem_id, vote_type=vote_type
            )
            db.session.add(new_vote)

        # Update vote counts
        problem.update_vote_counts()

        # Commit the transaction
        db.session.commit()

        # Refresh the problem object to get updated counts
        db.session.refresh(problem)

        # Get the updated vote type after the transaction
        current_vote = ProblemVote.query.filter_by(
            user_id=current_user.id, problem_id=problem_id
        ).first()

        vote_type = current_vote.vote_type if current_vote else None

        return jsonify(
            {
                "vote_type": vote_type,
                "satisfaction_percent": round(problem.satisfaction_percent or 0),
                "total_votes": problem.total_votes or 0,
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
    data = request.get_json()
    is_valid, error = validate_vote_type(data, ["up", "down"])
    if not is_valid:
        return jsonify({"error": error}), 400
    vote_type = data.get("vote_type")

    return handle_vote(CommentVote, current_user.id, comment_id, vote_type)


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
