from app.extensions import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    solution_id = db.Column(db.Integer, db.ForeignKey("solutions.id"), nullable=False)
    comment = db.Column(db.Text, nullable=False)

    user = db.relationship("User", back_populates="comments")
    solution = db.relationship("Solution", back_populates="comments")
    votes = db.relationship('CommentVote', back_populates='comment')

    @property
    def vote_count(self):
        return sum(1 for vote in self.votes if vote.vote_type == 'up') - \
               sum(1 for vote in self.votes if vote.vote_type == 'down')


class CommentVote(db.Model):
    __tablename__ = 'comment_votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False)
    vote_type = db.Column(db.String(4), nullable=False)  # 'up' or 'down'
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', back_populates='comment_votes')
    comment = db.relationship('Comment', back_populates='votes')
