from dotenv import load_dotenv
load_dotenv()
import random
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import API_KEY
from movie import Movie, load_movies, save_movies, find_movie, fetch_movie_data
from series import (Series, load_series, save_series, find_series,
                     fetch_series_data, fetch_season_episodes,
                     fetch_series_extra, fetch_episode_list)
import tmdb
from flask import jsonify
from flask_login import login_user, logout_user, login_required
import db
import auth
import os
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-fallback-change-this")
db.init_app(app)
auth.init_app(app)
from werkzeug.utils import secure_filename
from flask_login import current_user
from taste import build_profile, gather_recommendations

@app.context_processor
def inject_profile_stats():
    if current_user.is_authenticated:
        movies = load_movies()
        series_list = load_series()
        return {
            "profile_movie_count": len(movies),
            "profile_show_count": len(series_list),
        }
    return {}

@app.route("/")
@login_required
def home():
    movies = load_movies()
    series_list = load_series()

    # Movie stats
    watched = sum(1 for m in movies if m.is_watched())
    watchlist_movies = sum(1 for m in movies if m.is_watchlist())
    ratings = [m.rating for m in movies if m.is_watched() and isinstance(m.rating, int)]
    avg = round(sum(ratings) / len(ratings), 1) if ratings else 0

    # Combined total
    total = len(movies) + len(series_list)

    # Watchlist includes series watchlist too
    watchlist_series = sum(1 for s in series_list if s.is_watchlist())
    watchlist = watchlist_movies + watchlist_series

    # Featured from both
    all_media = movies + series_list
    featured = random.choice(all_media) if all_media else None
    featured_type = "series" if featured in series_list else "movie"

    return render_template("home.html",
        active_page="home",
        total=total,
        watched=watched,
        watchlist=watchlist,
        avg=avg,
        featured=featured,
        featured_type=featured_type
    )

@app.route("/movies")
@login_required
def movies():
    sort_by = request.args.get("sort")
    if sort_by:
        session["movies_sort"] = sort_by
    else:
        sort_by = session.get("movies_sort", "recent")

    movie_list = load_movies(sort_by)
    return render_template("movies.html",
        movies=movie_list,
        current_sort=sort_by,
        active_page="movies"
    )


@app.route("/addmovie", methods=["GET", "POST"])
@login_required
def addmovie():
    if request.method == "POST":
        movie_name = request.form["movie_name"]
        status = request.form["status"]
        movies = load_movies()

        if find_movie(movie_name, movies):
            flash(f"{movie_name} is already in your collection")
            return redirect(url_for("movies"))

        api_data = fetch_movie_data(movie_name)

        if status == "watched":
            rating = int(request.form["rating"])
            movie = Movie(movie_name, status, rating,
                         poster=api_data.get("poster", ""),
                         year=api_data.get("year", ""),
                         genre=api_data.get("genre", ""),
                         director=api_data.get("director", ""),
                         plot=api_data.get("plot", ""),
                         imdb_rating=api_data.get("imdb_rating", ""))
        else:
            movie = Movie(movie_name, status, "Not Watched Yet",
                         poster=api_data.get("poster", ""),
                         year=api_data.get("year", ""),
                         genre=api_data.get("genre", ""),
                         director=api_data.get("director", ""),
                         plot=api_data.get("plot", ""),
                         imdb_rating=api_data.get("imdb_rating", ""))

        movies.append(movie)
        save_movies(movies)
        flash(f"✓ {movie_name} added to your collection")
        return redirect(url_for("movies"))

    return render_template("addmovie.html", active_page="add")


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        search_name = request.form["search_name"]
        movies = load_movies()
        series_list = load_series()

        found_movie = find_movie(search_name, movies)
        found_series = find_series(search_name, series_list)

        results = {
            "movie": found_movie,
            "series": found_series
        }

        if not found_movie and not found_series:
            flash(f"Nothing found for '{search_name}'")

        return render_template("search.html",
            results=results,
            searched=True,
            active_page="search"
        )

    return render_template("search.html",
        results={},
        searched=False,
        active_page="search"
    )

