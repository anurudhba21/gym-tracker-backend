from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Ensure persistent storage directory exists in Railway
DB_PATH = "/mnt/data"
os.makedirs(DB_PATH, exist_ok=True)

# Full DB path
DB_NAME = os.path.join(DB_PATH, "database.db")


# Function to initialize database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS gym_tracker (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        weight REAL NOT NULL,
                        gym_attendance TEXT NOT NULL,
                        workout_type TEXT,
                        mood TEXT
                    )''')
    conn.commit()
    conn.close()


# Get all entries
@app.route("/records", methods=["GET"])
def get_records():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gym_tracker ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            "id": row["id"],
            "date": row["date"],
            "weight": float(row["weight"]),  # Keep decimal precision
            "gym_attendance": row["gym_attendance"],
            "workout_type": row["workout_type"],
            "mood": row["mood"]
        })
    return jsonify(data)


# Add a new record
@app.route("/records", methods=["POST"])
def add_record():
    data = request.get_json()
    date = data.get("date")
    weight = data.get("weight")
    gym_attendance = data.get("gym_attendance")
    workout_type = data.get("workout_type")
    mood = data.get("mood")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO gym_tracker (date, weight, gym_attendance, workout_type, mood) VALUES (?, ?, ?, ?, ?)",
        (date, weight, gym_attendance, workout_type, mood)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Record added successfully"})


# Update an existing record
@app.route("/records/<int:record_id>", methods=["PUT"])
def update_record(record_id):
    data = request.get_json()
    date = data.get("date")
    weight = data.get("weight")
    gym_attendance = data.get("gym_attendance")
    workout_type = data.get("workout_type")
    mood = data.get("mood")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """UPDATE gym_tracker 
           SET date=?, weight=?, gym_attendance=?, workout_type=?, mood=? 
           WHERE id=?""",
        (date, weight, gym_attendance, workout_type, mood, record_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Record updated successfully"})


# Delete a record
@app.route("/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gym_tracker WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Record deleted successfully"})


# Run the app
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
