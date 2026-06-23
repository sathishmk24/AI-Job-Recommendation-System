from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import PyPDF2

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
app.secret_key = "placementportal123"
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

skills_db = [
    "python",
    "flask",
    "html",
    "css",
    "javascript",
    "react",
    "mysql",
    "sql",
    "pandas",
    "machine learning",
    "tensorflow",
    "mongodb",
    "java",
    "spring boot"
]


def extract_text(pdf_path):
    text = ""

    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text

    return text.lower()


def extract_skills(text):
    found_skills = []

    for skill in skills_db:
        if skill.lower() in text:
            found_skills.append(skill)

    return found_skills


def calculate_resume_score(skills):
    total_skills = len(skills_db)
    matched_skills = len(skills)

    if total_skills == 0:
        return 0

    return int((matched_skills / total_skills) * 100)


def get_jobs():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()

    conn.close()

    return jobs


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload")
def upload_page():
    return render_template("upload.html")


@app.route("/admin")
def admin():
    jobs = get_jobs()
    return render_template("admin.html", jobs=jobs)


@app.route("/add-job", methods=["POST"])
def add_job():

    title = request.form["title"]
    skills = request.form["skills"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO jobs(job_title, skills) VALUES (?, ?)",
        (title, skills)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/edit-job/<int:id>")
def edit_job(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM jobs WHERE id=?",
        (id,)
    )

    job = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_job.html",
        job=job
    )


@app.route("/update-job/<int:id>", methods=["POST"])
def update_job(id):

    title = request.form["title"]
    skills = request.form["skills"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE jobs SET job_title=?, skills=? WHERE id=?",
        (title, skills, id)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/delete-job/<int:id>")
def delete_job(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM jobs WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/recommend", methods=["POST"])
def recommend():

    file = request.files["resume"]

    if not file:
        return "Please upload a resume"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    resume_text = extract_text(filepath)

    user_skills = extract_skills(resume_text)

    resume_score = calculate_resume_score(user_skills)

    jobs = get_jobs()

    documents = [" ".join(user_skills)]

    for job in jobs:
        documents.append(job[2])

    tfidf = TfidfVectorizer()

    matrix = tfidf.fit_transform(documents)

    scores = cosine_similarity(
        matrix[0:1],
        matrix[1:]
    )[0]

    recommendations = []

    for index, score in enumerate(scores):
        recommendations.append({
            "job": jobs[index][1],
            "score": round(score * 100, 2)
        })

    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return render_template(
        "recommendations.html",
        skills=user_skills,
        recommendations=recommendations,
        score=resume_score
    )
@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register-user", methods=["POST"])
def register_user():
    name = request.form["name"]
    email = request.form["email"]

    password = generate_password_hash(
    request.form["password"]
  )

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users(name,email,password) VALUES(?,?,?)",
        (name, email, password)
  )

    conn.commit()
    conn.close()

    return redirect("/login")


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login-user", methods=["POST"])
def login_user():


    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
  )

    user = cursor.fetchone()

    conn.close()

    if user and check_password_hash(user[3], password):
        session["user"] = user[1]
        return redirect("/dashboard")

    return "Invalid Email or Password"



@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "dashboard.html",
        user=session["user"]
  )


@app.route("/logout")
def logout():


    session.clear()

    return redirect("/login")



if __name__ == "__main__":
    app.run(debug=True)