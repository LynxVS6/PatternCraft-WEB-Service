from app.extensions import db
from itsdangerous import URLSafeTimedSerializer
from ...ropp_service import Result
from flask import current_app
from app.models import User


class ConfirmEmail:
    @staticmethod
    def validate_token(input_data) -> Result:
        token = input_data["token"]

        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = s.loads(
                token,
                salt=current_app.config["SECURITY_PASSWORD_SALT"],
                max_age=36000,
            )
        except Exception:
            return Result.fail(error="Invalid token", error_code=400)
        input_data.update({"email": email})
        return Result.ok(input_data)

    @staticmethod
    def validate_user(input_data) -> Result:
        email = input_data["email"]

        # Find unconfirmed user
        user = User.query.filter_by(email=email, email_confirmed=False).first()

        if not user:
            return Result.fail(
                error="User not found",
                error_code=400,
            )
        if user.email_confirmed:
            return Result.fail(
                error="Email is already confirmed",
                error_code=400,
            )
        print(f"Found user: {user.username} with email: {user.email}")
        return Result.ok({"user": user})

    @staticmethod
    def execute(input_data) -> Result:
        user = input_data["user"]
        user.email_confirmed = True
        db.session.commit()
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
                "message": "E‑mail подтверждён! Добро пожаловать 👋",
            },
        )
