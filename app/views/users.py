from flask import Blueprint, render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.forms.forms import EditProfileForm, ChangePasswordForm
from app.models.user import User
from app.services.email_service import send_confirmation_email
from app.utils.validators import validate_user_data

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
        if form.username.data != current_user.username:
            if User.query.filter_by(username=form.username.data).first():
                flash("Этот логин уже занят", "error")
                return render_template("edit_profile.html", form=form)
            current_user.username = form.username.data

        if form.email.data != current_user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash("Этот email уже зарегистрирован", "error")
                return render_template("edit_profile.html", form=form)

            current_user.new_email = form.email.data
            db.session.commit()

            send_confirmation_email(current_user)
            flash("На новый email отправлено письмо для подтверждения", "info")
        else:
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


@bp.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()

    # Handle both single object and list of objects
    if not isinstance(data, list):
        data = [data]

    results = []
    for item in data:
        is_valid, error = validate_user_data(item)
        if not is_valid:
            return jsonify({"error": error}), 400
        if not item or "username" not in item or "email" not in item:
            return jsonify({"error": "Invalid request format"}), 400

        # Check if username or email already exists
        if User.query.filter_by(username=item["username"]).first():
            return jsonify({"error": f"Username {item['username']} already exists"}), 400
        if User.query.filter_by(email=item["email"].lower()).first():
            return jsonify({"error": f"Email {item['email']} already exists"}), 400

        # Create new user
        new_user = User(
            username=item["username"].strip(),
            email=item["email"].lower().strip(),
            email_confirmed=False  # Default to False
        )

        if "password" not in item:
            return jsonify({"error": "Password is required"}), 400

        new_user.set_password(item["password"])

        db.session.add(new_user)
        db.session.flush()  # This will assign an ID without committing

        results.append({
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "email_confirmed": new_user.email_confirmed,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None
        })

        send_confirmation_email(new_user)

    db.session.commit()
    return jsonify(results), 201
