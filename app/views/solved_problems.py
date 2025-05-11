from flask import Blueprint, render_template, jsonify, request
from app.models.problem import Problem
from app.models.solution import Solution
from app.models.comment import Comment
from app.extensions import db
from flask_login import login_required, current_user
from app.services.like_service import LikeService
from sqlalchemy.exc import SQLAlchemyError

bp = Blueprint('solved_problems', __name__)


@bp.route('/solved-problems')
@login_required
def solved_problems():
    problems = Problem.query.all()
    return render_template('solved_problems.html', problems=problems)


@bp.route('/api/problems/<int:problem_id>/solutions')
@login_required
def get_more_solutions(problem_id):
    offset = request.args.get('offset', default=3, type=int)
    solutions = Solution.query.filter_by(
        problem_id=problem_id).offset(offset).limit(3).all()

    return jsonify([{
        'id': solution.id,
        'solution': solution.solution,
        'likes': solution.likes,
        'username': solution.user.username
    } for solution in solutions])


@bp.route('/api/solutions/<int:solution_id>/like', methods=['POST'])
@login_required
def toggle_solution_like(solution_id):
    try:
        likes_count, liked = LikeService.toggle_like(current_user.id, solution_id)
        return jsonify({
            'likes': likes_count,
            'liked': liked
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except SQLAlchemyError:
        return jsonify({'error': 'Database error occurred'}), 500


@bp.route('/api/solutions/<int:solution_id>/comments', methods=['POST'])
@login_required
def add_comment(solution_id):
    data = request.get_json()
    comment_text = data.get('comment')

    if not comment_text:
        return jsonify({'error': 'Comment is required'}), 400

    Solution.query.get_or_404(solution_id)  # Verify solution exists
    comment = Comment(
        user_id=current_user.id,
        solution_id=solution_id,
        comment=comment_text
    )

    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'id': comment.id,
        'comment': comment.comment,
        'username': current_user.username
    })


@bp.route('/api/comments/<int:comment_id>', methods=['PUT'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if the current user is the author of the comment
    if comment.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_comment_text = data.get('comment')
    
    if not new_comment_text:
        return jsonify({'error': 'Comment is required'}), 400
    
    comment.comment = new_comment_text
    db.session.commit()
    
    return jsonify({
        'id': comment.id,
        'comment': comment.comment,
        'username': comment.user.username
    })


@bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if the current user is the author of the comment
    if comment.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'message': 'Comment deleted successfully'})
