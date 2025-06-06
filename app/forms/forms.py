import re
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
    SelectField,
    SelectMultipleField,
)
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from app.models.user import User

languages = [
    {"code": "python", "name": "Python"},
    {"code": "java", "name": "Java"},
    {"code": "javascript", "name": "JavaScript"},
    {"code": "cplusplus", "name": "C++"},
    {"code": "csharp", "name": "C#"},
]

available_tags = [
    "Factory Method",
    "Abstract Factory",
    "Builder",
    "Prototype",
    "Singleton",
    "Adapter",
    "Bridge",
    "Composite",
    "Decorator",
    "Facade",
    "Flyweight",
    "Proxy",
    "Chain of Responsibility",
    "Command",
    "Interpreter",
    "Iterator",
    "Mediator",
    "Memento",
    "Observer",
    "State",
    "Strategy",
    "Template Method",
    "Visitor",
    "SRP",
    "OCP",
    "LSP",
    "ISP",
    "DIP",
]


def password_complexity_check(form, field):
    password = field.data
    if not re.search(r"[A-Z]", password):
        raise ValidationError("Пароль должен содержать хотя бы одну заглавную букву")
    if not re.search(r"[0-9]", password):
        raise ValidationError("Пароль должен содержать хотя бы одну цифру")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValidationError("Пароль должен содержать хотя бы один спецсимвол")


class LoginForm(FlaskForm):
    identity = StringField("Логин", validators=[DataRequired(message="Введите логин")])
    password = PasswordField(
        "Пароль", validators=[DataRequired(message="Введите пароль")]
    )
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")

    def validate_identity(self, identity):
        user = User.query.filter(
            (User.username == identity.data) | (User.email == identity.data)
        ).first()
        if user is None:
            raise ValidationError("Пользователь не найден")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Имя пользователя",
        validators=[
            DataRequired(message="Введите имя пользователя"),
            Length(
                min=3,
                max=20,
                message="Имя пользователя должно быть от 3 до 20 символов",
            ),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введите email"),
            Email(message="Введите корректный email адрес"),
        ],
    )
    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Введите пароль"),
            Length(min=6, message="Пароль должен быть не менее 6 символов"),
            password_complexity_check,
        ],
    )
    password_confirm = PasswordField(
        "Подтвердите пароль",
        validators=[
            DataRequired(message="Подтвердите пароль"),
            EqualTo("password", message="Пароли должны совпадать"),
        ],
    )
    submit = SubmitField("Зарегистрироваться")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Этот ник уже занят")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Этот email уже зарегистрирован")


class EditProfileForm(FlaskForm):
    username = StringField(
        "Логин",
        validators=[
            DataRequired(message="Введите логин"),
            Length(min=3, max=20, message="Логин должен быть от 3 до 20 символов"),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Введите email"),
            Email(message="Введите корректный email адрес"),
        ],
    )
    submit = SubmitField("Сохранить изменения")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Текущий пароль", validators=[DataRequired(message="Введите текущий пароль")]
    )
    new_password = PasswordField(
        "Новый пароль",
        validators=[
            DataRequired(message="Введите новый пароль"),
            Length(min=6, message="Пароль должен быть не менее 6 символов"),
            password_complexity_check,
        ],
    )
    confirm_password = PasswordField(
        "Подтвердите новый пароль",
        validators=[
            DataRequired(message="Подтвердите новый пароль"),
            EqualTo("new_password", message="Пароли должны совпадать"),
        ],
    )
    submit = SubmitField("Сменить пароль")


class CommentForm(FlaskForm):
    comment = TextAreaField(
        "Комментарий", validators=[DataRequired(message="Напишите комментарий")]
    )
    submit = SubmitField()


class ProblemsSearchForm(FlaskForm):
    search_input = StringField(
        "Поиск",
        validators=[
            Length(max=200, message="Название задачи должно быть не более 200 символов")
        ],
    )
    order_by = SelectField(
        "Сортировать по",
        choices=[
            ("sort_date desc", "Новые"),
            ("sort_date asc", "Старые"),
            ("popularity desc", "Популярные"),
            ("satisfaction_percent desc,total_completed desc", "Высокий рейтинг"),
            ("satisfaction_percent asc", "Низкий рейтинг"),
            ("name asc", "Имя"),
        ],
    )
    language_filter = SelectField(
        "Язык программирования",
        choices=[
            ("all", "Все"),
            ("my-languages", "Выбранные"),
        ]
        + [(lang["code"], lang["name"]) for lang in languages],
    )
    status_filter = SelectField(
        "Статус",
        choices=[
            ("all", "Все"),
            ("verified", "Проверенные"),
            ("beta", "В тестировке"),
        ],
    )
    ids_filter = SelectField(
        "Прогресс",
        choices=[
            ("all", "Все"),
            ("completed", "Завершенные"),
            ("not_completed", "Неначатые"),
        ],
    )
    ranks_filter = SelectField(
        "Сложность",
        choices=[
            ("all", "Все"),
            ("easy", "Легкие"),
            ("medium", "Средние"),
            ("hard", "Сложные"),
        ],
    )
    tags_filter = SelectMultipleField(
        "Тэги",
    )
    submit = SubmitField()
