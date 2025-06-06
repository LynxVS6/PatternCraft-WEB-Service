from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_login import LoginManager
from flask_babel import Babel
from flask import g, request
from flask_wtf.csrf import CSRFProtect


def get_locale():
    user = getattr(g, "user", None)
    if user is not None:
        return user.locale

    language = request.accept_languages.best_match(["ru", "en"])
    return language


def get_timezone():
    user = getattr(g, "user", None)
    if user is not None:
        return user.timezone


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
babel = Babel()
csrf = CSRFProtect()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Пожалуйста, войдите для доступа к этой странице."
login_manager.login_message_category = "info"
