from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy import text

# Association tables for many-to-many relationships
course_problems = db.Table(
    "course_problems",
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id"), primary_key=True),
    db.Column("problem_id", db.Integer, db.ForeignKey("problems.id"), primary_key=True),
)

course_theories = db.Table(
    "course_theories",
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id"), primary_key=True),
    db.Column("theory_id", db.Integer, db.ForeignKey("theories.id"), primary_key=True),
)


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    server_course_id = db.Column(db.Integer, nullable=True)  # For sync with lab version
    creator_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status = db.Column(
        db.String(20), nullable=False, default="active"
    )  # active, draft, archived
    is_hidden = db.Column(db.Boolean, default=False, nullable=False)
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

    is_hidden = db.Column(
        db.Boolean,
        default=False,
        server_default=text('0'),
        nullable=False
    )

    # Relationships
    creator = db.relationship("User", back_populates="created_courses")
    problems = db.relationship(
        "Problem", secondary=course_problems, back_populates="courses"
    )
    theories = db.relationship(
        "Theory", secondary=course_theories, back_populates="courses"
    )
    course_votes = db.relationship(
        "CourseVote", back_populates="course", cascade="all, delete-orphan"
    )
    bookmarks = db.relationship(
        "CourseBookmark", back_populates="course", cascade="all, delete-orphan"
    )

    @property
    def user_vote(self):
        """Get the current user's vote for this course"""
        from flask_login import current_user

        if not current_user.is_authenticated:
            return None
        vote = CourseVote.query.filter_by(
            target_id=self.id, user_id=current_user.id
        ).first()
        return vote.vote_type if vote else None

    @property
    def total_votes(self):
        """Get the total number of votes for this course"""
        return self.positive_vote + self.negative_vote + self.neutral_vote

    @property
    def satisfaction_percent(self):
        """Calculate the satisfaction percentage based on votes"""
        total = self.total_votes
        if total == 0:
            return 0
        return round((self.positive_vote * 100.0) / total)

    @property
    def problems_count(self):
        """Get the number of problems in this course"""
        return len(self.problems)

    @property
    def theories_count(self):
        """Get the number of theories in this course"""
        return len(self.theories)

    def update_vote_counts(self):
        """Update vote counts based on actual votes in the database"""
        # Reset all counts to 0
        self.positive_vote = 0
        self.neutral_vote = 0
        self.negative_vote = 0

        # Get all votes for this course
        votes = CourseVote.query.filter_by(target_id=self.id).all()

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


class CourseVote(db.Model):
    __tablename__ = "course_votes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    vote_type = db.Column(
        db.String(10), nullable=False
    )  # 'positive', 'neutral', 'negative'
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    user = db.relationship("User", back_populates="course_votes")
    course = db.relationship("Course", back_populates="course_votes")

    __table_args__ = (
        db.UniqueConstraint("user_id", "target_id", name="unique_user_course_vote"),
    )


class CourseBookmark(db.Model):
    __tablename__ = "course_bookmarks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # Relationships
    user = db.relationship("User", back_populates="course_bookmarks")
    course = db.relationship("Course", back_populates="bookmarks")

    __table_args__ = (
        db.UniqueConstraint("user_id", "course_id", name="unique_user_course_bookmark"),
    )
