from datetime import datetime
from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    new_email = db.Column(db.String(120), unique=True, nullable=True)
    email_confirmed = db.Column(db.Boolean, default=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    solutions = db.relationship('Solution', back_populates='user')
    comments = db.relationship('Comment', back_populates='user')
    solution_votes = db.relationship('SolutionVote', back_populates='user')
    discourse_comments = db.relationship('DiscourseComment', back_populates='user')
    discourse_votes = db.relationship('DiscourseVote', back_populates='user')
    comment_votes = db.relationship('CommentVote', back_populates='user')
    bookmarks = db.relationship('Bookmark', back_populates='user')
    problem_votes = db.relationship('ProblemVote', back_populates='user')
    authored_problems = db.relationship('Problem', back_populates='author')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