@app.route("/watchlist")
@login_required
def watchlist():
    movies = load_movies()
    series_list = load_series()

    watchlist_movies = [m for m in movies if m.is_watchlist()]
    watchlist_series = [s for s in series_list if s.is_watchlist()]

    return render_template("watchlist.html",
        movies=watchlist_movies,
        series=watchlist_series,
        active_page="watchlist"
    )


@app.route("/markwatched", methods=["GET", "POST"])
@login_required
def markwatched():
    if request.method == "POST":
        movie_name = request.form["movie_name"]
        rating = int(request.form["rating"]) if request.form["rating"] else 5
        movies = load_movies()
        movie = find_movie(movie_name, movies)

        if movie:
            if movie.is_watchlist():
                movie.mark_watched(rating)
                save_movies(movies)
                flash(f"✓ {movie_name} marked as watched")
                return redirect(url_for("movies"))
            else:
                flash(f"{movie_name} is already watched")
                return redirect(url_for("watchlist"))
        else:
            flash("Movie not found in your collection")
            return redirect(url_for("watchlist"))

    return render_template("markwatched.html", active_page="markwatched")


@app.route("/deletemovie", methods=["GET", "POST"])
@login_required
def deletemovie():
    if request.method == "POST":
        movie_name = request.form["movie_name"]
        movies = load_movies()
        movie = find_movie(movie_name, movies)

        if movie:
            database = db.get_db()
            database.execute("DELETE FROM movies WHERE id = ? AND user_id = ?", (movie.db_id, current_user.id))
            database.commit()
            flash(f"✓ {movie_name} removed from your collection")
            return redirect(url_for("movies"))
        else:
            flash("Movie not found in your collection")
            return redirect(url_for("movies"))

    return render_template("deletemovie.html", active_page="delete")

@app.route("/editrating", methods=["GET", "POST"])
@login_required
def editrating():
    if request.method == "POST":
        movie_name = request.form["movie_name"]
        new_rating = int(request.form["rating"])
        movies = load_movies()
        movie = find_movie(movie_name, movies)

        if movie:
            if movie.is_watched():
                movie.update_rating(new_rating)
                save_movies(movies)
                flash(f"✓ {movie_name} rating updated to {new_rating}/10")
                return redirect(url_for("movies"))
            else:
                flash(f"{movie_name} is in your watchlist — watch it first")
                return redirect(url_for("movies"))
        else:
            flash("Movie not found in your collection")
            return redirect(url_for("movies"))

    return render_template("editrating.html", active_page="editrating")


@app.route("/statistics")
@login_required
def statistics():
    movies = load_movies()
    series_list = load_series()

    # Movie stats
    total_movies = len(movies)
    watched_movies = [m for m in movies if m.is_watched()]
    watchlist_movies = [m for m in movies if m.is_watchlist()]
    ratings = [m.rating for m in watched_movies if isinstance(m.rating, int)]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0
    top_movie = max(watched_movies, key=lambda m: m.rating if isinstance(m.rating, int) else 0) if watched_movies else None

    # Genre stats for movies
    all_genres = []
    for m in movies:
        if m.genre:
            for g in m.genre.split(","):
                all_genres.append(g.strip())
    top_genre = max(set(all_genres), key=all_genres.count) if all_genres else "N/A"

    # Show stats
    total_shows = len(series_list)
    completed_shows = [s for s in series_list if s.is_completed()]
    watching_shows = [s for s in series_list if s.is_watching()]
    paused_shows = [s for s in series_list if s.is_paused()]
    watchlist_shows = [s for s in series_list if s.is_watchlist()]
    anime_shows = [s for s in series_list if s.is_anime()]
    tv_shows = [s for s in series_list if s.is_tv()]

    # Total episodes watched across all anime
    total_eps_watched = sum(s.episodes_watched for s in series_list if s.is_anime())

    # Overall
    total_collection = total_movies + total_shows

    return render_template("statistics.html",
        active_page="stats",
        # Overall
        total_collection=total_collection,
        total_movies=total_movies,
        total_shows=total_shows,
        # Movies
        watched_count=len(watched_movies),
        watchlist_count=len(watchlist_movies),
        avg_rating=avg_rating,
        top_genre=top_genre,
        top_movie=top_movie,
        # Shows
        completed_shows=len(completed_shows),
        watching_shows=len(watching_shows),
        paused_shows=len(paused_shows),
        watchlist_shows=len(watchlist_shows),
        anime_count=len(anime_shows),
        tv_count=len(tv_shows),
        total_eps_watched=total_eps_watched,
    )


