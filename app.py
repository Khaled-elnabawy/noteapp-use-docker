import os
import time
from flask import Flask, request, render_template
from sqlalchemy import create_engine, text
from datetime import datetime

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "notesuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "notespass")
DB_NAME = os.getenv("DB_NAME", "notesdb")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)

# نجهز الجدول
def init_db():
    while True:
        try:
            with engine.begin() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        Name VARCHAR(100) NOT NULL,
                        Content TEXT NOT NULL,
                        Date DATETIME NOT NULL
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """))
            break
        except Exception as e:
            print("⏳ Waiting for DB...", e)
            time.sleep(3)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        note = request.form.get("note")
        if name and note:
            with engine.begin() as conn:
                conn.execute(
                    text("INSERT INTO notes (Name, Content, Date) VALUES (:n, :c, :d)"),
                    {"n": name, "c": note, "d": datetime.now()}
                )

    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM notes ORDER BY Date DESC"))
        notes = [dict(r._mapping) for r in result]

    return render_template("index.html", notes=notes)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

