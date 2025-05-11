from app.extensions import db


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    solution_id = db.Column(db.Integer, db.ForeignKey('solutions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    user = db.relationship('User', back_populates='likes')
    solution = db.relationship('Solution', back_populates='likes')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'solution_id', name='unique_user_solution_like'),
    )
