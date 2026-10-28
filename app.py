
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database connection
def connect_db():
    return sqlite3.connect("students.db")


# Create database table
with connect_db() as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
    """)


# READ - Display all students
@app.route("/")
def home():
    with connect_db() as con:
        students = con.execute(
            "SELECT * FROM students"
        ).fetchall()

    return render_template("index.html", students=students)


# CREATE - Add a new student
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form["name"]
        department = request.form["department"]

        with connect_db() as con:
            con.execute(
                "INSERT INTO students (name, department) VALUES (?, ?)",
                (name, department)
            )

        return redirect(url_for("home"))

    return render_template("register.html")


# UPDATE - Edit student details
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):

    with connect_db() as con:
        student = con.execute(
            "SELECT * FROM students WHERE id = ?", (id,)
        ).fetchone()

        if student is None:
            return "Student not found", 404

        if request.method == "POST":
            name = request.form["name"]
            department = request.form["department"]

            con.execute(
                "UPDATE students SET name = ?, department = ? WHERE id = ?",
                (name, department, id)
            )

            return redirect(url_for("home"))

    return render_template("edit.html", student=student)


# DELETE - Remove student
@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):

    with connect_db() as con:
        con.execute(
            "DELETE FROM students WHERE id = ?", (id,)
        )

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
