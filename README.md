# Fitness Activity Tracker with an AI Coach

Desktop app for tracking gym workouts, built in Python as a team project at university. Users create an account, choose their exercises, run timed workout sessions and can ask an AI coach for advice based on their own workout history.

## Features

- **User accounts**: sign up and log in, with passwords stored as SHA-256 hashes
- **Live workout sessions**: a timer that counts reps and sets, starts an automatic rest break after each set, and plays a sound at the start of the break (on Windows)
- **Calorie estimate** based on MET values for each exercise, counted only during active time (rest breaks are excluded)
- **Workout history** saved per user in a local SQLite database
- **AI coach** (Google Gemini): answers the user's questions using their workout history and active exercises as context; the request runs in a separate thread so the interface does not freeze
- Graphical interface built with Tkinter

## Tech stack

- Python 3, Tkinter
- SQLite (`sqlite3`)
- Google Generative AI (Gemini API), python-dotenv

## Project structure

```
aplicatie-activitate-fizica/
├── main.py            # Tkinter interface: start, sign-up, login and dashboard screens
├── workout_logic.py   # workout session: timer, reps, sets, breaks, calories
├── database.py        # SQLite tables for users, active exercises and history
├── ai_logic.py        # AI coach built on the Gemini API
├── theme.py           # colors and fonts
└── requirements.txt
```

## How to run

1. Clone the repository:
   ```bash
   git clone https://github.com/TudorL22/aplicatie-activitate-fizica.git
   cd aplicatie-activitate-fizica
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. *(Optional, for the AI coach)* create a `.env` file with your Google API key:
   ```
   GOOGLE_API_KEY=your-key-here
   ```
   Without a key the app still works; only the AI coach is disabled.
4. Start the app:
   ```bash
   python main.py
   ```
   The database (`fitness.db`) is created automatically on the first run.

## Screenshots

<!-- Add screenshots of the login screen, the dashboard and a running workout here -->

## Authors

- Tudor Lungu
- Ionescu Tudor
- Rotariu Ștefan
- Iancu Teodor
