from app.extensions import db
from ...ropp_service import Result
from .comment_update_mixin import CommentUpdateMixin
from .comment_get_mixin import CommentGetMixin
from .comment_author_mixin import CommentAuthorMixin


class EditComment(CommentGetMixin, CommentUpdateMixin, CommentAuthorMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        comment_text = raw_json["comment"]
        return Result.ok(
            data={
                "comment_model": input_data["comment_model"],
                "comment_text": comment_text,
                "comment_id": input_data["comment_id"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    def execute(input_data):
        comment = input_data["comment"]
        comment_text = input_data["comment_text"]
        comment.comment = comment_text
        db.session.commit()
        print("2-" * 40)
        return Result.ok(input_data)
