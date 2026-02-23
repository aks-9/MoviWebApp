# MoviWebApp

A Flask web application for managing users and their personal movie lists, with automatic movie data fetching via the OMDb API.

## Features

- Add and view users
- Add movies to a user's list — title, director, year, and poster are fetched automatically from OMDb
- Edit or delete movies from a user's list
- Falls back to the entered title if the OMDb lookup fails or no API key is set
- Custom dark cinema-themed UI
- Error pages for 404 and 500

## Project Structure

```
MoviWebApp/
├── app.py               # Flask app, routes, OMDb fetch helper
├── data_manager.py      # Database access layer (SQLAlchemy)
├── models.py            # SQLAlchemy models: User, Movie
├── templates/
│   ├── base.html
│   ├── index.html       # User list + add-user form
│   ├── user_movies.html # Movie list + add/edit/delete forms
│   ├── 404.html
│   └── 500.html
├── static/
│   └── style.css
├── data/
│   └── movies.db        # SQLite database (auto-created on first run)
├── test_data_manager.py
├── test_routes.py
├── requirements.txt
└── .env                 # OMDb API key (not committed)
```

## Setup

**1. Clone the repository**

```bash
git clone https://github.com/aks-9/MoviWebApp.git
cd MoviWebApp
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/Scripts/activate   # Windows (Git Bash)
source venv/bin/activate        # macOS / Linux
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure the OMDb API key**

Create a `.env` file in the project root:

```
OMDB_API_KEY=your_api_key_here
```

A free key can be obtained at [omdbapi.com](http://www.omdbapi.com/apikey.aspx). The app works without a key — movies will be saved with just the title you enter.

**5. Run the app**

```bash
python app.py
```

The app will be available at `http://127.0.0.1:5000`.

## Running Tests

```bash
python -m pytest test_data_manager.py test_routes.py -v
```

Or with the built-in runner:

```bash
python -m unittest discover
```

## API Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Home page — list all users |
| POST | `/users` | Create a new user |
| GET | `/users/<id>/movies` | View a user's movie list |
| POST | `/users/<id>/movies` | Add a movie to a user's list |
| POST | `/users/<id>/movies/<id>/update` | Update a movie's details |
| POST | `/users/<id>/movies/<id>/delete` | Delete a movie |

## Stack

- Python 3
- Flask 3.1
- Flask-SQLAlchemy 3.1 / SQLAlchemy 2.0
- SQLite
- OMDb API
- python-dotenv
