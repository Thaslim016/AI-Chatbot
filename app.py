from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from chatbot.model import get_response, load_responses
from chatbot.utils import authenticate_user, create_user, add_faq, get_all_faqs, get_analytics
import os
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.jinja_env.cache = {}

@app.route("/")
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    with open("data/s3ettings.json", "r") as f:
        settings = json.load(f)
    return render_template("dashboard.html", use_ai=settings.get("use_ai", False))

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    bot_response = get_response(user_input)
    return jsonify({"response": bot_response})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = authenticate_user(username, password)
        if user:
            session["user"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("index"))
        else:
            return "❌ Invalid credentials", 401
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            create_user(username, password)
            return redirect(url_for("login"))
        except:
            return "⚠️ Username already exists. Try another.", 400
    return render_template("signup.html")

@app.route("/signup-student", methods=["GET", "POST"])
def signup_student():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            create_user(username, password, role="student")
            return redirect(url_for("login"))
        except:
            return "⚠️ Username already exists. Try another.", 400
    return render_template("signup_student.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if 'user' not in session or session.get("role") != "admin":
        return redirect(url_for('login'))

    if request.method == "POST":
        question = request.form["question"]
        answer = request.form["answer"]
        add_faq(question, answer)
        load_responses()

    with open("data/settings.json", "r") as f:
        settings = json.load(f)
    return render_template("admin.html", faqs=get_all_faqs(), use_ai=settings.get("use_ai", False))

@app.route("/toggle-ai", methods=["POST"])
def toggle_ai():
    settings_file = "data/settings.json"
    with open(settings_file, "r") as f:
        settings = json.load(f)

    # Directly flip the flag instead of relying on form value
    settings["use_ai"] = not settings.get("use_ai", False)

    with open(settings_file, "w") as f:
        json.dump(settings, f, indent=4)

    return redirect(request.referrer or url_for("index"))

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST":
        feedback_text = request.form["feedback"]
        username = session.get("user")
        print(f"📝 Feedback from {username}: {feedback_text}")  # Or save to DB
        return render_template("feedback.html", message="Thank you for your feedback!")

    return render_template("feedback.html")

@app.route("/analytics")
def analytics():
    if 'user' not in session:
        return redirect(url_for("login"))
    data = get_analytics()
    return jsonify(data)

@app.route("/check-role")
def check_role():
    role = session.get("role", "user")
    return jsonify({"role": role})

if __name__ == "__main__":
    app.run(debug=True)
