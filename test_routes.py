import unittest
from unittest.mock import patch, MagicMock

from app import app
from models import db, Movie, User


class TestRoutes(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    # --- Home ---

    @patch('app.render_template', return_value='home page')
    def test_index_returns_200(self, mock_render):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @patch('app.render_template', return_value='home page')
    def test_index_passes_users_to_template(self, mock_render):
        with app.app_context():
            db.session.add(User(name='Alice'))
            db.session.commit()
        self.client.get('/')
        users_passed = mock_render.call_args[1]['users']
        self.assertEqual(len(users_passed), 1)
        self.assertEqual(users_passed[0].name, 'Alice')

    # --- Add User ---

    def test_create_user_redirects_to_home(self):
        response = self.client.post('/users', data={'name': 'Alice'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/', response.headers['Location'])

    def test_create_user_persists_to_db(self):
        self.client.post('/users', data={'name': 'Alice'})
        with app.app_context():
            users = User.query.all()
            self.assertEqual(len(users), 1)
            self.assertEqual(users[0].name, 'Alice')

    def test_create_user_empty_name_ignored(self):
        self.client.post('/users', data={'name': '   '})
        with app.app_context():
            self.assertEqual(User.query.count(), 0)

    # --- User Movies ---

    @patch('app.render_template', return_value='movies page')
    def test_user_movies_returns_200(self, mock_render):
        with app.app_context():
            db.session.add(User(name='Alice'))
            db.session.commit()
            user_id = User.query.first().id
        response = self.client.get(f'/users/{user_id}/movies')
        self.assertEqual(response.status_code, 200)

    @patch('app.render_template', return_value='movies page')
    def test_user_movies_passes_correct_movies(self, mock_render):
        with app.app_context():
            user = User(name='Alice')
            db.session.add(user)
            db.session.commit()
            db.session.add(Movie(name='Jaws', user_id=user.id))
            db.session.commit()
            user_id = user.id
        self.client.get(f'/users/{user_id}/movies')
        movies_passed = mock_render.call_args[1]['movies']
        self.assertEqual(len(movies_passed), 1)
        self.assertEqual(movies_passed[0].name, 'Jaws')

    # --- Add Movie (no OMDb key) ---

    def test_add_movie_without_omdb_saves_title(self):
        with app.app_context():
            db.session.add(User(name='Alice'))
            db.session.commit()
            user_id = User.query.first().id
        self.client.post(f'/users/{user_id}/movies', data={'title': 'Alien'})
        with app.app_context():
            movie = Movie.query.first()
            self.assertIsNotNone(movie)
            self.assertEqual(movie.name, 'Alien')

    def test_add_movie_redirects_to_user_movies(self):
        with app.app_context():
            db.session.add(User(name='Alice'))
            db.session.commit()
            user_id = User.query.first().id
        response = self.client.post(
            f'/users/{user_id}/movies', data={'title': 'Alien'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'/users/{user_id}/movies', response.headers['Location'])

    def test_add_movie_empty_title_ignored(self):
        with app.app_context():
            db.session.add(User(name='Alice'))
            db.session.commit()
            user_id = User.query.first().id
        self.client.post(f'/users/{user_id}/movies', data={'title': ''})
        with app.app_context():
            self.assertEqual(Movie.query.count(), 0)

    # --- Add Movie (with OMDb mock) ---

    @patch('app.OMDB_API_KEY', 'fakekey')
    @patch('app.requests.get')
    def test_add_movie_with_omdb_uses_fetched_data(self, mock_get):
        mock_get.return_value.json.return_value = {
            'Response': 'True',
            'Title': 'Alien',
            'Director': 'Ridley Scott',
            'Year': '1979',
            'Poster': 'http://example.com/alien.jpg'
        }
        with app.app_context():
            db.session.add(User(name='Alice'))
            db.session.commit()
            user_id = User.query.first().id
        self.client.post(f'/users/{user_id}/movies', data={'title': 'Alien'})
        with app.app_context():
            movie = Movie.query.first()
            self.assertEqual(movie.name, 'Alien')
            self.assertEqual(movie.director, 'Ridley Scott')
            self.assertEqual(movie.year, 1979)

    @patch('app.OMDB_API_KEY', 'fakekey')
    @patch('app.requests.get')
    def test_add_movie_omdb_not_found_falls_back_to_title(self, mock_get):
        mock_get.return_value.json.return_value = {'Response': 'False'}
        with app.app_context():
            db.session.add(User(name='Alice'))
            db.session.commit()
            user_id = User.query.first().id
        self.client.post(
            f'/users/{user_id}/movies', data={'title': 'Unknown Movie'}
        )
        with app.app_context():
            movie = Movie.query.first()
            self.assertEqual(movie.name, 'Unknown Movie')

    # --- Update Movie ---

    def test_update_movie_changes_fields(self):
        with app.app_context():
            user = User(name='Alice')
            db.session.add(user)
            db.session.commit()
            movie = Movie(name='Jaws', director='Spielberg', year=1975,
                          poster_url='', user_id=user.id)
            db.session.add(movie)
            db.session.commit()
            user_id, movie_id = user.id, movie.id
        self.client.post(f'/users/{user_id}/movies/{movie_id}/update', data={
            'name': 'Jaws 2', 'director': 'Jeannot Szwarc',
            'year': '1978', 'poster_url': ''
        })
        with app.app_context():
            updated = db.session.get(Movie, movie_id)
            self.assertEqual(updated.name, 'Jaws 2')
            self.assertEqual(updated.year, 1978)

    def test_update_movie_redirects(self):
        with app.app_context():
            user = User(name='Alice')
            db.session.add(user)
            db.session.commit()
            movie = Movie(name='Jaws', user_id=user.id)
            db.session.add(movie)
            db.session.commit()
            user_id, movie_id = user.id, movie.id
        url = f'/users/{user_id}/movies/{movie_id}/update'
        data = {'name': 'Jaws', 'director': '', 'year': '0', 'poster_url': ''}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    # --- Delete Movie ---

    def test_delete_movie_removes_from_db(self):
        with app.app_context():
            user = User(name='Alice')
            db.session.add(user)
            db.session.commit()
            movie = Movie(name='Jaws', user_id=user.id)
            db.session.add(movie)
            db.session.commit()
            user_id, movie_id = user.id, movie.id
        self.client.post(f'/users/{user_id}/movies/{movie_id}/delete')
        with app.app_context():
            self.assertIsNone(db.session.get(Movie, movie_id))

    def test_delete_movie_redirects(self):
        with app.app_context():
            user = User(name='Alice')
            db.session.add(user)
            db.session.commit()
            movie = Movie(name='Jaws', user_id=user.id)
            db.session.add(movie)
            db.session.commit()
            user_id, movie_id = user.id, movie.id
        url = f'/users/{user_id}/movies/{movie_id}/delete'
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    unittest.main()
