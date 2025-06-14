from app.services.base_service import Result
from app.models import User
import re


class UserValidator:
    @staticmethod
    def validate_user_data(username, email, password=None, current_user=None) -> Result:
        """Validate user data including username, email, and optionally password."""
        if (
            not username
            or not isinstance(username, str)
            or not (3 <= len(username) <= 32)
        ):
            return Result(
                success=False,
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
            return Result(
                success=False,
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

        return Result(success=True)

    @staticmethod
    def validate_password(password, current_user=None) -> Result:
        """Validate password format and optionally check against current user's password."""
        if not password or not isinstance(password, str) or len(password) < 8:
            return Result(
                success=False,
                error="Password must be at least 8 characters",
                error_code=400,
            )

        # Check password complexity
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

        if current_user and not current_user.check_password(password):
            return Result(
                success=False,
                error="Current password is incorrect",
                error_code=400,
            )

        return Result(success=True)

    @staticmethod
    def check_authentication(current_user) -> Result:
        """Check if user is authenticated."""
        print("current", current_user)
        if current_user is None:
            return Result(
                success=False,
                error="User must be authenticated",
                error_code=401,
            )
        if not current_user.is_authenticated:
            return Result(
                success=False,
                error="User must be authenticated",
                error_code=401,
            )
        return Result(success=True)
