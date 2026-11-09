import os
from flask import Flask, jsonify, request, session
from werkzeug.exceptions import BadRequest
from supabase import create_client, Client

app = Flask(__name__)

# 1. Environment-based configuration (Fail fast if secrets are missing)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("FATAL: FLASK_SECRET_KEY environment variable is not set.")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("FATAL: Supabase credentials (URL/KEY) are missing from environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def error_response(message: str, status_code: int):
    """Helper for consistent JSON error responses."""
    return jsonify({"error": message}), status_code


@app.get("/api/health")
def health_check():
    """Health check endpoint for container orchestrators (e.g., Docker, AWS ECS)."""
    return {"status": "healthy"}, 200


@app.post("/api/auth/signup")
def signup():
    try:
        data = request.get_json(silent=True) or {}
    except BadRequest:
        return error_response("Invalid JSON payload.", 400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    # Input validation
    if "@" not in email or "." not in email:
        return error_response("Enter a valid email address.", 400)
    if len(password) < 8:
        return error_response("Password must be at least 8 characters long.", 400)

    try:
        # Supabase signup call
        response = supabase.auth.sign_up({"email": email, "password": password})
        
        if not response.user:
            return error_response("Registration failed. Please try again.", 400)

        return {
            "message": "Registration successful. Please check your email to verify your account if required.",
            "user_id": response.user.id,
            "email": response.user.email
        }, 201

    except Exception as e:
        # Catch Supabase API exceptions (e.g., user already exists)
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            return error_response("This email is already registered.", 409)
        return error_response(f"Authentication service error: {error_msg}", 500)


@app.post("/api/auth/login")
def login():
    try:
        data = request.get_json(silent=True) or {}
    except BadRequest:
        return error_response("Invalid JSON payload.", 400)

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return error_response("Email and password are required.", 400)

    try:
        # Supabase sign-in call
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        if not response.user:
            return error_response("Invalid email or password.", 401)

        # Secure session establishment
        session.clear()
        session["user_id"] = response.user.id
        session["email"] = response.user.email
        session["access_token"] = response.session.access_token if response.session else None

        return {
            "message": "Login successful",
            "user_id": response.user.id,
            "email": response.user.email
        }, 200

    except Exception as e:
        return error_response("Invalid email or password.", 401)


@app.post("/api/auth/logout")
def logout():
    session.clear()
    return {"message": "Successfully logged out."}, 200


@app.get("/api/me")
def get_current_user():
    if "user_id" not in session:
        return {"logged_in": False}, 401

    return {
        "logged_in": True,
        "user_id": session["user_id"],
        "email": session["email"]
    }, 200


@app.errorhandler(404)
def not_found(e):
    return error_response("Resource not found.", 404)


@app.errorhandler(500)
def internal_server_error(e):
    return error_response("Internal server error.", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)