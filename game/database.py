import sqlite3
import os
import sys
from datetime import datetime


def _get_db_path():
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.join(os.path.dirname(__file__), "..")
    return os.path.join(base_dir, "hezartoo.db")


DB_PATH = _get_db_path()


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS players (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            );

            CREATE TABLE IF NOT EXISTS records (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id  INTEGER NOT NULL REFERENCES players(id),
                maze_size  INTEGER NOT NULL,
                steps      INTEGER NOT NULL,
                undos      INTEGER NOT NULL,
                hints_used INTEGER NOT NULL,
                duration   INTEGER NOT NULL,
                won        INTEGER NOT NULL,
                played_at  TEXT NOT NULL
            );
        """)


def get_or_create_player(name):
    name = name.strip() or "ناشناس"
    with _connect() as conn:
        row = conn.execute("SELECT id FROM players WHERE name=?", (name,)).fetchone()
        if row:
            return row["id"]
        cur = conn.execute("INSERT INTO players (name) VALUES (?)", (name,))
        return cur.lastrowid


def save_record(player_id, maze_size, steps, undos, hints_used, duration, won):
    with _connect() as conn:
        conn.execute("""
            INSERT INTO records
              (player_id, maze_size, steps, undos, hints_used, duration, won, played_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            player_id, maze_size, steps, undos, hints_used,
            duration, 1 if won else 0,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))


def get_records(player_id):
    with _connect() as conn:
        rows = conn.execute("""
            SELECT maze_size, steps, undos, hints_used, duration, won, played_at
            FROM records
            WHERE player_id = ?
            ORDER BY played_at DESC
            LIMIT 50
        """, (player_id,)).fetchall()
    return [dict(r) for r in rows]


def get_best(player_id, maze_size):
    with _connect() as conn:
        row = conn.execute("""
            SELECT steps, duration, played_at
            FROM records
            WHERE player_id=? AND maze_size=? AND won=1
            ORDER BY steps ASC, duration ASC
            LIMIT 1
        """, (player_id, maze_size)).fetchone()
    return dict(row) if row else None


def get_all_players():
    with _connect() as conn:
        rows = conn.execute("SELECT name FROM players ORDER BY name").fetchall()
    return [r["name"] for r in rows]
