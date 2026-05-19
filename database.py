import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path("data/app.db")


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    NOT NULL UNIQUE,
                email      TEXT    NOT NULL UNIQUE,
                password   TEXT    NOT NULL,
                avatar     TEXT    DEFAULT '🧑',
                created_at TEXT    DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS auth_tokens (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token      TEXT    NOT NULL UNIQUE,
                created_at TEXT    DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS sessions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
                language   TEXT    NOT NULL,
                level      TEXT    NOT NULL DEFAULT 'intermediate',
                domain     TEXT    NOT NULL DEFAULT 'general',
                situation  TEXT,
                created_at TEXT    DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                role       TEXT    NOT NULL,
                content    TEXT    NOT NULL,
                created_at TEXT    DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS errors (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL,
                original    TEXT    NOT NULL,
                correction  TEXT    NOT NULL,
                created_at  TEXT    DEFAULT (datetime('now'))
            );
        """)


# ── Users ──────────────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password_hash: str) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO users (username, email, password) VALUES (?,?,?)",
            (username, email, password_hash),
        )
        return cur.lastrowid


def get_user_by_username(username: str) -> Optional[dict]:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        return dict(row) if row else None


def get_user_by_email(email: str) -> Optional[dict]:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict]:
    with _conn() as c:
        row = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_user_by_token(token: str) -> Optional[dict]:
    with _conn() as c:
        row = c.execute(
            "SELECT u.* FROM users u "
            "JOIN auth_tokens t ON t.user_id = u.id "
            "WHERE t.token=?",
            (token,),
        ).fetchone()
        return dict(row) if row else None


# ── Auth tokens ────────────────────────────────────────────────────────────────

def save_token(user_id: int, token: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO auth_tokens (user_id, token) VALUES (?,?)",
            (user_id, token),
        )


def delete_token(token: str) -> None:
    with _conn() as c:
        c.execute("DELETE FROM auth_tokens WHERE token=?", (token,))


# ── Sessions ───────────────────────────────────────────────────────────────────

def create_session(language: str, level: str, situation: str,
                   domain: str = "general", user_id: Optional[int] = None) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO sessions (user_id, language, level, domain, situation) VALUES (?,?,?,?,?)",
            (user_id, language, level, domain, situation),
        )
        return cur.lastrowid


def get_sessions(user_id: Optional[int] = None, limit: int = 30) -> list[dict]:
    with _conn() as c:
        if user_id:
            rows = c.execute(
                "SELECT * FROM sessions WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]


# ── Messages ───────────────────────────────────────────────────────────────────

def add_message(session_id: int, role: str, content: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?,?,?)",
            (session_id, role, content),
        )


def get_messages(session_id: int) -> list[dict]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM messages WHERE session_id=? ORDER BY created_at",
            (session_id,),
        ).fetchall()
        return [dict(r) for r in rows]


# ── Errors ─────────────────────────────────────────────────────────────────────

def add_error(session_id: int, original: str, correction: str,
              user_id: Optional[int] = None) -> None:
    with _conn() as c:
        c.execute(
            "INSERT INTO errors (session_id, user_id, original, correction) VALUES (?,?,?,?)",
            (session_id, user_id, original, correction),
        )


def get_errors(user_id: Optional[int] = None, limit: int = 50) -> list[dict]:
    with _conn() as c:
        if user_id:
            rows = c.execute(
                "SELECT e.*, s.language, s.domain FROM errors e "
                "JOIN sessions s ON e.session_id = s.id "
                "WHERE e.user_id=? ORDER BY e.created_at DESC LIMIT ?",
                (user_id, limit),
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT e.*, s.language, s.domain FROM errors e "
                "JOIN sessions s ON e.session_id = s.id "
                "ORDER BY e.created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]


# ── Stats ──────────────────────────────────────────────────────────────────────

def get_stats(user_id: Optional[int] = None) -> dict:
    with _conn() as c:
        if user_id:
            sessions = c.execute("SELECT COUNT(*) FROM sessions WHERE user_id=?",     (user_id,)).fetchone()[0]
            turns    = c.execute("SELECT COUNT(*) FROM messages m JOIN sessions s ON m.session_id=s.id WHERE s.user_id=? AND m.role='user'", (user_id,)).fetchone()[0]
            errors   = c.execute("SELECT COUNT(*) FROM errors WHERE user_id=?",       (user_id,)).fetchone()[0]
            langs    = c.execute("SELECT language, COUNT(*) as n FROM sessions WHERE user_id=? GROUP BY language ORDER BY n DESC LIMIT 1", (user_id,)).fetchone()
            domains  = c.execute("SELECT domain, COUNT(*) as n FROM sessions WHERE user_id=? GROUP BY domain ORDER BY n DESC LIMIT 1", (user_id,)).fetchone()
        else:
            sessions = c.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            turns    = c.execute("SELECT COUNT(*) FROM messages WHERE role='user'").fetchone()[0]
            errors   = c.execute("SELECT COUNT(*) FROM errors").fetchone()[0]
            langs    = None
            domains  = None
        return {
            "sessions":      sessions,
            "turns":         turns,
            "errors_caught": errors,
            "top_language":  langs["language"]  if langs   else None,
            "top_domain":    domains["domain"]  if domains else None,
        }
