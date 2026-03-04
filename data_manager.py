from models import db, User, Movie


class DataManager:
    """Provides CRUD operations for User and Movie database records."""

    def create_user(self, name):
        """Create and persist a new User with the given name."""
        try:
            new_user = User(name=name)
            db.session.add(new_user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def get_user(self, user_id):
        """Return the User with the given ID, or None if not found."""
        try:
            return db.session.get(User, user_id)
        except Exception:
            raise

    def get_users(self):
        """Return a list of all User records."""
        try:
            return User.query.all()
        except Exception:
            raise

    def get_movies(self, user_id):
        """Return a list of all Movie records belonging to the given user."""
        try:
            return Movie.query.filter_by(user_id=user_id).all()
        except Exception:
            raise

    def add_movie(self, movie):
        """Persist a new Movie record to the database."""
        try:
            db.session.add(movie)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def update_movie(self, movie_id, name, director, year, poster_url):
        """Update the fields of an existing Movie record.

        Does nothing if no movie with the given ID exists.
        """
        try:
            movie = db.session.get(Movie, movie_id)
            if movie:
                movie.name = name
                movie.director = director
                movie.year = year
                movie.poster_url = poster_url
                db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def delete_movie(self, movie_id):
        """Delete the Movie record with the given ID.

        Does nothing if no movie with the given ID exists.
        """
        try:
            movie = db.session.get(Movie, movie_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()
        except Exception:
            db.session.rollback()
            raise
