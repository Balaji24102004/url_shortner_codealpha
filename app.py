from flask import Flask, request, redirect, render_template, jsonify
import string, random
import sqlite3

app = Flask(__name__)

# Generate short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Initialize DB
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  original_url TEXT NOT NULL,
                  short_code TEXT UNIQUE NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# Route: Home + Optional Form
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# Route: Create short URL
@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.json or request.form
    original_url = data.get("url")
    short_code = generate_short_code()
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO urls (original_url, short_code) VALUES (?, ?)", (original_url, short_code))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Short code collision, try again"}), 500
    finally:
        conn.close()

    short_url = request.host_url + short_code
    return jsonify({"short_url": short_url})

# Route: Redirect
@app.route("/<short_code>")
def redirect_short_url(short_code):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT original_url FROM urls WHERE short_code = ?", (short_code,))
    result = c.fetchone()
    conn.close()

    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404

if __name__ == "__main__":
    app.run(debug=True)