@app.route("/toprated")
@login_required
def toprated():
    movies = load_movies()
    series_list = load_series()

    # Top movies — by personal rating
    watched_movies = [m for m in movies if m.is_watched()]
    sorted_movies = sorted(watched_movies,
        key=lambda m: m.rating if isinstance(m.rating, int) else 0,
        reverse=True)[:10]

    # Top shows — by personal rating (only rated ones)
    rated_shows = [s for s in series_list if s.rating and isinstance(s.rating, int) and s.rating > 0]
    sorted_shows = sorted(rated_shows, key=lambda s: s.rating, reverse=True)[:10]

    return render_template("toprated.html",
        movies=sorted_movies,
        shows=sorted_shows,
        active_page="toprated"
    )


@app.route("/unwatch", methods=["POST"])
@login_required
def unwatch():
    movie_name = request.form["movie_name"]
    movies = load_movies()
    movie = find_movie(movie_name, movies)

    if movie:
        if movie.is_watched():
            movie.mark_unwatched()
            save_movies(movies)
            flash(f"↩ {movie_name} moved back to watchlist")
            return redirect(url_for("movies"))
        else:
            flash(f"{movie_name} is already in watchlist")
            return redirect(url_for("movies"))
    else:
        flash("Movie not found")
        return redirect(url_for("movies"))

@app.route("/series")
@login_required
def series():
    sort_by = request.args.get("sort")
    if sort_by:
        session["series_sort"] = sort_by
    else:
        sort_by = session.get("series_sort", "recent")

    series_list = load_series(sort_by)
    return render_template("series.html",
        series_list=series_list,
        current_sort=sort_by,
        active_page="series"
    )

@app.route("/addseries", methods=["GET", "POST"])
@login_required
def addseries():
    if request.method == "POST":
        title = request.form["title"]
        status = request.form["status"]
        show_type = request.form.get("show_type", "tv")
        manual_poster = request.form.get("manual_poster", "").strip()
        rating = int(request.form.get("rating", 0)) if request.form.get("rating", "").strip() else 0

        series_list_check = load_series()
        if find_series(title, series_list_check):
            flash(f"{title} is already in your shows")
            return redirect(url_for("series"))

        api_data = fetch_series_data(title)
        total_seasons = int(api_data.get("total_seasons", 0))

        poster = api_data.get("poster", "")
        if not poster or poster == "N/A":
            poster = manual_poster

        if show_type == "anime":
            episodes_watched = int(request.form.get("episodes_watched", 0))
            total_episodes = int(request.form.get("total_episodes", 0))

            if status == "completed":
                if total_episodes > 0:
                    episodes_watched = total_episodes
                else:
                    fetched_total = 0
                    for s in range(1, total_seasons + 1):
                        fetched_total += fetch_season_episodes(title, s)
                    if fetched_total > 0:
                        total_episodes = fetched_total
                        episodes_watched = fetched_total

            new_series = Series(
                title=title,
                status=status,
                show_type="anime",
                current_season=1,
                current_episode=0,
                episodes_in_current_season=0,
                total_seasons=total_seasons,
                episodes_watched=episodes_watched,
                total_episodes=total_episodes,
                rating=rating,
                poster=poster,
                year=api_data.get("year", ""),
                genre=api_data.get("genre", ""),
                imdb_rating=api_data.get("imdb_rating", "")
            )

        else:
            current_season = int(request.form.get("current_season", 1))
            current_episode = int(request.form.get("current_episode", 0))
            episodes_in_season = fetch_season_episodes(title, current_season)

            if status == "completed" and total_seasons > 0:
                current_season = total_seasons
                episodes_in_season = fetch_season_episodes(title, total_seasons)
                current_episode = episodes_in_season

            new_series = Series(
                title=title,
                status=status,
                show_type="tv",
                current_season=current_season,
                current_episode=current_episode,
                episodes_in_current_season=episodes_in_season,
                total_seasons=total_seasons,
                episodes_watched=0,
                total_episodes=0,
                rating=rating,
                poster=poster,
                year=api_data.get("year", ""),
                genre=api_data.get("genre", ""),
                imdb_rating=api_data.get("imdb_rating", "")
            )

        series_list = load_series()
        series_list.append(new_series)
        save_series(series_list)
        flash(f"✓ {title} added to your shows")
        return redirect(url_for("series"))

    return render_template("addseries.html", active_page="add")

