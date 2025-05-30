from app.extensions import db
from datetime import datetime


class ProblemVote(db.Model):
    __tablename__ = "problem_votes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False)
    vote_type = db.Column(
        db.String(10), nullable=False
    )  # 'positive', 'neutral', 'negative'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = db.relationship("User", back_populates="problem_votes")
    problem = db.relationship("Problem", back_populates="votes")

    __table_args__ = (
        db.UniqueConstraint("user_id", "problem_id", name="unique_user_problem_vote"),
    )
