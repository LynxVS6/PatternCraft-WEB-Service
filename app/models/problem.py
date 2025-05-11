from app.extensions import db


class Problem(db.Model):
    __tablename__ = 'problems'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tags_json = db.Column(db.JSON, nullable=True)

    # Relationships
    solutions = db.relationship('Solution', back_populates='problem') 