@app.route("/updateseries", methods=["POST"])
@login_required
def updateseries():
    title = request.form["title"]
    new_status = request.form["status"]
    new_rating = request.form.get("rating", "").strip()

    series_list = load_series()
    s = find_series(title, series_list)

    if s:
        s.status = new_status

        # Save personal rating if provided
        if new_rating and new_rating.isdigit():
            s.rating = int(new_rating)

        if s.show_type == "anime":
            episodes_watched = int(request.form.get("episodes_watched", 0))
            total_episodes = int(request.form.get("total_episodes", s.total_episodes))
            s.total_episodes = total_episodes

            if new_status == "completed" and total_episodes > 0:
                s.episodes_watched = total_episodes
            else:
                s.episodes_watched = min(episodes_watched, total_episodes) if total_episodes > 0 else episodes_watched

        else:
            new_season = int(request.form.get("current_season", s.current_season))
            new_episode = int(request.form.get("current_episode", s.current_episode))
            s.current_episode = new_episode

            if new_season != s.current_season:
                s.current_season = new_season
                s.episodes_in_current_season = fetch_season_episodes(title, new_season)

            if new_status == "completed" and s.total_seasons > 0:
                s.current_season = s.total_seasons
                s.episodes_in_current_season = fetch_season_episodes(title, s.total_seasons)
                s.current_episode = s.episodes_in_current_season

        save_series(series_list)
        flash(f"✓ {title} updated")
    else:
        flash("Show not found")

    return redirect(url_for("series"))

@app.route("/deleteseries", methods=["POST"])
@login_required
def deleteseries():
    title = request.form["title"]
    series_list = load_series()
    s = find_series(title, series_list)

    if s:
        database = db.get_db()
        database.execute("DELETE FROM series WHERE id = ? AND user_id = ?", (s.db_id, current_user.id))
        database.commit()
    else:
        flash("Show not found")

    return redirect(url_for("series"))

@app.route("/add")
@login_required
def add():
    return render_template("add.html", active_page="add")

@app.route("/suggest")
@login_required
def suggest():
    query = request.args.get("q", "").lower().strip()
    if len(query) < 1:
        return jsonify([])

    movies = load_movies()
    series_list = load_series()
    results = []

    for m in movies:
        if m.title.lower().startswith(query):
            results.append({
                "title": m.title,
                "type": "movie",
                "year": m.year,
                "status": m.status
            })

    for s in series_list:
        if s.title.lower().startswith(query):
            results.append({
                "title": s.title,
                "type": "anime" if s.is_anime() else "tv",
                "year": s.year,
                "status": s.status
            })

    results.sort(key=lambda x: x["title"].lower())
    return jsonify(results[:8])


@app.route("/togglefavorite", methods=["POST"])
@login_required
def togglefavorite():
    movie_name = request.form["movie_name"]
    movies = load_movies()
    movie = find_movie(movie_name, movies)
    if movie:
        movie.is_favorite = not movie.is_favorite
        save_movies(movies)
        return jsonify({"success": True, "is_favorite": movie.is_favorite})
    return jsonify({"success": False}), 404


