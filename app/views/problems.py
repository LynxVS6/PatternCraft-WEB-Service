from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from app.models.bookmark import Bookmark
from app.models.problem import Problem
from app.models.solution import Solution
from app.models.comment import Comment
from app.models.discourse import (
    DiscourseComment, DiscourseReply, DiscourseVote, DiscourseReplyVote
)
from app.models.problem_vote import ProblemVote
from app.extensions import db
from app.services.like_service import LikeService
from sqlalchemy.exc import SQLAlchemyError
from .solved_problems import get_problem_query, process_language_for_devicon
from app.models.user import User

bp = Blueprint("problems", __name__)


def handle_vote(vote_model, user_id, target_id, vote_type):
    """Generic vote handling function for both comments and replies."""
    existing_vote = vote_model.query.filter_by(
        user_id=user_id,
        comment_id=target_id if vote_model == DiscourseVote else None,
        reply_id=target_id if vote_model == DiscourseReplyVote else None
    ).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            db.session.delete(existing_vote)
        else:
            existing_vote.vote_type = vote_type
    else:
        new_vote = vote_model(
            user_id=user_id,
            comment_id=target_id if vote_model == DiscourseVote else None,
            reply_id=target_id if vote_model == DiscourseReplyVote else None,
            vote_type=vote_type
        )
        db.session.add(new_vote)

    db.session.commit()
    return jsonify({"vote_count": existing_vote.parent.vote_count})


@bp.route("/problem/<int:problem_id>")
@login_required
def problem_card(problem_id):
    problem = (
        get_problem_query()
        .filter(Problem.id == problem_id)
        .first_or_404()
    )
    solutions = Solution.query.filter_by(problem_id=problem_id).all()

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
        "completed_count": problem.completed_count or 0,
        "satisfaction_percent": round(problem.satisfaction_percent or 0),
        "total_votes": problem.total_votes or 0,
        "bookmark_count": problem.bookmark_count or 0,
        "created_at": problem.created_at.strftime('%Y-%m-%d %H:%M') if problem.created_at else None,
    }

    return render_template(
        "problem_card.html",
        problem=problem_data,
        solutions=solutions
    )


