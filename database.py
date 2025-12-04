import sqlite3
import hashlib


class Database:
    def __init__(self, db_name="fitness.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.creeaza_tabele()

    def creeaza_tabele(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS exercitii_active (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            exercitiu TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            exercitiu TEXT,
            start_time TEXT,
            duration INTEGER,
            reps INTEGER,
            sets INTEGER,
            calories REAL
        )
        """)
        self.conn.commit()

    def hash_parola(self, parola):
        return hashlib.sha256(parola.encode()).hexdigest()

    def adauga_utilizator(self, username, parola):
        parola_hash = self.hash_parola(parola)
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, parola_hash)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def autentifica(self, username, parola):
        parola_hash = self.hash_parola(parola)
        self.cursor.execute(
            "SELECT id, username FROM users WHERE username=? AND password=?",
            (username, parola_hash)
        )
        return self.cursor.fetchone()

    def adauga_exercitiu(self, user_id, exercitiu):
        self.cursor.execute(
            "INSERT INTO exercitii_active (user_id, exercitiu) VALUES (?, ?)",
            (user_id, exercitiu)
        )
        self.conn.commit()

    def sterge_exercitiu(self, user_id, exercitiu):
        self.cursor.execute(
            "DELETE FROM exercitii_active WHERE user_id=? AND exercitiu=?",
            (user_id, exercitiu)
        )
        self.conn.commit()

    def exercitii_user(self, user_id):
        self.cursor.execute(
            "SELECT exercitiu FROM exercitii_active WHERE user_id=?",
            (user_id,)
        )
        return [row[0] for row in self.cursor.fetchall()]

    def salveaza_antrenament(self, user_id, exercitiu,
                             start_time, duration, reps, sets, calories):
        self.cursor.execute("""
        INSERT INTO workout_history
        (user_id, exercitiu, start_time, duration, reps, sets, calories)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, exercitiu, start_time, duration, reps, sets, calories))
        self.conn.commit()
