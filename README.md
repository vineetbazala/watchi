# 🎬 Watchi

A personal movie and TV show tracker built with Flask. Track what you've watched, maintain a watchlist, rate titles, browse cast and episode details, and get personalized recommendations — all in a clean, dark-themed web app.

This is a personal learning project built while studying B.Sc. Computer Applications, as a way to practice full-stack web development beyond classroom exercises.

---

## Features

- **Movie & TV tracking** — add titles to your watchlist, mark as watched, rate 1–10
- **Anime support** — separate episode-tracking logic for anime vs. regular TV seasons
- **Rich detail pages** — posters, backdrops, cast photos, episode stills, and "similar titles" pulled live from TMDb
- **Quick-add recommendations** — add a suggested title straight to your watchlist with one click, no page reload
- **Personalized "For You" page** — recommendations generated from your own highly-rated titles
- **Stats dashboard** — totals, average ratings, top genre, completion stats
- **User accounts** — login system with per-user data isolation
- **Profile customization** — upload your own avatar
- **Dark/light mode** toggle
- **Sorting & favorites** — sort by recently added, title, or mark favorites
- **Responsive card UI** — flip-card design with hover animations and image skeleton loaders

## Tech Stack

- **Backend:** Python, Flask, Flask-Login
- **Database:** SQLite
- **APIs:** [OMDB API](https://www.omdbapi.com/) (movie/show metadata), [TMDb API](https://www.themoviedb.org/documentation/api) (posters, cast, episodes, recommendations)
- **Frontend:** HTML, CSS, vanilla JavaScript (Jinja2 templating)

## Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/vineetbazala/watchi.git
   cd watchi
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your own API keys:
   ```
   API_KEY=your_omdb_api_key
   TMDB_API_KEY=your_tmdb_api_key
   FLASK_SECRET_KEY=any_random_string
   ```
   - Get a free OMDB key at [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx)
   - Get a free TMDb key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)

4. Initialize the database:
   ```bash
   python run_init_db.py
   ```

5. Run the app:
   ```bash
   python app.py
   ```
   Visit `http://127.0.0.1:5000` in your browser.

## Screenshots

<img width="1597" height="832" alt="Screenshot 2026-09-22 114909" src="https://github.com/user-attachments/assets/245f82d9-83ad-4b1a-a784-eb779b886140" />


<img width="1597" height="830" alt="Screenshot 2026-09-22 114932" src="https://github.com/user-attachments/assets/13446467-dc59-4ec2-b190-cb0f6f1a0317" />

<img width="1593" height="820" alt="Screenshot 2026-09-22 115239" src="https://github.com/user-attachments/assets/4e7ddc34-c75b-4fd2-b344-96f2d3bf0dab" />

<img width="1585" height="837" alt="Screenshot 2026-09-22 115258" src="https://github.com/user-attachments/assets/d3c96b32-a141-4dcc-a073-72bcf53cf3b5" />

---

## On the use of AI in this project

I built Watchi as a learning project, and I want to be upfront about how it was built: **I used AI assistants (Claude and ChatGPT) throughout development**, and I think that's worth explaining honestly rather than glossing over.

**How I used them:**
- Debugging errors I ran into (tracebacks, silent failures, logic bugs)
- Writing and refining CSS for layout issues I couldn't solve on my own yet
- Explaining *why* something was broken, not just handing me a fix — I asked "what's wrong and why" far more often than "just do it for me"
- Getting a second pair of eyes on features before I built them (e.g. how to structure the recommendations system, how session-based sorting should work)
- Setting up Git and GitHub for the first time — I had never used either before this project, and walked through the entire process (repository creation, `.gitignore`, staging, committing, authentication) step by step

**What this means about my involvement:**
- Every line of code in this repo passed through my own hands — I typed it, read it, and (with AI help) understood what it does and why
- The overall architecture, feature decisions, and UI direction were mine — I decided what Watchi should do and how it should feel to use
- Real bugs came up throughout (a mistyped environment variable name that silently broke TMDb integration for days, a sort-order bug from a database migration, an `IntegrityError` from a duplicate title) and I worked through diagnosing and fixing each one rather than skipping past them
- This was my **first real Flask project** and my **first time using Git/GitHub** — both of those learning curves are visible in how this project came together

I'm sharing this openly because I think claiming sole, unassisted authorship of every design and debugging decision here would be dishonest, and because I'd rather be upfront about how I actually learn and build than pretend otherwise. If you're evaluating this project, I'm happy to walk through any part of the codebase and explain the reasoning behind it.

---

## Project Status

Actively developed as a personal project. Planned improvements: mobile-responsive layout, live deployment, and a preview/add flow for recommended titles that aren't yet in the user's collection.

## Author

Built by **Vineet Bazala** — a B.Sc. Computer Applications student learning full-stack web development.

[GitHub](https://github.com/vineetbazala)
