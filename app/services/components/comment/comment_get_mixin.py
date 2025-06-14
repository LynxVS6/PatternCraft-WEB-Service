from ...ropp_service import Result


class CommentGetMixin:
    @staticmethod
    def get_comment(input_data) -> Result:
        comment_model = input_data.get("comment_model")
        comment_id = input_data.get("comment_id")
        comment = comment_model.query.get(comment_id)
        if not comment:
            return Result.fail(
                error=f"Comment model with id {comment_id} not found",
                error_code=400,
            )
        else:
            input_data.update({"comment": comment})
            return Result.ok(input_data)