@bp.route("/api/problems/<int:problem_id>/solutions")
@login_required
def get_more_solutions(problem_id):
    offset = request.args.get("offset", default=3, type=int)
    solutions = (
        Solution.query.filter_by(problem_id=problem_id)
        .offset(offset)
        .limit(3)
        .all()
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
        likes_count, liked = LikeService.toggle_like(
            current_user.id, solution_id
        )
        return jsonify({"likes": likes_count, "liked": liked})
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except SQLAlchemyError:
        return jsonify({"error": "Database error occurred"}), 500


@bp.route("/api/solutions/<int:solution_id>/comments", methods=["POST"])
@login_required
def add_comment(solution_id):
    data = request.get_json()
    comment_text = data.get("comment")

    if not comment_text:
        return jsonify({"error": "Comment is required"}), 400

    Solution.query.get_or_404(solution_id)  # Verify solution exists
    comment = Comment(
        user_id=current_user.id,
        solution_id=solution_id,
        comment=comment_text
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify(
        {
            "id": comment.id,
            "comment": comment.comment,
            "username": current_user.username,
        }
    )


@bp.route("/api/comments/<int:comment_id>", methods=["PUT"])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
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


@bp.route("/api/comments/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted successfully"})


@bp.route("/api/problems/<int:problem_id>/discourse/comments", methods=["POST"])
@login_required
def add_discourse_comment(problem_id):
    data = request.get_json()
    comment_text = data.get("comment")

    if not comment_text:
        return jsonify({"error": "Comment is required"}), 400

    Problem.query.get_or_404(problem_id)  # Verify problem exists
    comment = DiscourseComment(
        user_id=current_user.id,
        problem_id=problem_id,
        comment=comment_text
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify(
        {
            "id": comment.id,
            "comment": comment.comment,
            "username": current_user.username,
        }
    )


@bp.route("/api/problems/discourse/comments/<int:comment_id>", methods=["PUT"])
@login_required
def edit_discourse_comment(comment_id):
    comment = DiscourseComment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
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
    comment = DiscourseComment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted successfully"})


@bp.route("/api/problems/discourse/comments/<int:comment_id>/reply", methods=["POST"])
@login_required
def add_discourse_reply(comment_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        reply_text = data.get("comment")
        if not reply_text or not isinstance(reply_text, str):
            return jsonify({"error": "Valid reply text is required"}), 400

        parent_comment = DiscourseComment.query.get_or_404(comment_id)
        if not isinstance(parent_comment, DiscourseComment):
            return jsonify({"error": "Invalid parent comment"}), 400
        
        new_reply = DiscourseReply(
            user_id=current_user.id,
            comment_id=parent_comment.id,
            comment=reply_text.strip()
        )

        parent_comment.replies.append(new_reply)
        
        db.session.add(new_reply)
        db.session.commit()

        return jsonify({
            "success": True,
            "id": new_reply.id,
            "comment": new_reply.comment,
            "username": current_user.username,
            "vote_count": 0
        })
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/problems/discourse/replies/<int:reply_id>", methods=["PUT"])
@login_required
def edit_discourse_reply(reply_id):
    reply = DiscourseReply.query.get_or_404(reply_id)

    if reply.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    new_reply_text = data.get("comment")

    if not new_reply_text:
        return jsonify({"error": "Reply is required"}), 400

    reply.comment = new_reply_text
    db.session.commit()

    return jsonify({
        "id": reply.id,
        "comment": reply.comment,
        "username": reply.user.username,
    })


@bp.route("/api/problems/discourse/replies/<int:reply_id>", methods=["DELETE"])
@login_required
def delete_discourse_reply(reply_id):
    reply = DiscourseReply.query.get_or_404(reply_id)

    if reply.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(reply)
    db.session.commit()

    return jsonify({"message": "Reply deleted successfully"})


@bp.route("/api/problems/discourse/comments/<int:comment_id>/vote", methods=["POST"])
@login_required
def vote_discourse_comment(comment_id):
    data = request.get_json()
    vote_type = data.get("vote_type")

    if vote_type not in ["up", "down"]:
        return jsonify({"error": "Invalid vote type"}), 400

    DiscourseComment.query.get_or_404(comment_id)
    return handle_vote(DiscourseVote, current_user.id, comment_id, vote_type)


@bp.route("/api/problems/discourse/replies/<int:reply_id>/vote", methods=["POST"])
@login_required
def vote_discourse_reply(reply_id):
    data = request.get_json()
    vote_type = data.get("vote_type")

    if vote_type not in ["up", "down"]:
        return jsonify({"error": "Invalid vote type"}), 400

    DiscourseReply.query.get_or_404(reply_id)
    return handle_vote(DiscourseReplyVote, current_user.id, reply_id, vote_type)


@bp.route("/api/problems/<int:problem_id>/bookmark", methods=["POST"])
@login_required
def toggle_bookmark(problem_id):
    try:
        # Verify the problem exists
        problem = Problem.query.get_or_404(problem_id)
        
        # Check for existing bookmark
        bookmark = Bookmark.query.filter_by(
            user_id=current_user.id, 
            problem_id=problem_id
        ).first()

        if bookmark:
            db.session.delete(bookmark)
            problem.bookmark_count = max(0, problem.bookmark_count - 1)  # Prevent negative count
            bookmarked = False
        else:
            bookmark = Bookmark(user_id=current_user.id, problem_id=problem_id)
            db.session.add(bookmark)
            problem.bookmark_count += 1
            bookmarked = True

        db.session.commit()

        return jsonify({
            "bookmarked": bookmarked,
            "bookmark_count": problem.bookmark_count
        })

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

        vote_type = data.get("vote_type")
        if not vote_type or vote_type not in ["positive", "neutral", "negative"]:
            return jsonify({"error": "Invalid vote type"}), 400

        problem = Problem.query.get_or_404(problem_id)
        existing_vote = ProblemVote.query.filter_by(
            user_id=current_user.id,
            problem_id=problem_id
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
                user_id=current_user.id,
                problem_id=problem_id,
                vote_type=vote_type
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
            user_id=current_user.id,
            problem_id=problem_id
        ).first()
        
        vote_type = current_vote.vote_type if current_vote else None

        return jsonify({
            "vote_type": vote_type,
            "satisfaction_percent": round(problem.satisfaction_percent or 0),
            "total_votes": problem.total_votes or 0
        })

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error: {str(e)}")  # For debugging
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # For debugging
        return jsonify({"error": str(e)}), 500
