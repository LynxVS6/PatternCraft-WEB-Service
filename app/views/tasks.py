from flask import Blueprint, jsonify, request
from app.models import Problem, Solution
from app.extensions import db
from flask_login import current_user
from sqlalchemy import select, cast, String
import json

bp = Blueprint('tasks', __name__)


@bp.route('/api/filter-tasks', methods=['POST'])
def filter_tasks():
    data = request.get_json()

    if not data or 'lab_ids' not in data or 'tags_json' not in data:
        return jsonify({'error': 'Invalid request format'}), 400

    lab_ids = data['lab_ids']
    tags_json = data['tags_json']

    query = Problem.query

    if tags_json:
        tags_str = json.dumps(tags_json)
        query = query.filter(cast(Problem.tags_json, String) == tags_str)

    if lab_ids:
        query = query.filter(~Problem.id.in_(lab_ids))

    if current_user.is_authenticated:
        solved_problems = select(Solution.problem_id).where(
            Solution.user_id == current_user.id)
        query = query.filter(~Problem.id.in_(solved_problems))

    problems = query.all()
    result = [{
        'id': problem.id,
        'name': problem.name,
        'description': problem.description,
        'tags_json': problem.tags_json
    } for problem in problems]

    return jsonify(result)


@bp.route('/api/create-task', methods=['POST'])
def create_task():
    data = request.get_json()

    if not data or 'name' not in data or 'description' not in data or 'tags_json' not in data:
        return jsonify({'error': 'Invalid request format'}), 400

    new_problem = Problem(
        name=data['name'],
        description=data['description'],
        tags_json=data['tags_json']
    )

    db.session.add(new_problem)
    db.session.commit()

    return jsonify({'id': new_problem.id}), 201


@bp.route('/api/submit-solution', methods=['POST'])
def submit_solution():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User must be authenticated'}), 401

    data = request.get_json()

    if not data or 'server_problem_id' not in data or 'solution' not in data:
        return jsonify({'error': 'Invalid request format'}), 400

    problem_id = data['server_problem_id']
    solution = data['solution']

    problem = Problem.query.get(problem_id)
    if not problem:
        return jsonify({'error': 'Problem not found'}), 404

    new_solution = Solution(
        user_id=current_user.id,
        problem_id=problem_id,
        solution=solution
    )

    db.session.add(new_solution)
    db.session.commit()

    return jsonify({'message': 'Solution submitted successfully'}), 201
