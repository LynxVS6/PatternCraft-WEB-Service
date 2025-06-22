from app.extensions import db
from ...ropp_service import Result
from ...mixins import UserDataMixin
from ...email_service import send_confirmation_email
from app.models import User


class RegisterUser(UserDataMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        input_data.update(raw_json)
        return Result.ok(input_data)

    @staticmethod
    def execute(input_data) -> Result:
        username = input_data["username"]
        email = input_data["email"]
        password = input_data["password"]

        if User.query.filter_by(username=username).first():
            return Result.fail(
                error="Username already exists",
                error_code=400,
            )
        if User.query.filter_by(email=email).first():
            return Result.fail(
                error="Email already exists",
                error_code=400,
            )

        new_user = User(
            username=username,
            email=email,
        )
        new_user.set_password(password)
        print(f"Creating user: {new_user.username}, {new_user.email}")
        db.session.add(new_user)

        try:
            db.session.flush()

            send_confirmation_email(new_user)

            db.session.commit()
            print(
                f"User {new_user.username} registered successfully and confirmation email sent"
            )

        except Exception as e:
            db.session.rollback()
            print(f"Error during registration: {str(e)}")
            return Result.fail(
                error=f"Registration failed: {str(e)}",
                error_code=500,
            )

        return Result.ok({"user": new_user})

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
                "message": "Registration successful. Please check your email to confirm your account.",
            },
        )
