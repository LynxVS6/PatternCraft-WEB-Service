from app.extensions import db
from .base_service import BaseService, Result


class CommentService(BaseService):
    @staticmethod
    def submit_comment(
        target_model, comment_model, raw_data, target_id, current_user
    ) -> Result:
        input_data = {
            "target_model": target_model,
            "comment_model": comment_model,
            "raw_data": raw_data,
            "target_id": target_id,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            CommentService._parse_submit,
            CommentService._validate_comment_data,
            CommentService._handle_submit,
            CommentService._send_data,
        )

    @staticmethod
    def edit_comment(comment_model, raw_data, comment_id, current_user) -> Result:
        input_data = {
            "comment_model": comment_model,
            "raw_data": raw_data,
            "comment_id": comment_id,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            CommentService._parse_edit,
            BaseService._combine_funcs(
                CommentService._get_comment,
                CommentService._validate_author,
                CommentService._validate_comment_data,
            ),
            CommentService._handle_edit,
            CommentService._send_data,
        )

    @staticmethod
    def delete_comment(comment_model, comment_id, current_user):
        input_data = {
            "comment_model": comment_model,
            "comment_id": comment_id,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            CommentService._parse_delete,
            BaseService._combine_funcs(
                CommentService._get_comment, CommentService._validate_author
            ),
            CommentService._handle_delete,
            CommentService._send_data,
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_submit(input_data):
        raw_data = input_data["raw_data"]
        comment_text = raw_data["comment"]
        return Result(
            True,
            data={
                "target_model": input_data["target_model"],
                "comment_model": input_data["comment_model"],
                "comment_text": comment_text,
                "target_id": input_data["target_id"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_edit(input_data):
        raw_data = input_data["raw_data"]
        comment_text = raw_data["comment"]
        return Result(
            True,
            data={
                "comment_model": input_data["comment_model"],
                "comment_text": comment_text,
                "comment_id": input_data["comment_id"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_delete(input_data):
        return Result(
            True,
            data={
                "comment_model": input_data["comment_model"],
                "comment_id": input_data["comment_id"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    @BaseService._handle_errors
    def _handle_submit(input_data):
        comment_model = input_data["comment_model"]
        current_user = input_data["current_user"]
        target_id = input_data["target_id"]
        comment_text = input_data["comment_text"]
        comment = comment_model(
            comment=comment_text,
            user_id=current_user.id,
            target_id=target_id,
        )

        db.session.add(comment)
        db.session.commit()

        input_data.update({"comment_id": comment.id})
        return Result(True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _handle_edit(input_data):
        comment = input_data["comment"]
        comment_text = input_data["comment_text"]
        comment.comment = comment_text
        db.session.commit()
        print("2-"*40)
        return Result(True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _handle_delete(input_data):
        comment = input_data["comment"]
        db.session.delete(comment)
        db.session.commit()
        return Result(True, data=input_data)

    @staticmethod
    def _validate_author(input_data):
        comment = input_data["comment"]
        current_user = input_data["current_user"]
        if comment.user_id != current_user.id:
            return Result(success=False, error="Unauthorized", error_code=403)
        return Result(True, data=input_data)

    @staticmethod
    def _validate_comment_data(input_data) -> Result:
        comment_text = input_data["comment_text"]
        print("1-"*40)
        if not isinstance(comment_text, str):
            return Result(
                success=False, error="Comment must be a string", error_code=400
            )
        if not (1 <= len(comment_text) <= 1000):
            return Result(
                success=False,
                error="Comment must be between 1 and 1000 characters",
                error_code=400,
            )

        return Result(success=True, data=input_data)

    @staticmethod
    def _send_data(input_data):
        comment_id = input_data["comment_id"]
        comment_text = input_data.get("comment_text")  # May be empty if method="DELETE"
        current_user = input_data["current_user"]
        return Result(
            success=True,
            data={
                "id": comment_id,
                "comment": comment_text,
                "username": current_user.username,
                "user_id": current_user.id,
            },
        )

    @staticmethod
    def _get_comment(input_data) -> Result:
        comment_model = input_data.get("comment_model")
        comment_id = input_data.get("comment_id")
        comment = comment_model.query.get(comment_id)
        if not comment:
            return Result(
                success=False,
                error=f"Comment model with id {comment_id} not found",
                error_code=400,
            )
        else:
            input_data.update({"comment": comment})
            return Result(success=True, data=input_data)
