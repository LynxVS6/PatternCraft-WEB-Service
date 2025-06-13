from flask import Blueprint, render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.forms.forms import EditProfileForm, ChangePasswordForm
from app.services.auth_service import AuthService
from app.services.user_service import UserService

bp = Blueprint("users", __name__)


@bp.route("/account")
@login_required
def account():
    return render_template("account.html")


@bp.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        result = UserService.edit_profile(
            {
                "username": form.username.data,
                "email": form.email.data,
            },
            current_user,
        )

        if not result.success:
            flash(result.error, "error")
            return render_template("edit_profile.html", form=form)

        flash(result.data["message"], "success")
        return redirect(url_for("users.account"))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template("edit_profile.html", form=form)


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        result = UserService.change_password(
            {
                "current_password": form.current_password.data,
                "new_password": form.new_password.data,
            },
            current_user,
        )

        if not result.success:
            flash(result.error, "error")
        else:
            flash(result.data["message"], "success")
            return redirect(url_for("users.account"))

    return render_template("change_password.html", form=form)


@bp.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()

    # Handle both single object and list of objects
    if not isinstance(data, list):
        data = [data]

    results = []
    for item in data:
        result = AuthService.register(item)
        if not result.success:
            return jsonify({"error": result.error}), result.error_code

        results.append(
            {
                "id": result.data["user"].id,
                "username": result.data["user"].username,
                "email": result.data["user"].email,
                "email_confirmed": result.data["user"].email_confirmed,
                "created_at": (
                    result.data["user"].created_at.isoformat()
                    if result.data["user"].created_at
                    else None
                ),
            }
        )

    return jsonify(results), 201
