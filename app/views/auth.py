from urllib.parse import urljoin, urlparse
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from app.forms.forms import LoginForm, RegistrationForm
from app.services.auth_service import AuthService

bp = Blueprint("auth", __name__)


def is_safe_url(target: str) -> bool:
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


@bp.route("/confirm-email/<token>")
def confirm_email(token):
    if (
        current_user.is_authenticated
        and current_user.email_confirmed
        and not current_user.new_email
    ):
        return redirect(url_for("main.index"))

    result = AuthService.confirm_email(token)

    if not result.success:
        flash(result.error, "error")
        return redirect(url_for("auth.login"))
    else:
        flash(result.data["message"], "success")

    user = result.data["user"]
    login_user(user, remember=True)
    return redirect(url_for("main.index"))


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    register_form = RegistrationForm(prefix="register")
    login_form = LoginForm(prefix="login")
    print(request.method == "POST", register_form.validate_on_submit())

    if not register_form.validate_on_submit():
        flash("Invalid register form! Please check it again.", "error")
        redirect(url_for("auth.register"))

    if request.method == "POST" and register_form.validate_on_submit():
        result = AuthService.register(
            {
                "username": register_form.username.data,
                "email": register_form.email.data,
                "password": register_form.password.data,
            },
            current_user,
        )

        if not result.success:
            flash(result.error, "error")
        else:
            flash(result.data["message"], "info")
            return redirect(url_for("auth.login"))

    return render_template(
        "auth.html", login_form=login_form, register_form=register_form
    )


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    login_form = LoginForm(prefix="login")
    register_form = RegistrationForm(prefix="register")

    if request.method == "POST":
        if "login" in request.form and login_form.validate_on_submit():
            result = AuthService.login(
                {
                    "identity": login_form.identity.data,
                    "password": login_form.password.data,
                    "remember_me": login_form.remember_me.data,
                },
                current_user,
            )

            if not result.success:
                flash(result.error, "error")
            else:
                user = result.data["user"]
                login_user(user, remember=login_form.remember_me.data)
                flash("Успешный вход в аккаунт!", "success")
                next_page = request.args.get("next")
                return (
                    redirect(next_page)
                    if next_page and is_safe_url(next_page)
                    else redirect(url_for("main.index"))
                )
        elif "register" in request.form and register_form.validate_on_submit():
            result = AuthService.register(
                {
                    "username": register_form.username.data,
                    "email": register_form.email.data,
                    "password": register_form.password.data,
                },
                current_user,
            )

            if not result.success:
                flash(result.error, "error")
            else:
                flash(result.data["message"], "info")
                return redirect(url_for("auth.login"))

    return render_template(
        "auth.html", login_form=login_form, register_form=register_form
    )


@bp.route("/api/login", methods=["POST"])
def api_login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    login_form = LoginForm(prefix="login")

    if login_form.validate_on_submit():
        result = AuthService.login(
            {
                "identity": login_form.identity.data,
                "password": login_form.password.data,
                "remember_me": login_form.remember_me.data,
            },
            current_user,
        )

        if not result.success:
            return jsonify({"error": result.error}), result.error_code
        else:
            user = result.data["user"]
            login_user(user, remember=login_form.remember_me.data)

            return jsonify({"id": result.data["id"]})
    else:
        return jsonify(
            {"message": "Login failed... Please check your login form again"}
        )


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы успешно вышли из системы", "info")
    return redirect(url_for("main.index"))
