from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

DB_NAME = "database.db"

# Initialize database and add missing columns
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Create table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            weight REAL,
            gym_attendance TEXT,
            workout_type TEXT,
            mood TEXT
        )
    ''')

    # Add columns if missing
    try:
        c.execute("ALTER TABLE entries ADD COLUMN workout_type TEXT")
    except:
        pass
    try:
        c.execute("ALTER TABLE entries ADD COLUMN mood TEXT")
    except:
        pass

    conn.commit()
    conn.close()

init_db()

# Add new entry
@app.route("/add", methods=["POST"])
def add_entry():
    data = request.json
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    weight = float(data["weight"])
    gym_attendance = data["gym_attendance"]
    workout_type = data.get("workout_type")
    mood = data.get("mood")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO entries (date, weight, gym_attendance, workout_type, mood)
        VALUES (?, ?, ?, ?, ?)
    """, (date, weight, gym_attendance, workout_type, mood))
    conn.commit()
    conn.close()
    return jsonify({"message": "Entry added!"})

# Get all entries
@app.route("/get", methods=["GET"])
def get_entries():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM entries ORDER BY date ASC")
    rows = c.fetchall()
    conn.close()

    entries = [
        {
            "id": r[0],
            "date": r[1],
            "weight": r[2],
            "gym_attendance": r[3],
            "workout_type": r[4],
            "mood": r[5]
        }
        for r in rows
    ]
    return jsonify(entries)

# Update entry
@app.route("/update/<int:entry_id>", methods=["PUT"])
def update_entry(entry_id):
    data = request.json
    date = data.get("date")
    weight = data.get("weight")
    gym = data.get("gym_attendance")
    workout_type = data.get("workout_type")
    mood = data.get("mood")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if date:
        c.execute("UPDATE entries SET date=? WHERE id=?", (date, entry_id))
    if weight is not None:
        c.execute("UPDATE entries SET weight=? WHERE id=?", (float(weight), entry_id))
    if gym:
        c.execute("UPDATE entries SET gym_attendance=? WHERE id=?", (gym, entry_id))
    if workout_type is not None:
        c.execute("UPDATE entries SET workout_type=? WHERE id=?", (workout_type, entry_id))
    if mood is not None:
        c.execute("UPDATE entries SET mood=? WHERE id=?", (mood, entry_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Entry updated!"})

# Delete entry
@app.route("/delete/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Entry deleted!"})

# Clear all data
@app.route("/clear-all", methods=["DELETE"])
def clear_all():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM entries")
    conn.commit()
    conn.close()
    return jsonify({"message": "All data cleared!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
