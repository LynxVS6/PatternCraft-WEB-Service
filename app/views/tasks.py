from flask import Blueprint, jsonify, request
from app.models import Problem, Solution, User
from app.extensions import db
from flask_login import current_user, login_required
from sqlalchemy import select, cast, String
import json

bp = Blueprint("tasks", __name__)


@bp.route("/api/filter-tasks", methods=["POST"])
def filter_tasks():
    data = request.get_json()
    if not current_user.is_authenticated:
        return jsonify({"error": "User must be authenticated"}), 401

    if not data or "lab_ids" not in data or "tags_json" not in data:
        return jsonify({"error": "Invalid request format"}), 400

    lab_ids = data["lab_ids"]
    tags_json = data["tags_json"]

    query = Problem.query

    if tags_json:
        tags_str = json.dumps(tags_json)
        query = query.filter(cast(Problem.tags_json, String) == tags_str)

    if lab_ids:
        query = query.filter(~Problem.id.in_(lab_ids))

    if current_user.is_authenticated:
        solved_problems = select(Solution.problem_id).where(
            Solution.user_id == current_user.id
        )
        query = query.filter(~Problem.id.in_(solved_problems))

    problems = query.all()
    result = [
        {
            "id": problem.id,
            "name": problem.name,
            "description": problem.description,
            "tags_json": problem.tags_json,
            "difficulty": problem.difficulty,
            "language": problem.language,
            "status": problem.status,
            "author_id": problem.author_id,
            "bookmark_count": problem.bookmark_count,
            "positive_vote": problem.positive_vote,
            "negative_vote": problem.negative_vote,
            "neutral_vote": problem.neutral_vote,
            "total_votes": problem.total_votes,
            "satisfaction_percent": problem.satisfaction_percent,
            "created_at": (
                problem.created_at.isoformat() if problem.created_at else None
            ),
        }
        for problem in problems
    ]

    return jsonify(result)


@bp.route("/api/create-task", methods=["POST"])
def create_task():
    if not current_user.is_authenticated:
        return jsonify({"error": "User must be authenticated"}), 401

    data = request.get_json()

    # Handle both single object and list of objects
    if not isinstance(data, list):
        data = [data]

    results = []
    for item in data:
        if (
            not item
            or "name" not in item
            or "description" not in item
            or "tags_json" not in item
            or "difficulty" not in item
            or "language" not in item
            or "status" not in item
        ):
            return jsonify({"error": "Invalid request format"}), 400

        user = User.query.get(current_user.id)
        if not user:
            return jsonify({"error": f"Author with ID {item['author_id']} not found"}), 400

        new_problem = Problem(
            name=item["name"],
            description=item["description"],
            tags_json=item["tags_json"],
            difficulty=item["difficulty"],
            language=item["language"],
            status=item["status"],
            author_id=user.id,  # Use the actual user ID
        )

        db.session.add(new_problem)
        db.session.flush()
        results.append(
            {
                "id": new_problem.id,
                "name": new_problem.name,
                "description": new_problem.description,
                "tags_json": new_problem.tags_json,
                "difficulty": new_problem.difficulty,
                "language": new_problem.language,
                "status": new_problem.status,
                "author_id": new_problem.author_id,
                "bookmark_count": new_problem.bookmark_count,
                "created_at": (
                    new_problem.created_at.isoformat()
                    if new_problem.created_at
                    else None
                ),
            }
        )

    db.session.commit()
    return jsonify(results), 201


@bp.route("/api/submit-solution", methods=["POST"])
def submit_solution():
    data = request.get_json()

    # Handle both single object and list of objects
    if not isinstance(data, list):
        data = [data]

    results = []
    for item in data:
        if not item or "server_problem_id" not in item or "solution" not in item:
            return jsonify({"error": "Invalid request format"}), 400

        if not current_user.is_authenticated:
            return jsonify({"error": "User must be authenticated"}), 401

        problem_id = item["server_problem_id"]
        solution = item["solution"]

        problem = Problem.query.get(problem_id)
        if not problem:
            return jsonify({"error": f"Problem {problem_id} not found"}), 404

        user_id = current_user.id

        new_solution = Solution(
            user_id=user_id,
            problem_id=problem_id,
            solution=solution
        )

        db.session.add(new_solution)
        results.append(
            {
                "id": new_solution.id,
                "solution": new_solution.solution,
                "user": {"id": user_id, "username": User.query.get(user_id).username},
                "problem": {
                    "id": problem.id,
                    "name": problem.name,
                    "difficulty": problem.difficulty,
                },
                "likes_count": new_solution.likes_count,
                "comments": [],
                "created_at": (
                    new_solution.created_at.isoformat()
                    if hasattr(new_solution, "created_at")
                    else None
                ),
            }
        )

    db.session.commit()
    return jsonify(results), 201
