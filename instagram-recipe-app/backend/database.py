import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "recipes.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT 'Processing...',
                description TEXT DEFAULT '',
                servings TEXT DEFAULT '',
                prep_time TEXT DEFAULT '',
                cook_time TEXT DEFAULT '',
                ingredients TEXT DEFAULT '[]',
                steps TEXT DEFAULT '[]',
                thumbnail_url TEXT DEFAULT '',
                status TEXT DEFAULT 'processing',
                error_message TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def create_recipe(url: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO recipes (url, title) VALUES (?, ?)",
            (url, "Extracting recipe from your reel...")
        )
        conn.commit()
        return cur.lastrowid


def update_recipe(recipe_id: int, data: dict):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE recipes SET
                title=?, description=?, servings=?, prep_time=?, cook_time=?,
                ingredients=?, steps=?, thumbnail_url=?, status='ready'
            WHERE id=?
        """, (
            data.get('title', 'Untitled Recipe'),
            data.get('description', ''),
            data.get('servings', ''),
            data.get('prep_time', ''),
            data.get('cook_time', ''),
            json.dumps(data.get('ingredients', [])),
            json.dumps(data.get('steps', [])),
            data.get('thumbnail_url', ''),
            recipe_id
        ))
        conn.commit()


def update_recipe_error(recipe_id: int, error: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE recipes SET status='failed', error_message=?, title='Could not extract recipe' WHERE id=?",
            (error[:500], recipe_id)
        )
        conn.commit()


def get_recipe(recipe_id: int) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone()
        if not row:
            return None
        return _row_to_dict(row)


def get_all_recipes() -> list[dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM recipes ORDER BY created_at DESC"
        ).fetchall()
        return [_row_to_dict(row) for row in rows]


def delete_recipe(recipe_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
        conn.commit()


def _row_to_dict(row) -> dict:
    d = dict(row)
    d['ingredients'] = json.loads(d.get('ingredients') or '[]')
    d['steps'] = json.loads(d.get('steps') or '[]')
    return d
