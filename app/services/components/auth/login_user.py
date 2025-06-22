from ...ropp_service import Result
from ...validators import validate_password
from app.models import User


class LoginUser:
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        input_data.update(raw_json)
        return Result.ok(input_data)

    @staticmethod
    def validate_credentials(input_data) -> Result:
        # Validate login data
        if not input_data["identity"] or not isinstance(input_data["identity"], str):
            return Result.fail(
                error="Username is required",
                error_code=400,
            )

        validation_result = validate_password(input_data["password"])
        if not validation_result.success:
            return validation_result

        return Result.ok(input_data)

    @staticmethod
    def execute(input_data) -> Result:
        identity = input_data["identity"]
        password = input_data["password"]

        user = User.query.filter(
            (User.username == identity) | (User.email == identity.lower())
        ).first()

        if not user or not user.check_password(password):
            return Result.fail(
                error="Invalid username/email or password",
                error_code=401,
            )

        if not user.email_confirmed:
            return Result.fail(
                error="Email not confirmed",
                error_code=401,
            )

        # if user.is_locked:
        #     return Result(
        #         success=False,
        #         error="Account is locked",
        #         error_code=401,
        #     )

        input_data["user"] = user
        return Result.ok(input_data)

    @staticmethod
    def format(input_data) -> Result:
        user = input_data["user"]
        return Result.ok(
            data={
                "id": user.id,
                "user": user,
                "username": user.username,
                "email": user.email,
                "email_confirmed": user.email_confirmed,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "message": "Login successful",
            },
        )
