from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """Database model representing an application user."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    movies = db.relationship(
        'Movie', backref='user', cascade='all, delete-orphan'
    )

    def __repr__(self):
        """Return a string representation of the User instance."""
        return f'<User {self.name}>'


class Movie(db.Model):
    """Database model representing a movie belonging to a user."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100))
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        """Return a string representation of the Movie instance."""
        return f'<Movie {self.name}>'
