from app.extensions import db


class Solution(db.Model):
    __tablename__ = 'solutions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey(
        'problems.id'), nullable=False)
    solution = db.Column(db.Text, nullable=False)

    user = db.relationship('User', back_populates='solutions')
    problem = db.relationship('Problem', back_populates='solutions')
    comments = db.relationship('Comment', back_populates='solution')
    likes = db.relationship('Like', back_populates='solution')

    @property
    def likes_count(self):
        return len(self.likes)
