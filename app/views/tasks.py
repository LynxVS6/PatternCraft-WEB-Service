from flask import Blueprint, jsonify, request
from flask_login import current_user
from app.services.problem_service import ProblemService
from app.services.solution_service import SolutionService
from app.models import Problem


bp = Blueprint("tasks", __name__)


@bp.route("/api/filter-tasks", methods=["POST"])
def filter_tasks():
    data = request.get_json()
    result = ProblemService.filter_problems_api(data, current_user)

    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data["problems"])


@bp.route("/api/create-task", methods=["POST"])
def create_task():
    data = request.get_json()

    result = ProblemService.create_problem(data, current_user)
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data), 201


@bp.route("/api/submit-solution", methods=["POST"])
def submit_solution():
    data = request.get_json()

    result = SolutionService.submit_solution(Problem, data["server_problem_id"], data, current_user)
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data), 201
