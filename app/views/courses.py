from flask import Blueprint, render_template, abort
from app.models.course import Course


courses_bp = Blueprint('courses', __name__, url_prefix='/courses')


@courses_bp.route('/catalog')
def catalog():
    courses = Course.query.filter_by(status='active', is_hidden=False).order_by(Course.created_at.desc()).all()
    return render_template('courses/catalog.html', courses=courses)


@courses_bp.route('/<int:course_id>')
def detail(course_id):
    course = Course.query.filter_by(id=course_id, status='active', is_hidden=False).first()
    if course is None:
        abort(404)
    return render_template('courses/course.html', course=course)
