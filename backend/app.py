#API Tester, do not push to main
from flask import Flask, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "abcdef"  # put key in env

accounts = {}  # email -> {"account_id", "email", "password_hash", "first_name", "last_name"}


def error(message, status): 
    return jsonify({"error": message}), status

@app.get("/api/health")
def health():
    return {"ok": True}

@app.post("/api/auth/signup")
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if "@" not in email:
        return error("Enter a valid email.", 400)
    if len(password) < 8:
        return error("Password must be at least 8 characters.", 400)
    if email in accounts:
        return error("This email is already registered.", 409)
    account = {
        "account_id": len(accounts) + 1,
        "email": email,
        "password_hash": generate_password_hash(password),
        "first_name": data.get("first_name") or "",
        "last_name": data.get("last_name") or "",
    }
    accounts[email] = account
    return {"account_id": account["account_id"], "first_name": account["first_name"]}, 201

@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    account = accounts.get(email)
    if not account or not check_password_hash(account["password_hash"], data.get("password") or ""):
        return error("Wrong email or password.", 401)
    session["account_id"] = account["account_id"]
    session["first_name"] = account["first_name"]
    session["role"] = "customer"
    return {"account_id": account["account_id"], "first_name": account["first_name"], "role": "customer"}

@app.post("/api/auth/logout")
def logout():
    session.clear()
    return {"ok": True}

@app.get("/api/me")
def me():
    if "account_id" not in session:
        return {"logged_in": False}
    return {
        "logged_in": True,
        "account_id": session["account_id"],
        "first_name": session["first_name"],
        "role": session["role"],
    }

@app.errorhandler(404)
def not_found(e):
    return error("Not found.", 404)
