from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_migrate import Migrate
from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from mysql import connector

app = Flask(__name__)
app.debug = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="flaskuser",
    password="dersAGef3rover",
    hostname="127.0.0.1",
    databasename="gradebook",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
app.secret_key = "un34dersAGef3roverhe35rald"
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
        # return render_template("main_page.html", comment_display=db.session.query(Comment.content, Comment.commenter_ID,
        #                                                                          Comment.comment_time_stamp,
        #                                                                          User.user_name).select_from(
        #    Comment).join(User).order_by(desc(Comment.comment_time_stamp)))

    if not current_user.is_authenticated:
        return redirect(url_for("index"))

    # comment = Comment(content=request.form["contents"], commenter_ID=current_user.user_id)
    # db.session.add(comment)
    # db.session.commit()
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
# @login_required
def student():
    if request.method == "GET":
        return render_template("students.html", student_display=Student.query.all())
    else:
        return redirect(url_for("index"))


@app.route("/assignments/")
# @login_required
def assignment():
    return render_template("assignments.html")


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


@app.route("/edit_student/<int:edit_ID>", methods=["GET", "POST"])
@login_required
def edit_student():
    if request.method == "GET":
        return render_template("edit_student.html")

    new_student = Student()
    new_student.first_name = request.form["first_name"]
    new_student.last_name = request.form["last_name"]
    new_student.email_address = request.form["email_address"]
    new_student.major = request.form["major"]
    db.session.add(new_student)
    db.session.commit()

    return render_template("edit_student.html", create_success=True)

@app.route("/delete_student/", methods=["GET", "POST"])
@app.route("/delete_student/<delete_ID>", methods=["GET", "POST"])
@login_required
def delete_student(delete_ID=None):
    if request.method == "GET":
        if delete_ID is not None:
            return render_template("delete_student.html", student_display=db.session.query(Student.student_ID,
                                                                                       Student.first_name,
                                                                                       Student.last_name,
                                                                                       Student.email_address,
                                                                                       Student.major)
                               .select_from(Student).filter(Student.student_ID == delete_ID).first())
        else:
            return render_template("delete_student.html", student_display="")

    del_student = Student.query.filter_by(student_ID=delete_ID).first()
    if del_student is None:
        return render_template("delete_student.html", delete_fail =True)
    db.session.delete(del_student)
    db.session.commit()

    return render_template("delete_student.html", delete_success=True)
    # return redirect(url_for("student"))


@app.route("/student_grades/", methods=["GET", "POST"])
def student_grades():
    return render_template("student_grades.html")


@app.route("/create_assignment/")
def create_assignment():
    return render_template("create_assignment.html")


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
