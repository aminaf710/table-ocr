from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sqlite3
import json
from table_extractor import process_table

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DB_FILE = "data.db"

# دیتابیس
conn = sqlite3.connect(DB_FILE)
conn.execute("""
CREATE TABLE IF NOT EXISTS tables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    extracted_text TEXT
)
""")
conn.close()

# صفحه اصلی (آپلود عکس)
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename != "":
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # پردازش تصویر
            tables_json = process_table(filepath)
            result = tables_json

            # ذخیره در دیتابیس
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tables (filename, extracted_text) VALUES (?, ?)",
                (file.filename, json.dumps(tables_json, ensure_ascii=False))
            )
            conn.commit()
            conn.close()

    return render_template("index.html", result=result)

# نمایش رکوردهای دیتابیس
@app.route("/database")
def database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, extracted_text FROM tables ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    records = [
        {"id": r[0], "filename": r[1], "text": json.loads(r[2])}
        for r in rows
    ]
    return render_template("database.html", records=records)

if __name__ == "__main__":
    app.run(debug=True,port=8080)
