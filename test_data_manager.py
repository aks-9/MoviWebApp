import unittest
from flask import Flask
from models import db, Movie
from data_manager import DataManager


class TestDataManager(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        with self.app.app_context():
            db.create_all()
        self.dm = DataManager()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_create_user(self):
        with self.app.app_context():
            self.dm.create_user('Alice')
            users = self.dm.get_users()
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0].name, 'Alice')

    def test_get_users_empty(self):
        with self.app.app_context():
            users = self.dm.get_users()
            self.assertEqual(users, [])

    def test_get_users_multiple(self):
        with self.app.app_context():
            self.dm.create_user('Alice')
            self.dm.create_user('Bob')
            users = self.dm.get_users()
            self.assertEqual(len(users), 2)

    def test_add_and_get_movies(self):
        with self.app.app_context():
            self.dm.create_user('Alice')
            user = self.dm.get_users()[0]
            movie = Movie(name='Jaws', director='Spielberg', year=1975,
                          poster_url='http://example.com/jaws.jpg', user_id=user.id)
            self.dm.add_movie(movie)
            movies = self.dm.get_movies(user.id)
            self.assertEqual(len(movies), 1)
            self.assertEqual(movies[0].name, 'Jaws')

    def test_get_movies_empty(self):
        with self.app.app_context():
            self.dm.create_user('Alice')
            user = self.dm.get_users()[0]
            movies = self.dm.get_movies(user.id)
            self.assertEqual(movies, [])

    def test_update_movie(self):
        with self.app.app_context():
            self.dm.create_user('Alice')
            user = self.dm.get_users()[0]
            movie = Movie(name='Jaws', director='Spielberg', year=1975,
                          poster_url='http://example.com/jaws.jpg', user_id=user.id)
            self.dm.add_movie(movie)
            movie_id = self.dm.get_movies(user.id)[0].id
            self.dm.update_movie(movie_id, 'Jaws 2', 'Jeannot Szwarc', 1978,
                                 'http://example.com/jaws2.jpg')
            updated = self.dm.get_movies(user.id)[0]
            self.assertEqual(updated.name, 'Jaws 2')
            self.assertEqual(updated.year, 1978)

    def test_delete_movie(self):
        with self.app.app_context():
            self.dm.create_user('Alice')
            user = self.dm.get_users()[0]
            movie = Movie(name='Jaws', director='Spielberg', year=1975,
                          poster_url='http://example.com/jaws.jpg', user_id=user.id)
            self.dm.add_movie(movie)
            movie_id = self.dm.get_movies(user.id)[0].id
            self.dm.delete_movie(movie_id)
            movies = self.dm.get_movies(user.id)
            self.assertEqual(movies, [])

    def test_delete_nonexistent_movie(self):
        with self.app.app_context():
            self.dm.delete_movie(999)  # Should not raise


if __name__ == '__main__':
    unittest.main()