@app.route("/toggleseriesfavorite", methods=["POST"])
@login_required
def toggleseriesfavorite():
    title = request.form["title"]
    series_list = load_series()
    s = find_series(title, series_list)
    if s:
        s.is_favorite = not s.is_favorite
        save_series(series_list)
        return jsonify({"success": True, "is_favorite": s.is_favorite})
    return jsonify({"success": False}), 404

# ── Phase 4: Detail pages (TMDb-first artwork, OMDB/local as fallback) ──

@app.route("/movie/<title>")
@login_required
def moviedetail(title):
    movies = load_movies()
    movie = find_movie(title, movies)

    if not movie:
        flash("Movie not found in your collection")
        return redirect(url_for("movies"))

    # OMDB — plot/actors/imdb_id aren't persisted, so fetch live (also our fallback source)
    extra = fetch_movie_data(movie.title)
    plot = extra.get("plot", "") or "No synopsis available."
    director = movie.director or extra.get("director", "")
    imdb_id = extra.get("imdb_id", "")

    # TMDb — primary source for artwork, cast photos, and real similar titles
    tmdb_hit = tmdb.search_movie(movie.title, movie.year)
    tmdb_data = tmdb.get_movie_details(tmdb_hit["id"]) if tmdb_hit else {}

    backdrop = tmdb.img(tmdb_data.get("backdrop_path"), "w1280")
    poster = tmdb.img(tmdb_data.get("poster_path"), "w500") or movie.poster
    logo = tmdb.best_logo(tmdb_data) if tmdb_data else ""
    runtime = tmdb_data.get("runtime")
    runtime_display = tmdb.format_runtime(runtime)
    if tmdb_data.get("overview"):
        plot = tmdb_data["overview"]

    cast = []
    if tmdb_data.get("credits"):
        for c in tmdb_data["credits"].get("cast", [])[:12]:
            cast.append({
                "name": c.get("name", ""),
                "role": c.get("character", "") or "Cast",
                "photo": tmdb.img(c.get("profile_path"), "w185"),
            })
        for c in tmdb_data["credits"].get("crew", []):
            if c.get("job") == "Director":
                director = c.get("name", director)
                break
    elif extra.get("actors"):
        # OMDB fallback — no photos, template shows initials avatar instead
        for name in extra["actors"].split(","):
            cast.append({"name": name.strip(), "role": "Cast", "photo": ""})

    similar = []
    owned_titles_lower = {m.title.lower() for m in movies}
    for s in tmdb.get_recommendations(tmdb_data):
            similar.append({
                "title": s.get("title", ""),
                "poster": tmdb.img(s.get("poster_path"), "w342"),
                "rating": round(s.get("vote_average") or 0, 1),
                "url": f"https://www.themoviedb.org/movie/{s.get('id')}",
                "type": "movie",
                "owned": s.get("title", "").lower() in owned_titles_lower,
            })
    if not similar and movie.genre:
        # last-resort fallback — your own collection, same primary genre
        primary_genre = movie.genre.split(",")[0].strip().lower()
        for m in movies:
            if m.title != movie.title and primary_genre in m.genre.lower():
                similar.append({
                    "title": m.title,
                    "poster": m.poster,
                    "rating": m.imdb_rating,
                    "url": url_for("moviedetail", title=m.title),
                })
        similar = similar[:10]

    return render_template("detail.html",
        item=movie,
        item_type="movie",
        plot=plot,
        director=director,
        cast=cast,
        imdb_id=imdb_id,
        backdrop=backdrop,
        poster=poster,
        logo=logo,
        runtime=runtime,
        runtime_display=runtime_display,
        similar=similar,
        active_page="movies"
    )


