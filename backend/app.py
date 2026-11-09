
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, session
from werkzeug.exceptions import BadRequest

# Load environment variables
load_dotenv()

# Import Clark's database functions
import db

app = Flask(__name__)

# Flask session configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("FLASK_SECRET_KEY environment variable is missing.")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("FLASK_ENV") == "production"


# Standard error response
def error_response(message, status_code):
    return jsonify({"error": message}), status_code


# 1. HEALTH CHECK
@app.get("/api/health")
def health_check():
    return {"ok": True}, 200


# 2. CUSTOMER SIGNUP
@app.post("/api/auth/signup")
def signup():
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return error_response("Invalid JSON payload.", 400)

        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""
        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        phone_number = data.get("phone_number")

        # Validate customer information
        if "@" not in email or "." not in email:
            return error_response("Enter a valid email address.", 400)

        if len(password) < 8:
            return error_response(
                "Password must be at least 8 characters long.", 400
            )

        if not first_name or not last_name:
            return error_response(
                "First and last name are required.", 400
            )

        if phone_number is not None:
            phone_number = str(phone_number).strip() or None

        # Call Clark's signup function in db.py
        result = db.signup_customer(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )

        return result, 201

    except BadRequest:
        return error_response("Invalid JSON payload.", 400)

    except Exception as e:
        error_msg = str(e).lower()

        if "already registered" in error_msg or "already been registered" in error_msg:
            return error_response(
                "This email is already registered.", 409
            )

        print("Signup error:", e)
        return error_response("Signup failed.", 500)


# 3. CUSTOMER LOGIN
@app.post("/api/auth/login")
def login():
    try:
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return error_response("Invalid JSON payload.", 400)

        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not email or not password:
            return error_response(
                "Email and password are required.", 400
            )

        # Call Clark's login function in db.py
        result = db.login_customer(email, password)

        # Save the login session
        session.clear()
        session["access_token"] = result["access_token"]
        session["refresh_token"] = result["refresh_token"]

        # Return the information required by the assignment
        return {
            "account_id": result["account_id"],
            "first_name": result["first_name"],
            "role": result["role"]
        }, 200

    except Exception as e:
        print("Login error:", e)
        return error_response("Invalid email or password.", 401)


# 4. CUSTOMER LOGOUT
@app.post("/api/auth/logout")
def logout():
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")

    try:
        if access_token and refresh_token:
            # Call Clark's logout function in db.py
            db.logout_user(access_token, refresh_token)

    except Exception as e:
        print("Logout error:", e)

    finally:
        session.clear()

    return {"ok": True}, 200


# 5. GET CURRENT USER
@app.get("/api/me")
def current_user():
    access_token = session.get("access_token")

    if not access_token:
        return {"logged_in": False}, 200

    try:
        # Call Clark's current-user function in db.py
        user = db.get_current_user(access_token)

        if not user:
            session.clear()
            return {"logged_in": False}, 200

        return user, 200

    except Exception as e:
        print("Current user error:", e)
        session.clear()
        return {"logged_in": False}, 200


# 6. ERROR HANDLERS
@app.errorhandler(404)
def not_found(e):
    return error_response("Resource not found.", 404)


@app.errorhandler(500)
def internal_server_error(e):
    return error_response("Internal server error.", 500)


# START THE FLASK APPLICATION
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
