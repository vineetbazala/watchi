-- Watchi database schema
-- Run once via init_db() to create these tables in watchi.db

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS movies;
DROP TABLE IF EXISTS series;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'watchlist',   -- "watched" or "watchlist"
    rating INTEGER,                              -- NULL = not rated yet (see note below)
    poster TEXT,
    year TEXT,
    genre TEXT,
    director TEXT,
    plot TEXT,
    imdb_rating TEXT,
    is_favorite INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (user_id, title COLLATE NOCASE)
);

CREATE TABLE series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'watchlist',   -- watchlist / watching / paused / completed
    show_type TEXT NOT NULL DEFAULT 'tv',        -- "tv" or "anime"
    current_season INTEGER DEFAULT 1,
    current_episode INTEGER DEFAULT 0,
    episodes_in_current_season INTEGER DEFAULT 0,
    total_seasons INTEGER DEFAULT 0,
    episodes_watched INTEGER DEFAULT 0,
    total_episodes INTEGER DEFAULT 0,
    rating INTEGER DEFAULT 0,
    poster TEXT,
    year TEXT,
    genre TEXT,
    imdb_rating TEXT,
    is_favorite INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (user_id, title COLLATE NOCASE)
);