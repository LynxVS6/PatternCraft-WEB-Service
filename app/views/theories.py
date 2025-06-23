from flask import Blueprint, jsonify, request
from flask_login import current_user

from .. import db
from app.services.theory_service import TheoryService
from app.services.solution_service import SolutionService
from app.models import Theory
import base64


bp = Blueprint("theories", __name__)


@bp.route("/api/create-theory", methods=["POST"])
def create_task():
    data = request.get_json()

    result = TheoryService.create_theory(data, current_user)
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data), 201


@bp.route("/api/theories/<int:theory_id>", methods=["GET"])
def get_theory(theory_id):
    theory = db.session.get(Theory, theory_id)

    if not theory:
        return jsonify({"error": "Theory not found"}), 404
    
    if theory.image_url:
        image = theory.image_url
    else:
        with open(f"app/static/img/theories/{theory.id}.png", "rb") as image_file:
            image = "data:image/png;base64," + base64.b64encode(image_file.read()).decode("utf-8")

    return jsonify(
        {
            "id": theory.id,
            "name": theory.name,
            "description": theory.description,
            "content": theory.content,
            "image": image,
            "author_id": theory.author_id,
            "created_at": theory.created_at.strftime("%Y-%m-%d %H:%M"),
        }
    )