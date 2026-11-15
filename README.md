# 🎬 Watchi

A movie and TV show tracker built with Flask. Track what you've watched, keep a watchlist, rate titles, browse cast and episode details, and get personalized recommendations. It works on desktop and on your phone, in dark and light mode.

Built as a personal learning project while studying B.Sc. Computer Applications, to practice full-stack web development beyond classroom exercises.

## 🔗 Live demo

**https://vineetbazala.pythonanywhere.com**

Log in with the demo account:

| Username | Password |
|----------|----------|
| `vineet@678` | `9876543210` |

The demo account is shared and public, with sample movies and shows already added. Please don't store anything personal in it. The site runs on a free hosting plan, so it may occasionally be offline.

---

## Features

- **Movie & TV tracking**: add titles to your watchlist, mark them as watched, rate 1–10
- **Anime support**: separate episode-tracking logic for anime and regular TV seasons
- **Rich detail pages**: posters, backdrops, cast photos, episode stills, and "similar titles" pulled live from TMDb
- **Quick-add recommendations**: add a suggested title to your watchlist with one click, no page reload
- **Personalized "For You" page**: recommendations generated from your own highest-rated titles
- **Stats dashboard**: totals, average ratings, top genre, completion stats
- **User accounts**: login system with per-user data isolation
- **Profile customization**: upload your own avatar
- **Mobile-friendly design**: responsive layout with a collapsing menu, tuned for phone screens
- **Dark and light mode** with a toggle
- **Sorting and favorites**: sort by recently added or title, and mark favorites
- **Flip-card UI**: hover animations and image skeleton loaders

## Tech stack

- **Backend:** Python, Flask, Flask-Login
- **Database:** SQLite
- **APIs:** [OMDB API](https://www.omdbapi.com/) (movie/show metadata), [TMDb API](https://www.themoviedb.org/documentation/api) (posters, cast, episodes, recommendations)
- **Frontend:** HTML, CSS, vanilla JavaScript (Jinja2 templating)
- **Hosting:** PythonAnywhere (free plan)

## Screenshots

<img width="1597" height="832" alt="Screenshot 2026-09-22 114909" src="https://github.com/user-attachments/assets/245f82d9-83ad-4b1a-a784-eb779b886140" />


<img width="1597" height="830" alt="Screenshot 2026-09-22 114932" src="https://github.com/user-attachments/assets/13446467-dc59-4ec2-b190-cb0f6f1a0317" />

<img width="1593" height="820" alt="Screenshot 2026-09-22 115239" src="https://github.com/user-attachments/assets/4e7ddc34-c75b-4fd2-b344-96f2d3bf0dab" />

<img width="1585" height="837" alt="Screenshot 2026-09-22 115258" src="https://github.com/user-attachments/assets/d3c96b32-a141-4dcc-a073-72bcf53cf3b5" />

---

## Run it locally

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

3. Copy `.env.example` to `.env` and fill in your own keys:
   ```
   API_KEY=your_omdb_api_key
   TMDB_API_KEY=your_tmdb_api_key
   FLASK_SECRET_KEY=any_long_random_string
   FLASK_DEBUG=1
   ```
   - Get a free OMDB key at [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx)
   - Get a free TMDb key at [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
   - `FLASK_DEBUG=1` turns on debug mode for local work. Leave it out in production.

4. Create the database:
   ```bash
   python run_init_db.py
   ```

5. Create your account (there is no public sign-up page):
   ```bash
   python create_user.py
   ```

6. Run the app:
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` and log in with the account you just created.

To list, reset or delete accounts later, use `python manage_users.py list`, `passwd <username>` or `delete <username>`.

## How it's deployed

The live demo runs on PythonAnywhere. The setup:
- Code is pulled from this GitHub repo, and dependencies live in a virtual environment
- API keys and the secret key are kept in an environment file on the server and are never committed
- Debug mode is off, and database and upload paths are resolved from the project folder so they work on any host
- The SQLite database is created on the server with `run_init_db.py`, and accounts are created with `create_user.py`

## Project status

Deployed and in use. The mobile layout is finished. Planned improvements:
- A public sign-up page, so accounts don't need to be created from the command line
- A preview and add flow for recommended titles that aren't yet in the user's collection
- Splitting the large `app.py` into smaller modules

---

## On the use of AI in this project

This was my first real Flask project, and my first time using Git, GitHub and deployment. I used AI assistants (Claude and ChatGPT) along the way for debugging, CSS and layout problems, explaining why something broke, Git and GitHub setup, and deployment steps.

The idea, features and UI direction are mine, and I tested and fixed real bugs as they came up. I'm sharing this openly because I'd rather be upfront about how I learn and build. If you're evaluating this project, I'm happy to walk through any part of the code and explain the reasoning behind it.

## Author

Built by **Vineet Bazala**, a B.Sc. Computer Applications student learning full-stack web development.

[GitHub](https://github.com/vineetbazala) · [Live demo](https://vineetbazala.pythonanywhere.com)
