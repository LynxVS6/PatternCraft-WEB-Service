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
    solution_votes = db.relationship('SolutionVote', back_populates='solution')

    @property
    def votes_count(self):
        return len(self.solution_votes)


class SolutionVote(db.Model):
    __tablename__ = 'solution_votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('solutions.id'), nullable=False)
    vote_type = db.Column(db.String(7), nullable=False)  # 'like' or 'dislike'
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', back_populates='solution_votes')
    solution = db.relationship('Solution', back_populates='solution_votes')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'target_id', name='unique_user_solution_like'),
    )
