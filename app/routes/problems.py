from flask import jsonify
from flask_login import login_required, current_user
from app.models.problem import Problem
from app.models.bookmark import Bookmark
from app.extensions import db

@bp.route('/api/problems/<int:problem_id>/bookmark', methods=['POST'])
@login_required
def toggle_bookmark(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    bookmark = Bookmark.query.filter_by(
        user_id=current_user.id,
        problem_id=problem_id
    ).first()
    
    if bookmark:
        db.session.delete(bookmark)
        problem.bookmark_count -= 1
        bookmarked = False
    else:
        bookmark = Bookmark(user_id=current_user.id, problem_id=problem_id)
        db.session.add(bookmark)
        problem.bookmark_count += 1
        bookmarked = True
    
    db.session.commit()
    
    return jsonify({
        'bookmarked': bookmarked,
        'bookmark_count': problem.bookmark_count
    }) 