from flask import Blueprint, request
from app.extensions import db
from app.models.user import User
from app.utils.tokens import confirm_token
from app.services.email_service import send_confirmation_email
from flask_login import login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return {"error": "email and password required"}, 400
    if User.query.filter_by(email=email).first():
        return {"error": "email exists"}, 409

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    send_confirmation_email(user)
    return {"message": "registered, check email"}, 201


@auth_bp.route("/confirm/<token>")
def confirm_email(token):
    email = confirm_token(token)
    if not email:
        return {"error": "token invalid or expired"}, 400
    user = User.query.filter_by(email=email).first_or_404()
    if user.email_confirmed:
        return {"message": "already confirmed"}
    user.email_confirmed = True
    db.session.commit()
    return {"message": "email confirmed"}


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not user.check_password(data.get("password")):
        return {"error": "invalid creds"}, 401
    if not user.email_confirmed:
        return {"error": "email not confirmed"}, 403
    login_user(user)
    return {"message": "logged in"}
