import tkinter as tk
from tkinter import messagebox
import sqlite3


conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('student', 'instructor'))
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT NOT NULL,
    instructor_id INTEGER,
    FOREIGN KEY(instructor_id) REFERENCES users(id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    date TEXT,
    status TEXT CHECK(status IN ('Present', 'Absent')),
    FOREIGN KEY(student_id) REFERENCES users(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
""")
conn.commit()


def login():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    cursor.execute("SELECT id, role FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        user_id, role = user
        login_window.destroy()
        if role == "student":
            student_dashboard(user_id)
        elif role == "instructor":
            instructor_dashboard(user_id)
    else:
        messagebox.showerror("Error", "Invalid username or password.")

def register():
    username = username_entry.get()
    password = password_entry.get()
    role = role_var.get()

    if not username or not password or not role:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        messagebox.showinfo("Success", "Registration successful!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Username already exists.")


def student_dashboard(student_id):
    student_window = tk.Tk()
    student_window.title("Student Dashboard")

    tk.Label(student_window, text="My Courses").pack()
    cursor.execute("""
        SELECT courses.id, courses.course_name FROM courses
        JOIN users ON courses.instructor_id = users.id
    """)
    courses = cursor.fetchall()

    for course_id, course_name in courses:
        tk.Label(student_window, text=course_name).pack()
        tk.Button(student_window, text="Mark Attendance", command=lambda cid=course_id: mark_attendance(student_id, cid)).pack()

    student_window.mainloop()

def mark_attendance(student_id, course_id):
    cursor.execute("INSERT INTO attendance (student_id, course_id, date, status) VALUES (?, ?, date('now'), 'Present')",
                   (student_id, course_id))
    conn.commit()
    messagebox.showinfo("Success", "Attendance marked successfully.")


def instructor_dashboard(instructor_id):
    instructor_window = tk.Tk()
    instructor_window.title("Instructor Dashboard")

    tk.Label(instructor_window, text="Manage Courses").pack()
    cursor.execute("SELECT id, course_name FROM courses WHERE instructor_id = ?", (instructor_id,))
    courses = cursor.fetchall()

    for course_id, course_name in courses:
        tk.Label(instructor_window, text=course_name).pack()
        tk.Button(instructor_window, text="View Roster", command=lambda cid=course_id: view_roster(cid)).pack()

    tk.Label(instructor_window, text="Add New Course").pack()
    course_entry = tk.Entry(instructor_window)
    course_entry.pack()
    tk.Button(instructor_window, text="Add", command=lambda: add_course(instructor_id, course_entry.get())).pack()

    instructor_window.mainloop()

def add_course(instructor_id, course_name):
    if not course_name:
        messagebox.showerror("Error", "Please enter a course name.")
        return

    cursor.execute("INSERT INTO courses (course_name, instructor_id) VALUES (?, ?)", (course_name, instructor_id))
    conn.commit()
    messagebox.showinfo("Success", "Course added successfully.")

def view_roster(course_id):
    cursor.execute("""
        SELECT users.username, attendance.date, attendance.status
        FROM attendance
        JOIN users ON attendance.student_id = users.id
        WHERE attendance.course_id = ?
    """, (course_id,))
    records = cursor.fetchall()

    roster_window = tk.Toplevel()
    roster_window.title("Course Roster")

    for record in records:
        tk.Label(roster_window, text=f"Student: {record[0]}, Date: {record[1]}, Status: {record[2]}").pack()


login_window = tk.Tk()
login_window.title("University Attendance App")

tk.Label(login_window, text="Username").pack()
username_entry = tk.Entry(login_window)
username_entry.pack()

tk.Label(login_window, text="Password").pack()
password_entry = tk.Entry(login_window, show="*")
password_entry.pack()

role_var = tk.StringVar(value="student")
tk.Radiobutton(login_window, text="Student", variable=role_var, value="student").pack()
tk.Radiobutton(login_window, text="Instructor", variable=role_var, value="instructor").pack()

tk.Button(login_window, text="Login", command=login).pack()
tk.Button(login_window, text="Register", command=register).pack()

login_window.mainloop()
