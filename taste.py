import tmdb


def build_profile(movies, series_list):
    """Separates your rated-7+ titles into movie seeds, TV seeds, and anime
    seeds — three separate buckets, each sorted by rating — plus an
    aggregate of your most common genres. Anime and TV are kept apart so
    one type can't crowd the other out of the seed list entirely."""
    from collections import Counter
    genre_weight = Counter()
    movie_seeds = []
    tv_seeds = []
    anime_seeds = []

    for m in movies:
        if isinstance(m.rating, int) and m.rating >= 7:
            weight = m.rating - 6  # 7->1 ... 10->4
            for g in (m.genre or "").split(","):
                g = g.strip()
                if g:
                    genre_weight[g] += weight
            movie_seeds.append({
                "title": m.title, "type": "movie", "year": m.year,
                "rating": m.rating, "is_anime": False,
            })

    for s in series_list:
        if isinstance(s.rating, int) and s.rating >= 7:
            weight = s.rating - 6
            for g in (s.genre or "").split(","):
                g = g.strip()
                if g:
                    genre_weight[g] += weight
            seed = {
                "title": s.title, "type": "series", "year": s.year,
                "rating": s.rating, "is_anime": s.is_anime(),
            }
            (anime_seeds if s.is_anime() else tv_seeds).append(seed)

    movie_seeds.sort(key=lambda x: x["rating"], reverse=True)
    tv_seeds.sort(key=lambda x: x["rating"], reverse=True)
    anime_seeds.sort(key=lambda x: x["rating"], reverse=True)

    return {
        "top_genres": [g for g, _ in genre_weight.most_common(5)],
        "movie_seeds": movie_seeds,
        "tv_seeds": tv_seeds,
        "anime_seeds": anime_seeds,
        "seeds": movie_seeds + tv_seeds + anime_seeds,  # used only to check "do we have any data at all"
    }


def gather_recommendations(profile, owned_titles,
                            max_seeds_per_type=3, per_seed_limit=4, max_results=24):
    """Takes up to max_seeds_per_type from movies, TV, AND anime
    separately (so all three are guaranteed representation if you've
    rated any), and caps each seed's contribution to per_seed_limit new
    candidates."""
    candidates = {}

    chosen_seeds = (
        profile["movie_seeds"][:max_seeds_per_type] +
        profile["tv_seeds"][:max_seeds_per_type] +
        profile["anime_seeds"][:max_seeds_per_type]
    )

    for seed in chosen_seeds:
        if seed["type"] == "movie":
            hit = tmdb.search_movie(seed["title"], seed["year"])
            if not hit:
                print(f"[taste] no TMDb match for movie seed: {seed['title']}")
                continue
            details = tmdb.get_movie_details(hit["id"])
            recs = tmdb.get_recommendations(details)
            kind = "movie"
        else:
            hit = tmdb.search_tv(seed["title"], seed["year"])
            if not hit:
                print(f"[taste] no TMDb match for series seed: {seed['title']}")
                continue
            details = tmdb.get_tv_details(hit["id"])
            recs = tmdb.get_recommendations(details, is_anime=seed["is_anime"])
            kind = "series"

        added = 0
        for r in recs:
            if added >= per_seed_limit:
                break

            title = r.get("title") or r.get("name") or ""
            if not title or title.lower() in owned_titles:
                continue

            key = (kind, r.get("id"))
            if key not in candidates:
                candidates[key] = {
                    "id": r.get("id"),
                    "title": title,
                    "type": kind,
                    "is_anime": seed.get("is_anime", False),
                    "poster": tmdb.img(r.get("poster_path"), "w342"),
                    "rating": round(r.get("vote_average") or 0, 1),
                    "reasons": [],
                    "score": 0,
                }
            candidates[key]["reasons"].append(seed["title"])
            candidates[key]["score"] += seed["rating"]
            added += 1

        print(f"[taste] seed '{seed['title']}' ({kind}, {seed['rating']}/10): added {added} candidates")

    ranked = sorted(
        candidates.values(),
        key=lambda c: (len(c["reasons"]), c["score"]),
        reverse=True,
    )
    return ranked[:max_results]