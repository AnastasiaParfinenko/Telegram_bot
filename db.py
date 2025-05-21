import sqlite3
from contextlib import contextmanager


def init_db():
    conn = sqlite3.connect('words.db')
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            list_name TEXT NOT NULL,
            word TEXT NOT NULL,
            translation TEXT NOT NULL,
            example TEXT  
        ) 
    """)

    conn.commit()
    conn.close()


@contextmanager
def get_connection():
    conn = sqlite3.connect("words.db")
    try:
        yield conn, conn.cursor()
        conn.commit()
    finally:
        conn.close()


def get_user_lists(user_id):
    with sqlite3.connect("words.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT list_name FROM words WHERE user_id = ?",
                (user_id,))
        lists = [row[0] for row in cur.fetchall()]
    return lists


def get_word_list(user_id, list_name):
    with sqlite3.connect("words.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT word, translation FROM words WHERE user_id = ? AND list_name = ?",
                    (user_id, list_name))
        return cur.fetchall()


def get_flashcards(user_id, list_name):
    import random
    flashcards = get_word_list(user_id, list_name)
    random.shuffle(flashcards)
    return flashcards


def insert_word(user_id, list_name, word, translation):
    with sqlite3.connect("words.db") as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO words (user_id, list_name, word, translation) VALUES (?, ?, ?, ?)",
            (user_id, list_name, word.strip(), translation.strip())
        )
        conn.commit()


def delete_list(user_id, list_name):
    with sqlite3.connect("words.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM words WHERE user_id = ? AND list_name = ?",
                    (user_id, list_name))
        conn.commit()

def create_list(user_id, list_name, words):
    import re

    error_lines = []

    with sqlite3.connect("words.db") as conn:
        cur = conn.cursor()
        for line in words:
            try:
                word, translation = re.split(r':\s*', line, maxsplit=1)
                cur.execute("INSERT INTO words (user_id, list_name, word, translation) VALUES (?, ?, ?, ?)",
                            (user_id, list_name, word.strip(), translation.strip()))
            except ValueError:
                error_lines.append(line)
        conn.commit()

    return error_lines
