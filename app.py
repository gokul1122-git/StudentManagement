
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from login import login_bp
import sqlite3

app = Flask(__name__)

app.secret_key = "student-management-secret-key"

app.register_blueprint(login_bp)


# DATABASE CONNECTION
def connect_db():
    return sqlite3.connect("students.db")


# CREATE AND UPDATE DATABASE TABLE
def init_db():

    with connect_db() as con:

        con.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                department TEXT NOT NULL
            )
        """)

        # Add email column if it does not exist
        columns = [
            row[1] for row in
            con.execute("PRAGMA table_info(students)").fetchall()
        ]

        if "email" not in columns:
            con.execute("ALTER TABLE students ADD COLUMN email TEXT")

        if "password" not in columns:
            con.execute("ALTER TABLE students ADD COLUMN password TEXT")

        # Prevent duplicate email registrations
        con.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_students_email
            ON students(email)
        """)


init_db()


# READ - DISPLAY ALL STUDENTS
@app.route("/")
def home():

    with connect_db() as con:
        students = con.execute(
            "SELECT id, name, department FROM students"
        ).fetchall()

    return render_template("index.html", students=students)


# CREATE - STUDENT REGISTRATION
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        department = request.form["department"].strip()

        if not all([name, email, password, department]):
            return "All fields are required", 400

        hashed_password = generate_password_hash(password)

        try:
            with connect_db() as con:
                con.execute("""
                    INSERT INTO students
                    (name, email, password, department)
                    VALUES (?, ?, ?, ?)
                """, (
                    name,
                    email,
                    hashed_password,
                    department
                ))

        except sqlite3.IntegrityError:
            return "Email already registered", 409

        return redirect(url_for("login.login"))

    return render_template("register.html")


# UPDATE - EDIT STUDENT DETAILS
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):

    with connect_db() as con:

        student = con.execute(
            "SELECT id, name, department FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        if student is None:
            return "Student not found", 404

        if request.method == "POST":

            name = request.form["name"]
            department = request.form["department"]

            con.execute("""
                UPDATE students
                SET name = ?, department = ?
                WHERE id = ?
            """, (name, department, id))

            return redirect(url_for("home"))

    return render_template("edit.html", student=student)


# DELETE - REMOVE STUDENT
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):

    with connect_db() as con:
        con.execute(
            "DELETE FROM students WHERE id = ?",
            (id,)
        )

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
