from flask import Blueprint, render_template, abort
from datetime import datetime

courses_bp = Blueprint('courses', __name__, url_prefix='/courses')

courses_data = [
    {
        "id": 1,
        "title": "Введение в программирование",
        "author": "Иван Иванов",
        "created_at": datetime(2025, 1, 10),
        "description": "Курс для начинающих по основам программирования.",
        "tasks": ["Изучить переменные", "Написать первую программу", "Понять циклы"],
        "materials": ["Видео лекции", "Презентации", "Практические задания"],
        "image_url": "/static/img/course1.jpg"
    },
    {
        "id": 2,
        "title": "Веб-разработка с JavaScript",
        "author": "Анна Смирнова",
        "created_at": datetime(2025, 5, 15),
        "description": "Создавайте современные веб-приложения с JavaScript!",
        "tasks": ["Создать интерактивную страницу", "Разработать TODO-приложение", "Интегрировать API"],
        "materials": ["Видеоуроки (12 часов)", "Шпаргалка по JS", "Практические задания"],
        "image_url": "/static/img/js-course.jpg"
    }
]

@courses_bp.route('/catalog')
def catalog():
    return render_template('courses/catalog.html', courses=courses_data)

@courses_bp.route('/<int:course_id>')
def detail(course_id):
    course = next((c for c in courses_data if c['id'] == course_id), None)
    if course is None:
        abort(404)
    return render_template('courses/course.html', course=course)
