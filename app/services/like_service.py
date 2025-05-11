from typing import Tuple
from app.extensions import db
from app.models.like import Like
from app.models.solution import Solution
from sqlalchemy.exc import SQLAlchemyError


class LikeService:
    @staticmethod
    def toggle_like(user_id: int, solution_id: int) -> Tuple[int, bool]:
        """
        Toggle like status for a solution.
        
        Args:
            user_id: ID of the user performing the action
            solution_id: ID of the solution to like/unlike
            
        Returns:
            Tuple containing:
            - int: Updated likes count
            - bool: New like status (True if liked, False if unliked)
            
        Raises:
            ValueError: If solution doesn't exist
            SQLAlchemyError: If database operation fails
        """
        solution = Solution.query.get(solution_id)
        if not solution:
            raise ValueError(f"Solution with id {solution_id} not found")

        try:
            existing_like = Like.query.filter_by(
                user_id=user_id,
                solution_id=solution_id
            ).first()

            if existing_like:
                # Unlike
                db.session.delete(existing_like)
                liked = False
            else:
                # Like
                new_like = Like(user_id=user_id, solution_id=solution_id)
                db.session.add(new_like)
                liked = True

            db.session.commit()

            # Get updated likes count
            likes_count = Like.query.filter_by(solution_id=solution_id).count()
            
            return likes_count, liked

        except SQLAlchemyError as e:
            db.session.rollback()
            raise SQLAlchemyError(f"Failed to toggle like: {str(e)}") 