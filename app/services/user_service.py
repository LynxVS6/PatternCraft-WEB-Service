from app.extensions import db
from .base_service import BaseService, Result
from .email_service import send_confirmation_email
from .validators.user_validator import UserValidator


class UserService(BaseService):
    @staticmethod
    def edit_profile(raw_data, current_user) -> Result:
        input_data = {
            "raw_data": raw_data,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            UserService._parse_edit_profile,
            UserService._validate_edit_profile,
            UserService._handle_edit_profile,
            UserService._send_profile_data,
        )

    @staticmethod
    def change_password(raw_data, current_user) -> Result:
        input_data = {
            "raw_data": raw_data,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            UserService._parse_password_change,
            UserService._validate_password_change,
            UserService._handle_password_change,
            UserService._send_password_data,
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_edit_profile(input_data):
        raw_data = input_data["raw_data"]
        return Result(
            True,
            data={
                "username": raw_data["username"],
                "email": raw_data["email"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_password_change(input_data):
        raw_data = input_data["raw_data"]
        return Result(
            True,
            data={
                "current_password": raw_data["current_password"],
                "new_password": raw_data["new_password"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    @BaseService._handle_errors
    def _validate_edit_profile(input_data) -> Result:
        # Check authentication
        auth_result = UserValidator.check_authentication(input_data["current_user"])
        if not auth_result.success:
            return auth_result

        # Validate user data
        validation_result = UserValidator.validate_user_data(
            username=input_data["username"],
            email=input_data["email"],
            current_user=input_data["current_user"],
        )
        if not validation_result.success:
            return validation_result

        return Result(success=True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _validate_password_change(input_data) -> Result:
        # Check authentication
        auth_result = UserValidator.check_authentication(input_data["current_user"])
        if not auth_result.success:
            return auth_result

        # Validate current password
        current_password_result = UserValidator.validate_password(
            input_data["current_password"],
            input_data["current_user"],
        )
        if not current_password_result.success:
            return current_password_result

        # Validate new password
        new_password_result = UserValidator.validate_password(
            input_data["new_password"],
        )
        if not new_password_result.success:
            return new_password_result

        # Check if new password is same as current
        if input_data["current_password"] == input_data["new_password"]:
            return Result(
                success=False,
                error="New password must be different from current password",
                error_code=400,
            )

        return Result(success=True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _handle_edit_profile(input_data) -> Result:
        current_user = input_data["current_user"]
        username = input_data["username"]
        email = input_data["email"]

        try:
            if username != current_user.username:
                current_user.username = username

            if email != current_user.email:
                current_user.email = email
                current_user.email_confirmed = False
                try:
                    send_confirmation_email(current_user)
                except Exception as e:
                    db.session.rollback()
                    return Result(
                        success=False,
                        error="Failed to send confirmation email",
                        error_code=500,
                    )

            db.session.commit()
            return Result(success=True, data={"user": current_user})
        except Exception as e:
            db.session.rollback()
            return Result(
                success=False,
                error="Failed to update profile",
                error_code=500,
            )

    @staticmethod
    @BaseService._handle_errors
    def _handle_password_change(input_data) -> Result:
        current_user = input_data["current_user"]
        try:
            current_user.set_password(input_data["new_password"])
            db.session.commit()
            return Result(success=True, data={"user": current_user})
        except Exception as e:
            db.session.rollback()
            return Result(
                success=False,
                error="Failed to change password",
                error_code=500,
            )

    @staticmethod
    def _send_profile_data(input_data) -> Result:
        user = input_data["user"]
        message = "Profile updated successfully"
        if not user.email_confirmed:
            message += ". Please check your email to confirm your new email address."

        return Result(
            success=True,
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "email_confirmed": user.email_confirmed,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "message": message,
            },
        )

    @staticmethod
    def _send_password_data(input_data) -> Result:
        user = input_data["user"]
        return Result(
            success=True,
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "email_confirmed": user.email_confirmed,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "message": "Password changed successfully",
            },
        )
