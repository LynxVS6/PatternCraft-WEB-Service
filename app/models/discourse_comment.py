from app.extensions import db


class DiscourseComment(db.Model):
    __tablename__ = "discourse_comments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey("problems.id"), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    user = db.relationship("User", back_populates="discourse_comments")
    problem = db.relationship("Problem", back_populates="discourse_comments")
    votes = db.relationship(
        "DiscourseVote", back_populates="comment", cascade="all, delete-orphan"
    )

    @property
    def vote_count(self):
        return sum(1 for vote in self.votes if vote.vote_type == "up") - sum(
            1 for vote in self.votes if vote.vote_type == "down"
        )


class DiscourseVote(db.Model):
    __tablename__ = "discourse_votes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    target_id = db.Column(
        db.Integer, db.ForeignKey("discourse_comments.id"), nullable=False
    )
    vote_type = db.Column(db.String(4), nullable=False)  # 'up' or 'down'
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", back_populates="discourse_votes")
    comment = db.relationship("DiscourseComment", back_populates="votes")