@app.route("/show/<title>")
@login_required
def showdetail(title):
    series_list = load_series()
    show = find_series(title, series_list)

    if not show:
        flash("Show not found in your collection")
        return redirect(url_for("series"))

    # OMDB fallback source
    extra = fetch_series_extra(show.title)
    plot = extra.get("plot", "") or "No synopsis available."
    director = extra.get("creator", "")
    imdb_id = extra.get("imdb_id", "")

    # TMDb — primary source
    tmdb_hit = tmdb.search_tv(show.title, show.year)
    tmdb_data = tmdb.get_tv_details(tmdb_hit["id"]) if tmdb_hit else {}

    backdrop = tmdb.img(tmdb_data.get("backdrop_path"), "w1280")
    poster = tmdb.img(tmdb_data.get("poster_path"), "w500") or show.poster
    logo = tmdb.best_logo(tmdb_data) if tmdb_data else ""
    if tmdb_data.get("overview"):
        plot = tmdb_data["overview"]
    if tmdb_data.get("created_by"):
        director = ", ".join(c["name"] for c in tmdb_data["created_by"]) or director

    ert = tmdb_data.get("episode_run_time") or []
    runtime = ert[0] if ert else None
    runtime_display = tmdb.format_runtime(runtime)

    cast = []
    if tmdb_data.get("credits"):
        for c in tmdb_data["credits"].get("cast", [])[:12]:
            cast.append({
                "name": c.get("name", ""),
                "role": c.get("character", "") or "Cast",
                "photo": tmdb.img(c.get("profile_path"), "w185"),
            })
    elif extra.get("actors"):
        for name in extra["actors"].split(","):
            cast.append({"name": name.strip(), "role": "Cast", "photo": ""})

    # episode strip for TV shows — supports browsing other seasons via ?season=N
    viewing_season = request.args.get("season", type=int) or show.current_season
    if show.total_seasons and viewing_season > show.total_seasons:
        viewing_season = show.total_seasons
    if viewing_season < 1:
        viewing_season = 1

    episodes = []
    season_poster = ""
    if show.is_tv() and viewing_season:
        if tmdb_hit:
            season_data = tmdb.get_season(tmdb_hit["id"], viewing_season)
            season_poster = tmdb.img(season_data.get("poster_path"), "w300")
            for e in season_data.get("episodes", []):
                num = e.get("episode_number", 0)
                watched = (viewing_season < show.current_season or
                           (viewing_season == show.current_season and num <= show.current_episode))
                episodes.append({
                    "number": num,
                    "title": e.get("name", f"Episode {num}"),
                    "still": tmdb.img(e.get("still_path"), "w300"),
                    "rating": round(e.get("vote_average") or 0, 1),
                    "runtime": e.get("runtime"),
                    "runtime_display": tmdb.format_runtime(e.get("runtime")),
                    "overview": e.get("overview", ""),
                    "air_date": e.get("air_date", ""),
                    "watched": watched,
                })
        if not episodes:
            # OMDB fallback — no still images, template shows generated gradient art instead
            for ep in fetch_episode_list(show.title, viewing_season):
                num = int(ep.get("Episode", 0))
                watched = (viewing_season < show.current_season or
                           (viewing_season == show.current_season and num <= show.current_episode))
                rating = ep.get("imdbRating")
                episodes.append({
                    "number": num,
                    "title": ep.get("Title", f"Episode {num}"),
                    "still": "",
                    "rating": float(rating) if rating and rating != "N/A" else None,
                    "runtime": None,
                    "runtime_display": "",
                    "overview": "",
                    "air_date": ep.get("Released", ""),
                    "watched": watched,
                })

    similar = []
    owned_titles_lower = {sh.title.lower() for sh in series_list}
    for s in tmdb.get_recommendations(tmdb_data, is_anime=show.is_anime()):
            similar.append({
                "title": s.get("name", ""),
                "poster": tmdb.img(s.get("poster_path"), "w342"),
                "rating": round(s.get("vote_average") or 0, 1),
                "url": f"https://www.themoviedb.org/tv/{s.get('id')}",
                "type": "series",
                "owned": s.get("name", "").lower() in owned_titles_lower,
            })
    if not similar and show.genre:
        primary_genre = show.genre.split(",")[0].strip().lower()
        for s in series_list:
            if s.title != show.title and primary_genre in s.genre.lower():
                similar.append({
                    "title": s.title,
                    "poster": s.poster,
                    "rating": s.imdb_rating,
                    "url": url_for("showdetail", title=s.title),
                })
        similar = similar[:10]

    return render_template("detail.html",
        item=show,
        item_type="series",
        plot=plot,
        director=director,
        cast=cast,
        imdb_id=imdb_id,
        backdrop=backdrop,
        poster=poster,
        logo=logo,
        runtime=runtime,
        runtime_display=runtime_display,
        episodes=episodes,
        season_poster=season_poster,
        viewing_season=viewing_season,
        similar=similar,
        active_page="series"
    )

