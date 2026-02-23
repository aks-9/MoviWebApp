import os
import requests
from flask import Flask, request, redirect, url_for, render_template
from data_manager import DataManager
from models import db, Movie

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

data_manager = DataManager()

OMDB_API_KEY = os.environ.get('OMDB_API_KEY', '')


def fetch_movie_data(title):
    if not OMDB_API_KEY:
        return None
    response = requests.get(
        'http://www.omdbapi.com/',
        params={'t': title, 'apikey': OMDB_API_KEY}
    )
    data = response.json()
    if data.get('Response') == 'True':
        return {
            'name': data.get('Title', title),
            'director': data.get('Director', 'N/A'),
            'year': int(data.get('Year', 0)[:4]),
            'poster_url': data.get('Poster', '')
        }
    return None


@app.route('/')
def index():
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    name = request.form.get('name', '').strip()
    if name:
        data_manager.create_user(name)
    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def user_movies(user_id):
    movies = data_manager.get_movies(user_id)
    return render_template('user_movies.html', movies=movies, user_id=user_id)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    title = request.form.get('title', '').strip()
    if not title:
        return redirect(url_for('user_movies', user_id=user_id))

    movie_data = fetch_movie_data(title)
    if movie_data:
        movie = Movie(
            name=movie_data['name'],
            director=movie_data['director'],
            year=movie_data['year'],
            poster_url=movie_data['poster_url'],
            user_id=user_id
        )
    else:
        movie = Movie(name=title, user_id=user_id)

    data_manager.add_movie(movie)
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    name = request.form.get('name', '').strip()
    director = request.form.get('director', '').strip()
    year = request.form.get('year', 0)
    poster_url = request.form.get('poster_url', '').strip()
    data_manager.update_movie(movie_id, name, director, int(year), poster_url)
    return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
