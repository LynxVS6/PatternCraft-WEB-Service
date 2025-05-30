from app.extensions import db
from app.models.problem_vote import ProblemVote
from flask_login import current_user
from datetime import datetime, timezone


class Problem(db.Model):
    __tablename__ = 'problems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tags_json = db.Column(db.JSON, nullable=True)
    difficulty = db.Column(db.String(20), nullable=False, default='Легкое')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    language = db.Column(db.String(50), nullable=False, default='python')
    status = db.Column(db.String(20), nullable=False, default='active')  # checked, beta
    bookmark_count = db.Column(db.Integer, nullable=False, default=0)
    positive_vote = db.Column(db.Integer, default=0)
    negative_vote = db.Column(db.Integer, default=0)
    neutral_vote = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

    solutions = db.relationship('Solution', back_populates='problem')
    discourse_comments = db.relationship('DiscourseComment', back_populates='problem')
    bookmarks = db.relationship('Bookmark', back_populates='problem')
    votes = db.relationship('ProblemVote', back_populates='problem')
    author = db.relationship('User', back_populates='authored_problems')

    @property
    def user_vote(self):
        """Get the current user's vote for this problem"""
        if not current_user.is_authenticated:
            return None
        vote = ProblemVote.query.filter_by(
            problem_id=self.id,
            user_id=current_user.id
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

    def update_vote_counts(self):
        """Update vote counts based on actual votes in the database"""
        # Reset all counts to 0
        self.positive_vote = 0
        self.neutral_vote = 0
        self.negative_vote = 0

        # Get all votes for this problem
        votes = ProblemVote.query.filter_by(problem_id=self.id).all()
        
        # Count votes by type
        for vote in votes:
            if vote.vote_type == 'positive':
                self.positive_vote += 1
            elif vote.vote_type == 'neutral':
                self.neutral_vote += 1
            elif vote.vote_type == 'negative':
                self.negative_vote += 1
