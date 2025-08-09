import os
import sqlite3
from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from datetime import datetime
import csv
import io

app = Flask(__name__)
CORS(app)

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            weight REAL,
            gym_attendance TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/add", methods=["POST"])
def add_entry():
    data = request.json
    date = data.get("date") or datetime.now().strftime("%Y-%m-%d")
    weight = float(data["weight"])
    gym_attendance = data.get("gym_attendance", "No")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO entries (date, weight, gym_attendance) VALUES (?, ?, ?)",
              (date, weight, gym_attendance))
    conn.commit()
    conn.close()
    return jsonify({"message": "Entry added!"})

@app.route("/get", methods=["GET"])
def get_entries():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, date, weight, gym_attendance FROM entries ORDER BY date ASC")
    rows = c.fetchall()
    conn.close()
    entries = [{"id": r[0], "date": r[1], "weight": r[2], "gym_attendance": r[3]} for r in rows]
    return jsonify(entries)

@app.route("/delete/<int:entry_id>", methods=["DELETE"])
def delete_entry(entry_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Entry deleted!"})

@app.route("/update/<int:entry_id>", methods=["PUT"])
def update_entry(entry_id):
    data = request.json
    date = data.get("date")
    weight = data.get("weight")
    gym = data.get("gym_attendance")
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # only update provided fields
    if date:
        c.execute("UPDATE entries SET date=? WHERE id=?", (date, entry_id))
    if weight is not None:
        c.execute("UPDATE entries SET weight=? WHERE id=?", (float(weight), entry_id))
    if gym:
        c.execute("UPDATE entries SET gym_attendance=? WHERE id=?", (gym, entry_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Entry updated!"})

@app.route("/export", methods=["GET"])
def export_csv():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, date, weight, gym_attendance FROM entries ORDER BY date ASC")
    rows = c.fetchall()
    conn.close()

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["id", "date", "weight", "gym_attendance"])
    writer.writerows(rows)
    output = si.getvalue().encode('utf-8')
    return Response(output,
                    mimetype="text/csv",
                    headers={"Content-Disposition":"attachment;filename=gym_data.csv"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
