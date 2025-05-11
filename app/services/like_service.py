from typing import Tuple
from app.extensions import db
from app.models.like import Like
from app.models.solution import Solution
from sqlalchemy.exc import SQLAlchemyError


class LikeService:
    @staticmethod
    def toggle_like(user_id: int, solution_id: int) -> Tuple[int, bool]:
        if not Solution.query.get(solution_id):
            raise ValueError(f"Solution with id {solution_id} not found")

        try:
            existing_like = Like.query.filter_by(
                user_id=user_id,
                solution_id=solution_id
            ).first()

            if existing_like:
                db.session.delete(existing_like)
                liked = False
            else:
                db.session.add(Like(user_id=user_id, solution_id=solution_id))
                liked = True

            db.session.commit()
            return Like.query.filter_by(solution_id=solution_id).count(), liked

        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Failed to toggle like: {str(e)}")
