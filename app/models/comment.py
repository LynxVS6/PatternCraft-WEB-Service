from app.extensions import db


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    solution_id = db.Column(db.Integer, db.ForeignKey('solutions.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)

    user = db.relationship('User', back_populates='comments')
    solution = db.relationship('Solution', back_populates='comments') 