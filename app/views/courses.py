from flask import Blueprint, render_template, abort, jsonify, request
from app.models.course import Course
from app.services import CourseService
from flask_login import current_user


courses_bp = Blueprint('courses', __name__, url_prefix='/courses')


@courses_bp.route('/catalog')
def catalog():
    courses = Course.query.filter_by(status='active', is_hidden=False).order_by(Course.created_at.desc()).all()
    return render_template('catalog.html', courses=courses)


@courses_bp.route('/<int:course_id>')
def detail(course_id):
    course = Course.query.filter_by(id=course_id, status='active', is_hidden=False).first()
    if course is None:
        abort(404)
    return render_template('course.html', course=course)


@courses_bp.route('/api/<int:course_id>/download', methods=['GET'])
def download_course(course_id):
    """Get full course information for download (theories and problems only)"""
    try:
        course = Course.query.filter_by(id=course_id, status='active', is_hidden=False).first()
        if course is None:
            return jsonify({'error': 'Course not found'}), 404

        course_data = {
            'id': course.id,
            'name': course.name,
            'description': course.description,
            'image_url': course.image_url,
            'server_course_id': course.server_course_id,
            'created_at': course.created_at.isoformat() if course.created_at else None,
            'updated_at': course.updated_at.isoformat() if course.updated_at else None,
            'creator': {
                'id': course.creator.id,
                'username': course.creator.username
            } if course.creator else None,
            'problems': [],
            'theories': []
        }

        for problem in course.problems:
            problem_data = {
                'id': problem.id,
                'name': problem.name,
                'description': problem.description,
                'tags_json': problem.tags_json,
                'tests': problem.tests,
                'difficulty': problem.difficulty,
                'language': problem.language,
                'status': problem.status,
                'created_at': problem.created_at.isoformat() if problem.created_at else None,
                'author': {
                    'id': problem.author.id,
                    'username': problem.author.username
                } if problem.author else None
            }
            course_data['problems'].append(problem_data)

        for theory in course.theories:
            theory_data = {
                'id': theory.id,
                'name': theory.name,
                'content': theory.content,
                'description': theory.description,
                'image_url': theory.image_url,
                'in_practice': theory.in_practice,
                'status': theory.status,
                'created_at': theory.created_at.isoformat() if theory.created_at else None,
                'updated_at': theory.updated_at.isoformat() if theory.updated_at else None,
                'author': {
                    'id': theory.author.id,
                    'username': theory.author.username
                } if theory.author else None
            }
            course_data['theories'].append(theory_data)

        return jsonify(course_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@courses_bp.route('/api/create_course', methods=['POST'])
def create_course():
    data = request.get_json()

    result = CourseService.create_course(data, current_user)
    if not result.success:
        return jsonify({"error": result.error}), result.error_code

    return jsonify(result.data), 201
