from app.extensions import db
from .base_service import BaseService, Result
from app.models import User
from .email_service import send_confirmation_email
from .validators.user_validator import UserValidator


class AuthService(BaseService):
    @staticmethod
    def register(raw_data, current_user) -> Result:
        input_data = {
            "raw_data": raw_data,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            AuthService._parse_register_data,
            AuthService._validate_register_data,
            AuthService._handle_register,
            AuthService._send_register_data,
        )

    @staticmethod
    def login(raw_data, current_user) -> Result:
        input_data = {
            "raw_data": raw_data,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            AuthService._parse_login_data,
            AuthService._validate_login_data,
            AuthService._handle_login,
            AuthService._send_login_data,
        )

    @staticmethod
    def confirm_email(token, current_user) -> Result:
        input_data = {
            "token": token,
            "current_user": current_user,
        }
        return BaseService._process_input_data(
            input_data,
            AuthService._parse_token,
            AuthService._validate_token,
            AuthService._handle_confirm,
            AuthService._send_confirmation_data,
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_register_data(input_data):
        raw_data = input_data["raw_data"]
        return Result(
            True,
            data={
                "username": raw_data["username"],
                "email": raw_data["email"],
                "password": raw_data["password"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_login_data(input_data):
        raw_data = input_data["raw_data"]
        return Result(
            True,
            data={
                "username": raw_data["identity"],
                "password": raw_data["password"],
                "current_user": input_data["current_user"],
            },
        )

    @staticmethod
    @BaseService._parse_errors
    def _parse_token(input_data):
        return Result(True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _validate_register_data(input_data) -> Result:
        # Validate user data
        validation_result = UserValidator.validate_user_data(
            username=input_data["username"],
            email=input_data["email"],
            password=input_data["password"],
        )
        if not validation_result.success:
            return validation_result

        return Result(success=True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _validate_login_data(input_data) -> Result:
        # Validate login data
        if not input_data["username"] or not isinstance(input_data["username"], str):
            return Result(
                success=False,
                error="Username is required",
                error_code=400,
            )

        validation_result = UserValidator.validate_password(input_data["password"])
        if not validation_result.success:
            return validation_result

        return Result(success=True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _validate_token(input_data) -> Result:
        # Check authentication
        auth_result = UserValidator.check_authentication(input_data["current_user"])
        if not auth_result.success:
            return auth_result

        return Result(success=True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _handle_register(input_data) -> Result:
        username = input_data["username"]
        email = input_data["email"]
        password = input_data["password"]

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return Result(
                success=False,
                error="Username already exists",
                error_code=400,
            )
        if User.query.filter_by(email=email).first():
            return Result(
                success=False,
                error="Email already exists",
                error_code=400,
            )

        new_user = User(
            username=username,
            email=email,
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.flush()

        try:
            send_confirmation_email(new_user)
        except Exception as e:
            db.session.rollback()
            return Result(
                success=False,
                error="Failed to send confirmation email",
                error_code=500,
            )

        return Result(success=True, data={"user": new_user})

    @staticmethod
    @BaseService._handle_errors
    def _handle_login(input_data) -> Result:
        identity = input_data["username"]
        password = input_data["password"]

        user = User.query.filter(
            (User.username == identity) | (User.email == identity.lower())
        ).first()

        if not user or not user.check_password(password):
            return Result(
                success=False,
                error="Invalid username/email or password",
                error_code=401,
            )

        if not user.email_confirmed:
            return Result(
                success=False,
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
        return Result(success=True, data=input_data)

    @staticmethod
    @BaseService._handle_errors
    def _handle_confirm(input_data) -> Result:
        current_user = input_data["current_user"]
        token = input_data["token"]

        if current_user.email_confirmed:
            return Result(
                success=False,
                error="Email is already confirmed",
                error_code=400,
            )

        if not current_user.verify_token(token):
            return Result(
                success=False,
                error="Invalid or expired token",
                error_code=400,
            )

        current_user.email_confirmed = True
        db.session.commit()

        return Result(success=True, data={"user": current_user})

    @staticmethod
    def _send_register_data(input_data) -> Result:
        user = input_data["user"]
        return Result(
            success=True,
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "email_confirmed": user.email_confirmed,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "message": "Registration successful. Please check your email to confirm your account.",
            },
        )

    @staticmethod
    def _send_login_data(input_data) -> Result:
        user = input_data["user"]
        return Result(
            success=True,
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

    @staticmethod
    def _send_confirmation_data(input_data) -> Result:
        user = input_data["user"]
        return Result(
            success=True,
            data={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "email_confirmed": user.email_confirmed,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "message": "Email confirmed successfully",
            },
        )
