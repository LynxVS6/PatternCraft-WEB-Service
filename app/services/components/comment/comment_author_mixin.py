from ...ropp_service import Result


class CommentAuthorMixin:
    @staticmethod
    def validate_author(input_data):
        comment = input_data["comment"]
        current_user = input_data["current_user"]
        if comment.user_id != current_user.id:
            return Result.fail(error="Unauthorized", error_code=403)
        return Result.ok(input_data)