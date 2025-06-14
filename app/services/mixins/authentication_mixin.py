from ..ropp_service import Result


class AuthenticationMixin:
    @staticmethod
    def validate_authentication(input_data) -> Result:
        current_user = input_data["current_user"]

        if current_user is None or not current_user.is_authenticated:
            return Result.fail(
                error="User must be authenticated",
                error_code=401,
            )
        return Result.ok(input_data)
