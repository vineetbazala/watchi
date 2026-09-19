from flask_login import current_user
import requests

import db
from config import API_KEY


class Movie:
    def __init__(self, title, status, rating=0,
                poster="", year="", genre="",
                director="", plot="", imdb_rating="",
                is_favorite=False, db_id=None):
        self.title = title
        self.status = status
        self.rating = rating
        self.poster = poster
        self.year = year
        self.genre = genre
        self.director = director
        self.plot = plot
        self.imdb_rating = imdb_rating
        self.is_favorite = bool(is_favorite)
        self.db_id = db_id

    def is_watchlist(self):
        return self.status == "watchlist"

    def is_watched(self):
        return self.status == "watched"

    def mark_watched(self, rating):
        self.status = "watched"
        self.rating = rating

    def mark_unwatched(self):
        self.status = "watchlist"
        self.rating = "Not Watched Yet"

    def matches(self, movie_name):
        return self.title.lower() == movie_name.lower()

    def update_rating(self, rating):
        self.rating = rating

    @classmethod
    def from_row(cls, row):
        rating = row["rating"] if row["rating"] is not None else "Not Watched Yet"
        return cls(
            title=row["title"],
            status=row["status"],
            rating=rating,
            poster=row["poster"] or "",
            year=row["year"] or "",
            genre=row["genre"] or "",
            director=row["director"] or "",
            plot=row["plot"] or "",
            imdb_rating=row["imdb_rating"] or "",
            is_favorite=bool(row["is_favorite"]),
            db_id=row["id"],
        )

# ── Database access ─────────────────────────────

def load_movies(sort_by="recent"):
    if not current_user.is_authenticated:
        return []

    if sort_by == "favorites":
        rows = db.get_db().execute(
            "SELECT * FROM movies WHERE user_id = ? AND is_favorite = 1 ORDER BY id DESC",
            (current_user.id,)
        ).fetchall()
        return [Movie.from_row(r) for r in rows]

    sort_options = {
        "recent": "created_at DESC",
        "first_added": "created_at ASC",
        "title_asc": "title COLLATE NOCASE ASC",
        "title_desc": "title COLLATE NOCASE DESC",
    }

    order_by = sort_options.get(sort_by, "id DESC")

    rows = db.get_db().execute(
        f"SELECT * FROM movies WHERE user_id = ? ORDER BY {order_by}",
        (current_user.id,)
    ).fetchall()

    return [Movie.from_row(r) for r in rows]

def save_movies(movies):
    database = db.get_db()

    for m in movies:
        rating = m.rating if isinstance(m.rating, int) else None
        if m.db_id is not None:
            database.execute(
                """UPDATE movies SET
                   title=?, status=?, rating=?, poster=?, year=?, genre=?,
                   director=?, plot=?, imdb_rating=?, is_favorite=?
                   WHERE id=? AND user_id=?""",
                (m.title, m.status, rating, m.poster, m.year, m.genre,
                 m.director, m.plot, m.imdb_rating, int(m.is_favorite),
                 m.db_id, current_user.id)
            )
        else:
            database.execute(
                """INSERT INTO movies
                   (user_id, title, status, rating, poster, year, genre, director, plot, imdb_rating, is_favorite)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (current_user.id, m.title, m.status, rating, m.poster, m.year,
                 m.genre, m.director, m.plot, m.imdb_rating, int(m.is_favorite))
            )
    database.commit()


def find_movie(movie_name, movies):
    for movie in movies:
        if movie.matches(movie_name):
            return movie
    return None


# ── OMDB API (unchanged) ─────────────────────────

def fetch_movie_data(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") == "True":
            return {
                "poster": data.get("Poster", ""),
                "year": data.get("Year", ""),
                "genre": data.get("Genre", ""),
                "director": data.get("Director", ""),
                "plot": data.get("Plot", ""),
                "actors": data.get("Actors", ""),
                "imdb_rating": data.get("imdbRating", ""),
                "imdb_id": data.get("imdbID", "")
            }
    except:
        pass
    return {}