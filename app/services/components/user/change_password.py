from app.extensions import db
from ...ropp_service import Result
from ...mixins import AuthenticationMixin
from ...validators import validate_password


class ChangePassword(AuthenticationMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        return Result.ok(
            data={
                "current_password": raw_json["current_password"],
                "new_password": raw_json["new_password"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    def validate_password_change(input_data) -> Result:
        # Validate current password
        current_password_result = validate_password(
            input_data["current_password"],
            input_data["current_user"],
        )
        if not current_password_result.success:
            return current_password_result

        # Validate new password
        new_password_result = validate_password(
            input_data["new_password"],
        )
        if not new_password_result.success:
            return new_password_result

        # Check if new password is same as current
        if input_data["current_password"] == input_data["new_password"]:
            return Result.fail(
                error="New password must be different from current password",
                error_code=400,
            )

        return Result.ok(input_data)

    @staticmethod
    def execute(input_data) -> Result:
        current_user = input_data["current_user"]
        current_user.set_password(input_data["new_password"])
        db.session.commit()
        return Result.ok({"user": current_user})

    @staticmethod
    def format(input_data) -> Result:
        user = input_data["user"]
        return Result.ok(
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "email_confirmed": user.email_confirmed,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "message": "Password changed successfully",
            },
        )
