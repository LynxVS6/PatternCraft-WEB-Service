from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.forms.forms import EditProfileForm, ChangePasswordForm

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
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Профиль успешно обновлён!", "success")
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
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Пароль успешно изменён!", "success")
            return redirect(url_for("users.account"))
        else:
            flash("Неверный текущий пароль", "error")
    return render_template("change_password.html", form=form)
