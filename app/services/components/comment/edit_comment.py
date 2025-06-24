from app.extensions import db
from ...ropp_service import Result
from .comment_update_mixin import CommentUpdateMixin
from .comment_get_mixin import CommentGetMixin
from .comment_author_mixin import CommentAuthorMixin


class EditComment(CommentGetMixin, CommentUpdateMixin, CommentAuthorMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        input_data.update(raw_json)
        return Result.ok(input_data)

    @staticmethod
    def execute(input_data):
        comment = input_data["comment"]
        comment_text = input_data["comment"]
        comment.comment = comment_text
        db.session.commit()
        print("2-" * 40)
        return Result.ok(input_data)
