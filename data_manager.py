from models import db, User, Movie


class DataManager:

    def create_user(self, name):
        try:
            new_user = User(name=name)
            db.session.add(new_user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def get_user(self, user_id):
        try:
            return db.session.get(User, user_id)
        except Exception:
            raise

    def get_users(self):
        try:
            return User.query.all()
        except Exception:
            raise

    def get_movies(self, user_id):
        try:
            return Movie.query.filter_by(user_id=user_id).all()
        except Exception:
            raise

    def add_movie(self, movie):
        try:
            db.session.add(movie)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def update_movie(self, movie_id, name, director, year, poster_url):
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
        try:
            movie = db.session.get(Movie, movie_id)
            if movie:
                db.session.delete(movie)
                db.session.commit()
        except Exception:
            db.session.rollback()
            raise
