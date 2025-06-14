from ..ropp_service import Result
import re
from app.models import User


class UserDataMixin:
    @staticmethod
    def validate_user_data(input_data) -> Result:
        """Validate user data including username, email, and optionally password."""
        username = input_data["username"]
        email = input_data["email"]
        password = input_data.get("password")
        current_user = input_data["current_user"]
        if (
            not username
            or not isinstance(username, str)
            or not (3 <= len(username) <= 32)
        ):
            return Result.fail(
                error="Username must be a string between 3 and 32 characters",
                error_code=400,
            )

        # Validate email format
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if (
            not email
            or not isinstance(email, str)
            or not re.match(email_pattern, email)
        ):
            return Result.fail(
                error="Valid email is required",
                error_code=400,
            )

        if password is not None:
            # Validate password complexity
            if not password or not isinstance(password, str) or len(password) < 8:
                return Result(
                    success=False,
                    error="Password must be at least 8 characters",
                    error_code=400,
                )
            if not re.search(r"[A-Z]", password):
                return Result(
                    success=False,
                    error="Password must contain at least one uppercase letter",
                    error_code=400,
                )
            if not re.search(r"[a-z]", password):
                return Result(
                    success=False,
                    error="Password must contain at least one lowercase letter",
                    error_code=400,
                )
            if not re.search(r"\d", password):
                return Result(
                    success=False,
                    error="Password must contain at least one number",
                    error_code=400,
                )

        # Check uniqueness only if we're not updating the current user
        if current_user is None:
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
        else:
            # For updates, check uniqueness excluding current user
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != current_user.id:
                return Result(
                    success=False,
                    error="Username already exists",
                    error_code=400,
                )

            existing_email = User.query.filter_by(email=email).first()
            if existing_email and existing_email.id != current_user.id:
                return Result(
                    success=False,
                    error="Email already exists",
                    error_code=400,
                )

        return Result.ok(input_data)
