from app.extensions import db
from datetime import datetime, timezone


class Theory(db.Model):
    __tablename__ = "theories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    in_practice = db.Column(db.Boolean, default=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")
    positive_vote = db.Column(db.Integer, default=0)
    negative_vote = db.Column(db.Integer, default=0)
    neutral_vote = db.Column(db.Integer, default=0)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    author = db.relationship("User", back_populates="authored_theories")
    theory_votes = db.relationship(
        "TheoryVote", back_populates="theory", cascade="all, delete-orphan"
    )
    bookmarks = db.relationship(
        "TheoryBookmark", back_populates="theory", cascade="all, delete-orphan"
    )
    courses = db.relationship(
        "Course", secondary="course_theories", back_populates="theories"
    )

    @property
    def user_vote(self):
        """Get the current user's vote for this theory"""
        from flask_login import current_user

        if not current_user.is_authenticated:
            return None
        vote = TheoryVote.query.filter_by(
            target_id=self.id, user_id=current_user.id
        ).first()
        return vote.vote_type if vote else None

    @property
    def total_votes(self):
        """Get the total number of votes for this theory"""
        return self.positive_vote + self.negative_vote + self.neutral_vote

    @property
    def satisfaction_percent(self):
        """Calculate the satisfaction percentage based on votes"""
        total = self.total_votes
        if total == 0:
            return 0
        return round((self.positive_vote * 100.0) / total)

    def update_vote_counts(self):
        """Update vote counts based on actual votes in the database"""
        self.positive_vote = 0
        self.neutral_vote = 0
        self.negative_vote = 0

        votes = TheoryVote.query.filter_by(target_id=self.id).all()

        for vote in votes:
            if vote.vote_type == "positive":
                self.positive_vote += 1
            elif vote.vote_type == "neutral":
                self.neutral_vote += 1
            elif vote.vote_type == "negative":
                self.negative_vote += 1

        db.session.commit()


class TheoryVote(db.Model):
    __tablename__ = "theory_votes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("theories.id"), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    user = db.relationship("User", back_populates="theory_votes")
    theory = db.relationship("Theory", back_populates="theory_votes")

    __table_args__ = (
        db.UniqueConstraint("user_id", "target_id", name="unique_user_theory_vote"),
    )


class TheoryBookmark(db.Model):
    __tablename__ = "theory_bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    theory_id = db.Column(db.Integer, db.ForeignKey("theories.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="theory_bookmarks")
    theory = db.relationship("Theory", back_populates="bookmarks")

    __table_args__ = (
        db.UniqueConstraint("user_id", "theory_id", name="unique_user_theory_bookmark"),
    )
