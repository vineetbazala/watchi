import requests
from config import TMDB_API_KEY

TMDB_BASE = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p"

ANIMATION_GENRE_ID = 16


def img(path, size="original"):
    """Build a full TMDb image URL from a path like '/abc123.jpg'. Returns '' if no path."""
    if not path:
        return ""
    return f"{IMG_BASE}/{size}{path}"


def _get(path, params=None):
    params = dict(params or {})
    params["api_key"] = TMDB_API_KEY
    last_error = None
    for attempt in range(2):
        try:
            r = requests.get(f"{TMDB_BASE}{path}", params=params, timeout=10)
            if r.status_code == 200:
                return r.json()
            last_error = f"status {r.status_code}: {r.text[:200]}"
        except Exception as e:
            last_error = e
    print(f"[tmdb] FAILED {path} params={ {k:v for k,v in params.items() if k != 'api_key'} } -> {last_error}")
    return {}


def search_movie(title, year=None):
    """Find the best-matching TMDb movie for a title (+ optional year to disambiguate)."""
    params = {"query": title}
    if year:
        digits = "".join(c for c in str(year) if c.isdigit())[:4]
        if digits:
            params["year"] = digits
    data = _get("/search/movie", params)
    results = data.get("results", [])
    return results[0] if results else None


def search_tv(title, year=None):
    """Find the best-matching TMDb TV show for a title (+ optional year to disambiguate)."""
    params = {"query": title}
    if year:
        digits = "".join(c for c in str(year) if c.isdigit())[:4]
        if digits:
            params["first_air_date_year"] = digits
    data = _get("/search/tv", params)
    results = data.get("results", [])
    return results[0] if results else None


def get_movie_details(tmdb_id):
    """Full movie record: backdrop/poster paths, credits (cast+crew), similar/recommendations, logos."""
    return _get(f"/movie/{tmdb_id}", {
        "append_to_response": "credits,similar,recommendations,images",
        "include_image_language": "en,null"
    })


def get_tv_details(tmdb_id):
    """Full TV record: backdrop/poster paths, credits, similar/recommendations, logos, created_by."""
    return _get(f"/tv/{tmdb_id}", {
        "append_to_response": "credits,similar,recommendations,images",
        "include_image_language": "en,null"
    })


def get_season(tmdb_id, season_number):
    """Full season record: season poster + list of episodes (each with its own still image)."""
    return _get(f"/tv/{tmdb_id}/season/{season_number}")


def get_recommendations(tmdb_data, is_anime=False, limit=10):
    
    if not tmdb_data:
        return []

    source_genres = {g["id"] for g in (tmdb_data.get("genres") or [])}

    candidates = (tmdb_data.get("recommendations") or {}).get("results") or []
    if not candidates:
        candidates = (tmdb_data.get("similar") or {}).get("results") or []

    scored = []
    for c in candidates:
        c_genres = set(c.get("genre_ids") or [])

        if is_anime:
            if c.get("original_language") != "ja" or ANIMATION_GENRE_ID not in c_genres:
                continue
        else:
            if not (source_genres & c_genres):
                continue

        overlap = len(source_genres & c_genres)
        score = overlap * 10 + (c.get("vote_average") or 0)
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:limit]]


def best_logo(tmdb_data):
    """Pick a usable logo image (PNG, English if possible) from an append_to_response=images payload."""
    logos = (tmdb_data.get("images") or {}).get("logos") or []
    if not logos:
        return ""
    english = [l for l in logos if l.get("iso_639_1") == "en"]
    pick = (english or logos)[0]
    return img(pick.get("file_path"), "w500")


def format_runtime(minutes):
    """126 -> '2h 6m'. Returns '' if no runtime available."""
    if not minutes:
        return ""
    minutes = int(minutes)
    h, m = divmod(minutes, 60)
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"