from flask_mail import Message
from flask import current_app, url_for

from app.extensions import mail
from app.utils.tokens import generate_confirmation_token


def send_confirmation_email(user):
    token = generate_confirmation_token(user.email)
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    msg = Message("Confirm your account", recipients=[user.email])
    msg.body = f"Please click the link to confirm: {confirm_url}"
    current_app.logger.info("Send mail to %s", user.email)
    mail.send(msg)
