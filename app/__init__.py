from flask import Flask
from .settings import settings
from .extensions import (
    db,
    migrate,
    mail,
    login_manager,
    babel,
    get_timezone,
    get_locale,
)
from .views import auth, main, users, solved_problems, tasks, problems


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    db.init_app(app)
    babel.init_app(app, locale_selector=get_locale, timezone_selector=get_timezone)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(solved_problems.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(problems.bp)

    return app
