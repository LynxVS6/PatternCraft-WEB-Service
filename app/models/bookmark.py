from app import db
from datetime import datetime


class Bookmark(db.Model):
    __tablename__ = "bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    problem_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Define relationships
    user = db.relationship("User", back_populates="bookmarks")
    problem = db.relationship("Problem", back_populates="bookmarks")

    # Add unique constraint to prevent duplicate bookmarks
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "problem_id", name="unique_user_problem_bookmark"
        ),
    )
