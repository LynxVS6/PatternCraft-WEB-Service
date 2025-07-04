from flask import Flask
from .settings import settings
from .extensions import (
    db,
    migrate,
    mail,
    login_manager,
    babel,
    csrf,
    get_timezone,
    get_locale,
)
from .views import auth, main, problem_hub, problem_page, users, tasks, courses, theories


def monthyearformat(value):
    if not value:
        return ""
    return value.strftime("%B %Y")  # Например: "Июнь 2025"


def create_app():
    app = Flask(__name__)
    app.config.from_object(settings)

    db.init_app(app)
    babel.init_app(app, locale_selector=get_locale, timezone_selector=get_timezone)
    migrate.init_app(app, db)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Регистрируем фильтр для Jinja2
    app.jinja_env.filters["monthyearformat"] = monthyearformat

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(problem_hub.bp)
    app.register_blueprint(tasks.bp)
    app.register_blueprint(problem_page.bp)
    app.register_blueprint(courses.courses_bp)
    app.register_blueprint(theories.bp)

    return app
