
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
import sqlite3

login_bp = Blueprint("login", __name__)


def connect_db():
    return sqlite3.connect("students.db")


# STUDENT LOGIN
@login_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        with connect_db() as con:
            student = con.execute(
    """SELECT id, name, department, password
       FROM students WHERE email = ?""",
    (email,)
).fetchone()

        if student and check_password_hash(student[3], password):
            session["student_id"] = student[0]
            session["student_name"] = student[1]

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid email or password"
        )

    return render_template("login.html")


# STUDENT LOGOUT
@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login.login"))
