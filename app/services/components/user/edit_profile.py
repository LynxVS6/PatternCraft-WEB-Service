from app.extensions import db
from ...ropp_service import Result
from ...email_service import send_confirmation_email
from ...mixins import AuthenticationMixin, UserDataMixin


class EditProfile(AuthenticationMixin, UserDataMixin):
    @staticmethod
    def parse_json(input_data):
        raw_json = input_data["raw_json"]
        input_data.update(raw_json)
        return Result.ok(input_data)

    @staticmethod
    def execute(input_data) -> Result:
        print("-"*100, input_data)
        current_user = input_data["current_user"]
        username = input_data["username"]
        email = input_data["email"]
        print("-"*100)
        if username != current_user.username:
            current_user.username = username

        if email != current_user.email:
            current_user.email = email
            current_user.email_confirmed = False

            send_confirmation_email(current_user)

        db.session.commit()
        return Result.ok({"current_user": current_user})

    @staticmethod
    def format(input_data) -> Result:
        current_user = input_data["current_user"]
        message = "Profile updated successfully"
        if not current_user.email_confirmed:
            message += ". Please check your email to confirm your new email address."

        return Result.ok(
            data={
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "email_confirmed": current_user.email_confirmed,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                "message": message,
            },
        )
