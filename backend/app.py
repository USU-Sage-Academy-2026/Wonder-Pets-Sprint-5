from flask import Flask, request, render_template,\
    redirect, url_for, session
from db import supabase
app = Flask(__name__)

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        response = supabase.auth.sign.up(\
            {"email": email, "password": password})

        if response.user:
            return redirect(url_for("login"))
        else:
            return render_template("register.html", \
                                   error="Registration faild. Try again.")
    return render_template("register.html")

@app.route("/login", methhods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        response = supabase.auth.sign_in_with_password(\
            {"email": email, "password": password})

        if response.user:
            session["user"] = response.user.email
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", \
                                   error="Login failed. Wrong email or password")
    return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
