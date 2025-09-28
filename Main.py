from flask import Flask, render_template, request, jsonify, session
import json, os, uuid
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecret"  # CHANGE karo strong secret key me

KEYS_FILE = 'keys.json'

# Admin credentials (CHANGE karo apne hisaab se)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "12345"

# Redirect URLs
REDIRECT_URLS = {
    "site1": "http://fi9.bot-hosting.net:21584",
    "site2": "http://de3.bot-hosting.net:22099/",
    "site3": "http://fi8.bot-hosting.net:21755/",
    "site4": "https://knight-bot-paircode.onrender.com/",
    "site5": "http://fi10.bot-hosting.net:20424",
    "site6": "https://fyterboy.netlify.app/",
    "site7": "http://fi9.bot-hosting.net:22039/"
}

keys_cache = {}

# --- Helpers ---
def load_keys():
    global keys_cache
    if not os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'w') as f:
            json.dump({}, f)
        return {}
    with open(KEYS_FILE, 'r') as f:
        try:
            keys_cache = json.load(f)
        except:
            keys_cache = {}
    return keys_cache

def save_keys(data):
    global keys_cache
    keys_cache = data
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys_cache, f, indent=4)

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get("is_admin"):
            return jsonify({"ok": False, "message": "Not authorized"}), 401
        return f(*args, **kwargs)
    return wrapped

# --- User side ---

@app.route('/')
def index():
    return render_template("index.html")  # tumhara user HTML page

@app.route('/check_key', methods=['POST'])
def check_key():
    data = request.get_json() or {}
    user_key = data.get("key")
    if not user_key:
        return jsonify({"status": "invalid", "message": "❌ Key missing"})

    keys_data = load_keys()

    # Agar pehli baar hai to entry bana do
    if user_key not in keys_data:
        keys_data[user_key] = {"status": "pending"}
        save_keys(keys_data)

    status = keys_data[user_key]["status"]

    return jsonify({
        "status": status,
        "redirect_url": REDIRECT_URLS.get("site1") if status == "approved" else None
    })

# --- Admin side ---

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json() or {}
    user = data.get("username", "").strip()
    pw = data.get("password", "").strip()
    if user == ADMIN_USERNAME and pw == ADMIN_PASSWORD:
        session["is_admin"] = True
        session["admin_user"] = user
        return jsonify({"ok": True, "message": "Login successful"})
    return jsonify({"ok": False, "message": "Invalid credentials"}), 401

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop("is_admin", None)
    session.pop("admin_user", None)
    return jsonify({"ok": True, "message": "Logged out"})

@app.route('/admin/keys')
@admin_required
def admin_keys():
    keys_data = load_keys()
    return jsonify(keys_data or {})

@app.route('/admin/approve', methods=['POST'])
@admin_required
def admin_approve():
    data = request.get_json() or {}
    key = data.get("key")
    keys_data = load_keys()
    if key not in keys_data:
        return jsonify({"ok": False, "message": "Key not found"}), 404
    keys_data[key]["status"] = "approved"
    save_keys(keys_data)
    return jsonify({"ok": True, "message": f"Key {key} approved"})

@app.route('/admin/disapprove', methods=['POST'])
@admin_required
def admin_disapprove():
    data = request.get_json() or {}
    key = data.get("key")
    keys_data = load_keys()
    if key not in keys_data:
        return jsonify({"ok": False, "message": "Key not found"}), 404
    keys_data[key]["status"] = "pending"
    save_keys(keys_data)
    return jsonify({"ok": True, "message": f"Key {key} set to pending"})

# --- Run server ---
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=20023)
