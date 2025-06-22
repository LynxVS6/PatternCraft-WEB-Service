from app.extensions import db
from ...ropp_service import Result
from .comment_update_mixin import CommentUpdateMixin


class SubmitComment(CommentUpdateMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        input_data.update(raw_json)
        return Result.ok(data=input_data)

    @staticmethod
    def execute(input_data):
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
        return Result.ok(input_data)
