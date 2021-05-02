from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from flask_migrate import Migrate
from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from mysql import connector

app = Flask(__name__)
app.debug = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="",
    password="",
    hostname="127.0.0.1",
    databasename="gradebook",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
app.secret_key = ""
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app, db)


@login_manager.user_loader
def load_user(entered_name):
    return User.query.filter_by(user_name=entered_name).first()


# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html")
    if not current_user.is_authenticated:
        return redirect(url_for("index"))
    return redirect(url_for("index"))


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    login_user(user)
    return redirect(url_for("index"))


@app.route("/create/", methods=["GET", "POST"])
def create():
    if request.method == "GET":
        return render_template("create_login.html", error=False)

    if current_user.is_authenticated:
        return render_template("create_login.html", current_user_error=True)

    user = load_user(request.form["username"])
    if user:
        return render_template("create_login.html", duplicate_user_error=True)

    if request.form.get("password") != request.form.get("password_confirm"):
        return render_template("create_login.html", password_error=True)

    new_user = User()
    new_user.user_name = request.form["username"]
    new_user.password_hash = generate_password_hash(request.form["password"])
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return render_template("create_login.html", account_success=True)


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/students/", methods=["GET"])
@login_required
def student():
    if request.method == "GET":
        return render_template("students.html", student_display=Student.query.all())
    else:
        return redirect(url_for("index"))


@app.route("/assignments/", methods=["GET"])
@login_required
def assignment():
    if request.method == "GET":
        return render_template("assignments.html", assignment_display=Assignment.query.all())
    else:
        return redirect(url_for("index"))


@app.route("/create_student/", methods=["GET", "POST"])
@login_required
def create_student():
    if request.method == "GET":
        return render_template("create_student.html")

    new_student = Student()
    new_student.first_name = request.form["first_name"]
    new_student.last_name = request.form["last_name"]
    new_student.email_address = request.form["email_address"]
    new_student.major = request.form["major"]
    db.session.add(new_student)
    db.session.commit()

    return render_template("create_student.html", create_success=True)


@app.route("/edit_student/", methods=["GET", "POST"])
@app.route("/edit_student/<int:edit_ID>", methods=["GET", "POST"])
@login_required
def edit_student(edit_ID=None):
    if request.method == "GET":
        if edit_ID is not None:
            student_return = db.session.query(
                Student.student_ID,
                Student.first_name,
                Student.last_name,
                Student.email_address,
                Student.major).select_from(Student).filter(Student.student_ID == edit_ID).first()

            return render_template("edit_student.html", student_display=student_return)
        else:
            return render_template("edit_student.html", student_display="")

    ed_student = Student.query.filter_by(student_ID=edit_ID).first()
    if ed_student is None:
        return render_template("edit_student.html", edit_fail=True)

    ed_student.first_name = request.form["first_name"]
    ed_student.last_name = request.form["last_name"]
    ed_student.email_address = request.form["email_address"]
    ed_student.major = request.form["major"]
    db.session.add(ed_student)
    db.session.commit()

    return render_template("edit_student.html", edit_success=True)


@app.route("/delete_student/", methods=["GET", "POST"])
@app.route("/delete_student/<delete_ID>", methods=["GET", "POST"])
@login_required
def delete_student(delete_ID=None):
    if request.method == "GET":
        if delete_ID is not None:
            student_return = db.session.query(
                Student.student_ID,
                Student.first_name,
                Student.last_name,
                Student.email_address,
                Student.major).select_from(
                Student).filter(Student.student_ID == delete_ID).first()

            return render_template("delete_student.html", student_display=student_return)
        else:
            return render_template("delete_student.html", student_display="")

    del_student = Student.query.filter_by(student_ID=delete_ID).first()
    if del_student is None:
        return render_template("delete_student.html", delete_fail=True)
    db.session.delete(del_student)
    db.session.commit()

    return render_template("delete_student.html", delete_success=True)


@app.route("/student_grades/", methods=["GET", "POST"])
def student_grades():
    return render_template("student_grades.html")


@app.route("/create_assignment/", methods=["GET", "POST"])
@login_required
def create_assignment():
    if request.method == "GET":
        return render_template("create_assignment.html")

    new_assignment = Assignment()
    new_assignment.assignment_name = request.form["assignment_name"]
    db.session.add(new_assignment)
    db.session.commit()

    return render_template("create_assignment.html", create_success=True)


@app.route("/edit_assignment/", methods=["GET", "POST"])
@app.route("/edit_assignment/<int:edit_ID>", methods=["GET", "POST"])
@login_required
def edit_assignment(edit_ID=None):
    if request.method == "GET":
        if edit_ID is not None:
            assignment_return = db.session.query(
                Assignment.assignment_ID,
                Assignment.assignment_name
                ).select_from(Assignment).filter(Assignment.assignment_ID == edit_ID).first()

            return render_template("edit_assignment.html", assignment_display=assignment_return)
        else:
            return render_template("edit_assignment.html", assignment_display="")

    ed_assignment = Assignment.query.filter_by(assignment_ID=edit_ID).first()
    if ed_assignment is None:
        return render_template("edit_assignment.html", edit_fail=True)

    ed_assignment.assignment_name = request.form["assignment_name"]
    db.session.add(ed_assignment)
    db.session.commit()

    return render_template("edit_assignment.html", edit_success=True)


@app.route("/delete_assignment/", methods=["GET", "POST"])
@app.route("/delete_assignment/<delete_ID>", methods=["GET", "POST"])
@login_required
def delete_assignment(delete_ID=None):
    if request.method == "GET":
        if delete_ID is not None:
            assignment_return = db.session.query(
                Assignment.assignment_ID,
                Assignment.assignment_name).select_from(
                Assignment).filter(Assignment.assignment_ID == delete_ID).first()

            return render_template("delete_assignment.html", assignment_display=assignment_return)
        else:
            return render_template("delete_assignment.html", assignment_display="")

    del_assignment = Assignment.query.filter_by(assignment_ID=delete_ID).first()
    if del_assignment is None:
        return render_template("delete_assignment.html", delete_fail=True)
    db.session.delete(del_assignment)
    db.session.commit()

    return render_template("delete_assignment.html", delete_success=True)


@app.route("/create_grade/")
def create_grade():
    return render_template("create_grade")


@app.route("/edit_grade/")
def edit_grade():
    return render_template("edit_grade.html")


# Models
class User(UserMixin, db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.user_name


class Student(db.Model):
    __tablename__ = "student"
    student_ID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email_address = db.Column(db.String(45))
    major = db.Column(db.String(45))


class Assignment(db.Model):
    __tablename__ = "assignment"
    assignment_ID = db.Column(db.Integer, primary_key=True)
    assignment_name = db.Column(db.String(128))


class Grade(db.Model):
    __tablename__ = "grade"
    # grade_ID = db.Column(db.Integer, primary_key=True) Artificial primary key, not currently used.
    assignment_ID = db.Column(db.Integer, db.ForeignKey(Assignment.assignment_ID), primary_key=True)
    student_ID = db.Column(db.Integer, db.ForeignKey(Student.student_ID), primary_key=True)
    grade = db.Column(db.Float)
    assignment_grade_constraint = db.relationship("Assignment", foreign_keys=assignment_ID)
    student_grade_constraint = db.relationship("Student", foreign_keys=student_ID)
