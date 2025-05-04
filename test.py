from flask_mail import Message
from app.extensions import mail
from app import create_app

app = create_app()
with app.app_context():
    msg = Message("Тест Gmail SMTP", recipients=["lynxvs66@gmail.com"])
    msg.body = "Если это письмо пришло — соединение с Gmail SMTP настроено верно!"
    mail.send(msg)
