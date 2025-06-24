from ...ropp_service import Result


class CommentUpdateMixin:
    @staticmethod
    def validate_comment_data(input_data) -> Result:
        comment_text = input_data["comment"]

        if not isinstance(comment_text, str):
            return Result.fail(error="Comment must be a string", error_code=400)
        if not (1 <= len(comment_text) <= 1000):
            return Result.fail(
                error="Comment must be between 1 and 1000 characters",
                error_code=400,
            )

        return Result.ok(input_data)

    @staticmethod
    def format(input_data):
        comment_id = input_data["comment_id"]
        comment_text = input_data["comment"]
        current_user = input_data["current_user"]
        return Result.ok(
            data={
                "id": comment_id,
                "comment": comment_text,
                "username": current_user.username,
                "user_id": current_user.id,
            },
        )
