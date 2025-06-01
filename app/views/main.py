from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/creational")
def creational():
    return render_template("main.html")


@bp.route("/structural")
def structural():
    return render_template("main.html")


@bp.route("/behavioral")
def behavioral():
    return render_template("main.html")
