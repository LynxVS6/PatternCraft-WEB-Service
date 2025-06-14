from ..ropp_service import Result
import re


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

    return Result.ok()
