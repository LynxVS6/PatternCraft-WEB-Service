from ...ropp_service import Result


class DescriptionMixin:
    @staticmethod
    def validate_author(input_data):
        target = input_data["target"]
        current_user = input_data["current_user"]
        if target.author_id != current_user.id:
            return Result.fail(
                error="Only the author can update the description",
                error_code=403,
            )
        return Result.ok(input_data)
