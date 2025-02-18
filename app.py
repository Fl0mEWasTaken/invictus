from flask import Flask, render_template, request, redirect, url_for, session
import os
import time

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a strong secret key

def save_user_data(username, data, password):
    with open(f"{username}_data.txt", "w") as file:
        file.write(f"{password}\n{data}")

def load_user_data(username):
    if os.path.exists(f"{username}_data.txt"):
        with open(f"{username}_data.txt", "r") as file:
            lines = file.readlines()
            if len(lines) < 2:
                return "", ""
            password = lines[0].strip()
            data = lines[1].strip()
            return password, data
    return "", ""

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        stored_password, _ = load_user_data(username)

        if stored_password and stored_password == password:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")

        if os.path.exists(f"{username}_data.txt"):
            return render_template("register.html", error="Username already exists")

        save_user_data(username, "0,0,0,0,0", password)
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    stored_password, data = load_user_data(username)

    current_time = time.time()
    current_day = int(current_time // (24 * 3600))

    if data:
        streak, last_update_day, pushups, situps, squats = map(int, data.split(","))
    else:
        streak, last_update_day, pushups, situps, squats = 0, 0, 0, 0, 0

    if current_day != last_update_day:
        pushups, situps, squats = 0, 0, 0
        if pushups < 100 and situps < 100 and squats < 100:
            streak = 0

    if request.method == "POST":
        pushups += int(request.form.get("pushups", 0))
        situps += int(request.form.get("situps", 0))
        squats += int(request.form.get("squats", 0))

        if pushups >= 100 and situps >= 100 and squats >= 100:
            streak += 1

        save_user_data(username, f"{streak},{current_day},{pushups},{situps},{squats}", stored_password)

    return render_template("dashboard.html", username=username, streak=streak, pushups=pushups, situps=situps, squats=squats)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
