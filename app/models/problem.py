from app.extensions import db
from app.models.solution import Solution
from flask_login import current_user
from datetime import datetime, timezone
from sqlalchemy import exists


class Problem(db.Model):
    __tablename__ = "problems"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tags_json = db.Column(db.JSON, nullable=True)
    difficulty = db.Column(db.String(20), nullable=False, default="Легкое")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    language = db.Column(db.String(50), nullable=False, default="python")
    status = db.Column(
        db.String(20), nullable=False, default="active"
    )  # verified, beta
    bookmark_count = db.Column(db.Integer, nullable=False, default=0)
    positive_vote = db.Column(db.Integer, default=0)
    negative_vote = db.Column(db.Integer, default=0)
    neutral_vote = db.Column(db.Integer, default=0)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )

    solutions = db.relationship(
        "Solution", back_populates="problem", cascade="all, delete-orphan"
    )
    discourse_comments = db.relationship(
        "DiscourseComment", back_populates="problem", cascade="all, delete-orphan"
    )
    bookmarks = db.relationship(
        "Bookmark", back_populates="problem", cascade="all, delete-orphan"
    )
    votes = db.relationship(
        "ProblemVote", back_populates="problem", cascade="all, delete-orphan"
    )
    author = db.relationship("User", back_populates="authored_problems")

    @property
    def user_vote(self):
        """Get the current user's vote for this problem"""
        if not current_user.is_authenticated:
            return None
        vote = ProblemVote.query.filter_by(
            target_id=self.id, user_id=current_user.id
        ).first()
        return vote.vote_type if vote else None

    @property
    def total_votes(self):
        """Get the total number of votes for this problem"""
        return self.positive_vote + self.negative_vote + self.neutral_vote

    @property
    def satisfaction_percent(self):
        """Calculate the satisfaction percentage based on votes"""
        total = self.total_votes
        if total == 0:
            return 0
        return round((self.positive_vote * 100.0) / total)

    @property
    def is_completed_by_current_user(self):
        """Check if the current user has completed this problem"""
        if not current_user.is_authenticated:
            return False
        return db.session.query(
            exists().where(
                Solution.problem_id == self.id, Solution.user_id == current_user.id
            )
        ).scalar()

    def update_vote_counts(self):
        """Update vote counts based on actual votes in the database"""
        # Reset all counts to 0
        self.positive_vote = 0
        self.neutral_vote = 0
        self.negative_vote = 0

        # Get all votes for this problem
        votes = ProblemVote.query.filter_by(target_id=self.id).all()

        # Count votes by type
        for vote in votes:
            if vote.vote_type == "positive":
                self.positive_vote += 1
            elif vote.vote_type == "neutral":
                self.neutral_vote += 1
            elif vote.vote_type == "negative":
                self.negative_vote += 1

        # Commit the changes to the database
        db.session.commit()


class ProblemVote(db.Model):
    __tablename__ = "problem_votes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False)
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
        db.UniqueConstraint("user_id", "target_id", name="unique_user_problem_vote"),
    )