@app.route("/foryou")
@login_required
def foryou():
    movies = load_movies()
    series_list = load_series()

    owned_titles = {m.title.lower() for m in movies} | {s.title.lower() for s in series_list}
    profile = build_profile(movies, series_list)

    if not profile["seeds"]:
        return render_template("foryou.html",
            active_page="foryou",
            recommendations=[],
            top_genres=[],
            has_ratings=False,
        )

    recommendations = gather_recommendations(profile, owned_titles)

    return render_template("foryou.html",
        active_page="foryou",
        recommendations=recommendations,
        top_genres=profile["top_genres"],
        has_ratings=True,
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = auth.User.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.username}")
            return redirect(url_for("home"))
        flash("Wrong username or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("login"))

UPLOAD_FOLDER = "static/avatars"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


@app.route("/profile/photo", methods=["POST"])
@login_required
def upload_profile_photo():
    file = request.files.get("photo")

    if not file or not file.filename:
        flash("No file selected")
        return redirect(request.referrer or url_for("home"))

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        flash("Please upload a PNG, JPG, or WEBP image")
        return redirect(request.referrer or url_for("home"))

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    filename = secure_filename(f"user_{current_user.id}.{ext}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # stored as a static/-relative path so {{ url_for('static', filename=...) }} works directly
    database = db.get_db()
    database.execute(
        "UPDATE users SET profile_image = ? WHERE id = ?",
        (f"avatars/{filename}", current_user.id),
    )
    database.commit()

    flash("Profile photo updated")
    return redirect(request.referrer or url_for("home"))

@app.route("/quickadd", methods=["POST"])
@login_required
def quickadd():
    title = request.form["title"]
    kind = request.form["kind"]  # "movie" or "series"

    if kind == "movie":
        movies = load_movies()
        if find_movie(title, movies):
            return jsonify({"success": False, "message": "Already in your collection"})
        api_data = fetch_movie_data(title)
        movie = Movie(title, "watchlist", "Not Watched Yet",
                     poster=api_data.get("poster", ""),
                     year=api_data.get("year", ""),
                     genre=api_data.get("genre", ""),
                     director=api_data.get("director", ""),
                     plot=api_data.get("plot", ""),
                     imdb_rating=api_data.get("imdb_rating", ""))
        movies.append(movie)
        save_movies(movies)
        return jsonify({"success": True})

    else:
        series_list = load_series()
        if find_series(title, series_list):
            return jsonify({"success": False, "message": "Already in your collection"})
        api_data = fetch_series_data(title)
        total_seasons = int(api_data.get("total_seasons", 0))
        new_series = Series(
            title=title, status="watchlist", show_type="tv",
            current_season=1, current_episode=0,
            episodes_in_current_season=0,
            total_seasons=total_seasons,
            poster=api_data.get("poster", ""),
            year=api_data.get("year", ""),
            genre=api_data.get("genre", ""),
            imdb_rating=api_data.get("imdb_rating", ""),
        )
        series_list.append(new_series)
        save_series(series_list)
        return jsonify({"success": True})
@app.route("/suggest_external")
@login_required
def suggest_external():
    query = request.args.get("q", "").strip()
    media_type = request.args.get("type", "movie")
    if len(query) < 2:
        return jsonify([])

    try:
        omdb_type = "movie" if media_type == "movie" else "series"
        url = f"http://www.omdbapi.com/?s={query}&type={omdb_type}&apikey={API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        results = []
        if data.get("Search"):
            for item in data["Search"][:6]:
                results.append({
                    "title": item.get("Title", ""),
                    "year": item.get("Year", ""),
                })
        return jsonify(results)
    except Exception as e:
        return jsonify([])
if __name__ == "__main__":
    app.run(debug=True)