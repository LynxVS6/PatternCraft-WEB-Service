from flask import Blueprint, render_template, redirect, url_for

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/change_language/<language_code>")
def change_language(language_code):
    lang_codes = {'en': 'English', 'ru': 'Русский'}
    return redirect(url_for("main.index"))
