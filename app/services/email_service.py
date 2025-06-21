from flask_mail import Message
from flask import current_app, url_for

from app.extensions import mail
from app.utils.tokens import generate_confirmation_token


def send_confirmation_email(user):
    try:
        token = generate_confirmation_token(user.email)
        confirm_url = url_for("auth.confirm_email", token=token, _external=True)

        msg = Message(
            "Подтверждение аккаунта - PatternCraft Lab",
            recipients=[user.email],
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
        )
        msg.body = f"""
Здравствуйте, {user.username}!

Для подтверждения вашего аккаунта в PatternCraft Lab, пожалуйста, перейдите по следующей ссылке:

{confirm_url}

Если вы не регистрировались в PatternCraft Lab, просто проигнорируйте это письмо.

С уважением,
Команда PatternCraft Lab
        """

        current_app.logger.info(
            f"Attempting to send confirmation email to {user.email}"
        )
        current_app.logger.info(
            f"Email settings: server={current_app.config.get('MAIL_SERVER')}, "
            f"port={current_app.config.get('MAIL_PORT')}, "
            f"username={current_app.config.get('MAIL_USERNAME')}"
        )

        mail.send(msg)
        current_app.logger.info(f"Successfully sent confirmation email to {user.email}")

    except Exception as e:
        current_app.logger.error(
            f"Failed to send confirmation email to {user.email}: {str(e)}"
        )
        raise e
