from app.extensions import db
from .base_service import BaseService, Result


class CommentService(BaseService):
    @staticmethod
    @BaseService.handle_errors
    def submit_comment(
        target_model, comment_model, target_id, user, comment_text
    ) -> Result:
        target = target_model.query.get(target_id)
        if not target:
            return Result(
                success=False,
                error=f"Target model with id {target_id} not found",
                error_code=400,
            )

        if not comment_text:
            return Result(success=False, error="Comment is required", error_code=400)

        comment = comment_model(
            comment=comment_text,
            user_id=user.id,
            target_id=target_id,
        )

        db.session.add(comment)
        db.session.commit()

        return Result(
            success=True,
            data={
                "comment_id": comment.id,
                "comment": comment_text,
                "username": user.username,
                "user_id": user.id,
            },
        )

    @staticmethod
    @BaseService.handle_errors
    def edit_comment(comment_model, comment_id, user, comment_text) -> Result:
        comment = comment_model.query.get(comment_id)
        if not comment:
            return Result(
                success=False,
                error=f"Comment model with id {comment_id} not found",
                error_code=400,
            )

        if comment.user_id != user.id:
            return Result(success=False, error="Unauthorized", error_code=403)

        if not comment_text:
            return Result(success=False, error="Comment is required", error_code=400)

        comment.comment = comment_text
        db.session.commit()

        return Result(
            success=True,
            data={
                "comment_id": comment.id,
                "comment": comment_text,
                "username": user.username,
            },
        )

    @staticmethod
    @BaseService.handle_errors
    def delete_comment(comment_model, comment_id, user):
        try:
            comment = comment_model.query.get(comment_id)
            if not comment:
                return Result(
                    success=False,
                    error=f"Comment model with id {comment_id} not found",
                    error_code=400,
                )

            if comment.user_id != user.id:
                return Result(success=False, error="Unauthorized", error_code=403)

            db.session.delete(comment)
            db.session.commit()

            return Result(
                success=True,
                data={
                    "message": "Comment deleted successfully"
                }
            )
        except Exception as e:
            db.session.rollback()
            return Result(
                success=False, error="Failed to delete comment", error_code=500
            )
