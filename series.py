from flask_login import current_user
import requests

import db
from config import API_KEY


class Series:
    def __init__(self, title, status="watchlist", show_type="tv",
                current_season=1, current_episode=0,
                episodes_in_current_season=0, total_seasons=0,
                episodes_watched=0, total_episodes=0,
                rating=0, poster="", year="", genre="", imdb_rating="",
                is_favorite=False, db_id=None):
        self.title = title
        self.status = status
        self.show_type = show_type  # "tv" or "anime"

        # TV specific
        self.current_season = int(current_season or 1)
        self.current_episode = int(current_episode or 0)
        self.episodes_in_current_season = int(episodes_in_current_season or 0)
        self.total_seasons = int(total_seasons or 0)

        # Anime specific
        self.episodes_watched = int(episodes_watched or 0)
        self.total_episodes = int(total_episodes or 0)

        # Common
        self.rating = rating
        self.poster = poster
        self.year = year
        self.genre = genre
        self.imdb_rating = imdb_rating
        self.is_favorite = bool(is_favorite)
        self.db_id = db_id  # row id in the series table — internal use only
    # ── Status checks ──────────────────────────

    def is_watchlist(self):
        return self.status == "watchlist"

    def is_watching(self):
        return self.status == "watching"

    def is_paused(self):
        return self.status == "paused"

    def is_completed(self):
        return self.status == "completed"

    def is_anime(self):
        return self.show_type == "anime"

    def is_tv(self):
        return self.show_type == "tv"

    # ── Progress ────────────────────────────────

    def progress_percent(self):
        if self.is_completed():
            return 100
        if self.show_type == "anime":
            if self.total_episodes == 0:
                return 0
            return min(round((self.episodes_watched / self.total_episodes) * 100), 100)
        else:
            if self.episodes_in_current_season == 0:
                if self.total_seasons == 0:
                    return 0
                return min(round((self.current_season / self.total_seasons) * 100), 100)
            return min(round((self.current_episode / self.episodes_in_current_season) * 100), 100)

    def matches(self, title):
        return self.title.lower() == title.lower()

    @classmethod
    def from_row(cls, row):
        return cls(
            title=row["title"],
            status=row["status"],
            show_type=row["show_type"],
            current_season=row["current_season"],
            current_episode=row["current_episode"],
            episodes_in_current_season=row["episodes_in_current_season"],
            total_seasons=row["total_seasons"],
            episodes_watched=row["episodes_watched"],
            total_episodes=row["total_episodes"],
            rating=row["rating"],
            poster=row["poster"] or "",
            year=row["year"] or "",
            genre=row["genre"] or "",
            imdb_rating=row["imdb_rating"] or "",
            is_favorite=bool(row["is_favorite"]),
            db_id=row["id"],
        )


# ── Database access ─────────────────────────────

def load_series(sort_by="recent"):
    if not current_user.is_authenticated:
        return []

    if sort_by == "favorites":
        rows = db.get_db().execute(
            "SELECT * FROM series WHERE user_id = ? AND is_favorite = 1 ORDER BY id DESC",
            (current_user.id,)
        ).fetchall()
        return [Series.from_row(r) for r in rows]

    sort_options = {
        "recent": "created_at DESC",
        "first_added": "created_at ASC",
        "title_asc": "title COLLATE NOCASE ASC",
        "title_desc": "title COLLATE NOCASE DESC",
    }

    order_by = sort_options.get(sort_by, "id DESC")

    rows = db.get_db().execute(
        f"SELECT * FROM series WHERE user_id = ? ORDER BY {order_by}",
        (current_user.id,)
    ).fetchall()
    return [Series.from_row(r) for r in rows]

def save_series(series_list):
    database = db.get_db()

    for s in series_list:
        if s.db_id is not None:
            database.execute(
                """UPDATE series SET
                   title=?, status=?, show_type=?, current_season=?, current_episode=?,
                   episodes_in_current_season=?, total_seasons=?, episodes_watched=?,
                   total_episodes=?, rating=?, poster=?, year=?, genre=?, imdb_rating=?, is_favorite=?
                   WHERE id=? AND user_id=?""",
                (s.title, s.status, s.show_type, s.current_season, s.current_episode,
                 s.episodes_in_current_season, s.total_seasons, s.episodes_watched,
                 s.total_episodes, s.rating, s.poster, s.year, s.genre, s.imdb_rating,
                 int(s.is_favorite), s.db_id, current_user.id)
            )
        else:
            database.execute(
                """INSERT INTO series
                   (user_id, title, status, show_type, current_season, current_episode,
                    episodes_in_current_season, total_seasons, episodes_watched,
                    total_episodes, rating, poster, year, genre, imdb_rating, is_favorite)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (current_user.id, s.title, s.status, s.show_type, s.current_season,
                 s.current_episode, s.episodes_in_current_season, s.total_seasons,
                 s.episodes_watched, s.total_episodes, s.rating, s.poster,
                 s.year, s.genre, s.imdb_rating, int(s.is_favorite))
            )
    database.commit()


def find_series(title, series_list):
    for s in series_list:
        if s.matches(title):
            return s
    return None


# ── OMDB API (unchanged) ─────────────────────────

def fetch_series_data(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&type=series&apikey={API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") == "True":
            return {
                "poster": data.get("Poster", ""),
                "year": data.get("Year", ""),
                "genre": data.get("Genre", ""),
                "imdb_rating": data.get("imdbRating", ""),
                "total_seasons": int(data.get("totalSeasons", 0)),
            }
    except:
        pass
    return {}


def fetch_season_episodes(title, season):
    try:
        url = f"http://www.omdbapi.com/?t={title}&Season={season}&apikey={API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") == "True":
            return len(data.get("Episodes", []))
    except:
        pass
    return 0


def fetch_series_extra(title):
    """Live lookup for plot/cast/creator, used only on the detail page."""
    try:
        url = f"http://www.omdbapi.com/?t={title}&type=series&apikey={API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") == "True":
            return {
                "plot": data.get("Plot", ""),
                "actors": data.get("Actors", ""),
                "creator": data.get("Writer", ""),
                "imdb_id": data.get("imdbID", ""),
            }
    except:
        pass
    return {}


def fetch_episode_list(title, season):
    """Full episode list (number, title, rating) for one season, for the episode strip."""
    try:
        url = f"http://www.omdbapi.com/?t={title}&Season={season}&apikey={API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("Response") == "True":
            return data.get("Episodes", [])
    except:
        pass
    return []