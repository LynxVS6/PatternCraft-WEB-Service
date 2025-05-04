from datetime import datetime
from urllib.parse import urljoin, urlparse
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import or_
from app.extensions import db
from app.forms.forms import LoginForm, RegistrationForm
from app.models.user import User
from app.utils.tokens import confirm_token
from app.services.email_service import send_confirmation_email
from flask_login import current_user, login_required, login_user, logout_user

bp = Blueprint("auth", __name__)


def is_safe_url(target: str) -> bool:
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ("http", "https")
        and ref_url.netloc == test_url.netloc
    )


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    register_form = RegistrationForm(prefix="register")
    login_form = LoginForm(prefix="login")

    if request.method == "POST" and register_form.validate_on_submit():
        if User.query.filter_by(username=register_form.username.data).first():
            flash("Такой ник уже занят", "error")
        elif User.query.filter_by(email=register_form.email.data).first():
            flash("Такой email уже зарегистрирован", "error")
        else:
            user = User(
                username=register_form.username.data.strip(),
                email=register_form.email.data.lower().strip()
            )
            user.set_password(register_form.password.data)
            db.session.add(user)
            db.session.commit()

            send_confirmation_email(user)
            flash("Проверьте почту и подтвердите регистрацию", "info")
            return redirect(url_for("auth.login"))

    return render_template("auth.html",
                           login_form=login_form,
                           register_form=register_form)


@bp.route("/confirm/<token>")
def confirm_email(token):
    if current_user.is_authenticated and current_user.email_confirmed:
        return redirect(url_for("main.index"))

    email = confirm_token(token)
    if not email:
        flash("Ссылка просрочена или недействительна", "error")
        return redirect(url_for("auth.login_page"))

    user = User.query.filter_by(email=email).first_or_404()

    if not user.email_confirmed:
        user.email_confirmed = True
        user.email_confirmed_at = datetime.utcnow()
        db.session.commit()
        flash("E‑mail подтверждён! Добро пожаловать 👋", "success")
    else:
        flash("Почта уже была подтверждена", "info")

    login_user(user, remember=True)
    return redirect(url_for("main.index"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    login_form = LoginForm(prefix="login")
    register_form = RegistrationForm(prefix="register")

    if request.method == "POST" and login_form.validate_on_submit():
        user = User.query.filter(
            or_(User.username == login_form.identity.data,
                User.email == login_form.identity.data.lower())
        ).first()

        if user and user.check_password(login_form.password.data):
            if not user.email_confirmed:
                flash("Сначала подтвердите e‑mail", "error")
            else:
                login_user(user, remember=login_form.remember_me.data)
                user.last_login = datetime.utcnow()
                db.session.commit()

                next_page = request.args.get("next")
                return redirect(next_page) if next_page and is_safe_url(next_page) \
                    else redirect(url_for("main.index"))
        else:
            flash("Неверный логин/email или пароль", "error")

    return render_template("auth.html",
                           login_form=login_form,
                           register_form=register_form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы успешно вышли из системы", "info")
    return redirect(url_for("main.index"))
