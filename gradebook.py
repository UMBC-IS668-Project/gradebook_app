from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, redirect, render_template, request, url_for, json
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from mysql import connector
from werkzeug.exceptions import HTTPException

# Breadcrumb set up from https://usersnap.com/blog/breadcrumbs/

app = Flask(__name__)
app.debug = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="",
    password="",
    hostname="",
    databasename="",
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
        return render_template("create_login.html")

    # If post...
    # Check if the form has been filled out
    for i in request.form:
        if request.form[i] is None or request.form[i] == "":
            return render_template("create_login.html", message="The form must be filled out!")

    # Check if form entries are within 128 characters
    for i in request.form:
        if len(request.form[i]) > 128:
            return render_template("create_login.html", message="Please enter 128 characters or fewer for each field")

    if current_user.is_authenticated:
        return render_template("create_login.html", message="You are already logged in!")

    user = load_user(request.form["username"])
    if user:
        return render_template("create_login.html", message="Choose a different username!")

    if request.form.get("password") != request.form.get("password_confirm"):
        return render_template("create_login.html", message="Your passwords did not match!")

    new_user = User()
    new_user.user_name = request.form["username"]
    new_user.password_hash = generate_password_hash(request.form["password"])
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return render_template("create_login.html", message="Your account has been created!")
    # return render_template("create_login.html", message="This feature has not been enabled for PythonAnywhere!")


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/students/", methods=["GET"])
@login_required
def student():
    if request.method == "GET":
        # Subquery to get assignments using grade entries
        grade_return_inner = db.session.query(
            Assignment.assignment_ID,
            Assignment.assignment_name,
            Grade.student_ID,
            Grade.grade,
            ).select_from(Assignment).join(Grade, isouter=True).subquery()

        # Subquery to get aggregate grade for students, assuming equal weighting.
        student_return_inner = db.session.query(
            Student.student_ID,
            (db.func.round((db.func.sum(Grade.grade)/db.func.count(Grade.grade)),3)).label(
             "agg_grade")).select_from(Student).join(Grade).group_by(Student.student_ID).subquery()

        student_return = db.session.query(
            Student.student_ID,
            Student.first_name,
            Student.last_name,
            Student.major,
            Student.email_address,
            grade_return_inner.c.assignment_ID,
            grade_return_inner.c.assignment_name,
            grade_return_inner.c.grade,
            student_return_inner.c.agg_grade).select_from(Student).join(student_return_inner,
                student_return_inner.c.student_ID == Student.student_ID, isouter=True).join(grade_return_inner,
            grade_return_inner.c.student_ID == Student.student_ID, isouter=True).order_by(Student.first_name)

        student_outer_return = db.session.query(
           Student.student_ID,
            Student.first_name,
            Student.last_name,
            Student.major,
            Student.email_address,
            student_return_inner.c.agg_grade).select_from(Student).join(student_return_inner,
            student_return_inner.c.student_ID == Student.student_ID, isouter=True).order_by(Student.first_name)

        return render_template(
            "students.html",
            student_display=student_outer_return,
            grade_display=student_return
        )
    else:
        return redirect(url_for("index"))


@app.route("/student_grades/<student_get_ID>", methods=["GET"])
@login_required
def student_grades(student_get_ID= None):
    if request.method == "GET":
        grade_return_inner = db.session.query(
            Student.first_name,
            Student.last_name,
            Grade.student_ID,
            Grade.assignment_ID,
            Grade.grade).select_from(Student).join(
            Grade, isouter=True).filter(
            Grade.student_ID == student_get_ID).subquery()

        grade_return = db.session.query(
            Assignment.assignment_ID,
            Assignment.assignment_name,
            grade_return_inner.c.student_ID,
            grade_return_inner.c.grade,
            grade_return_inner.c.first_name,
            grade_return_inner.c.last_name
            ).select_from(Assignment).join(
            grade_return_inner, grade_return_inner.c.assignment_ID == Assignment.assignment_ID, isouter=True)

        student_get = db.session.query(
                Student.student_ID,
                Student.first_name,
                Student.last_name,
                Student.major,
                Student.email_address
                ).select_from(Student).filter(Student.student_ID == student_get_ID).first()

        return render_template("student_grades.html", grade_display=grade_return, student_display=student_get)
    else:
        return redirect(url_for("index"))


@app.route("/assignments/", methods=["GET"])
@login_required
def assignment():
    if request.method == "GET":

        grade_return_inner = db.session.query(
            Student.student_ID,
            Student.first_name,
            Student.last_name,
            Grade.grade,
            Grade.assignment_ID
            ).select_from(Student).join(Grade, isouter=True).subquery()

        grade_return = db.session.query(
            Assignment.assignment_ID,
            Assignment.assignment_name,
            grade_return_inner.c.student_ID,
            grade_return_inner.c.first_name,
            grade_return_inner.c.last_name,
            grade_return_inner.c.grade
            ).select_from(Assignment).join(
                grade_return_inner,
                grade_return_inner.c.assignment_ID == Assignment.assignment_ID,
                isouter=True)

        return render_template("assignments.html", assignment_display=Assignment.query.all(),
                               grade_display=grade_return)
    else:
        return redirect(url_for("index"))


@app.route("/assignment_grades/<assign_get_ID>", methods=["GET"])
@login_required
def assignment_grades(assign_get_ID= None):
    if request.method == "GET":
        grade_return_inner = db.session.query(Student.student_ID, Grade.grade, Assignment.assignment_ID,
            Assignment.assignment_name).select_from(Student).join(Grade).\
            join(Assignment).filter_by(assignment_ID=assign_get_ID).subquery()

        assign_get = db.session.query(
            Assignment.assignment_ID,
            Assignment.assignment_name
            ).select_from(Assignment).filter(Assignment.assignment_ID == assign_get_ID).first()

        grade_return = db.session.query(
            grade_return_inner.c.assignment_ID,
            grade_return_inner.c.assignment_name,
            grade_return_inner.c.grade,
            Student.student_ID,
            Student.first_name,
            Student.last_name
            ).select_from(Student).join(grade_return_inner, grade_return_inner.c.student_ID ==
                Student.student_ID, isouter=True).order_by(Student.first_name)

        return render_template("assignment_grades.html", grade_display=grade_return, grade_assignment=assign_get)
    else:
        return redirect(url_for("index"))


@app.route("/create_student/", methods=["GET", "POST"])
@login_required
def create_student():
    if request.method == "GET":
        return render_template("create_student.html")

    # Validate input

    # Check if the form has been filled out.
    for i in request.form:
        if request.form[i] is None or request.form[i] == "":
            return render_template("create_student.html", message="The form must be filled out")

    # Check if form entries are within 45 characters
    for i in request.form:
        if len(request.form[i]) > 45:
            return render_template("create_student.html", message="Please enter 45 characters or fewer for each field")

    # Check if the student has been entered already
    student_check = Student.query.filter_by(
        first_name=request.form["first_name"].lower(),
        last_name=request.form["last_name"].lower(),
        email_address=request.form["email_address"].lower()).first()

    if student_check is not None:
        return render_template("create_student.html", message="This entry already exists")

    new_student = Student()
    new_student.first_name = request.form["first_name"]
    new_student.last_name = request.form["last_name"]
    new_student.email_address = request.form["email_address"]
    new_student.major = request.form["major"]
    db.session.add(new_student)
    db.session.commit()

    return render_template("create_student.html", message="The student was added successfully")


@app.route("/edit_student/<int:edit_ID>", methods=["GET", "POST"])
@login_required
def edit_student(edit_ID=None):
    student_return = db.session.query(
        Student.student_ID,
        Student.first_name,
        Student.last_name,
        Student.email_address,
        Student.major).select_from(Student).filter(Student.student_ID == edit_ID).first()

    if request.method == "GET":
        if edit_ID is not None:
            return render_template("edit_student.html", student_display=student_return)
        else:
            return render_template("edit_student.html", student_display="")

    # Validate input

    # Check if form entries are within 45 characters
    for i in request.form:
        if len(request.form[i]) > 45:
            return render_template("edit_student.html", student_display=student_return,
                                   message="Please enter 45 characters or fewer for each field")

    # Check if the form has been filled out.
    for i in request.form:
        if request.form[i] is None or request.form[i] == "":
            return render_template("edit_student.html", message="The form must be filled out!")

    ed_student = Student.query.filter_by(student_ID=edit_ID).first()
    if ed_student is None:
        return render_template("edit_student.html", message="The student entry could not be found")

    ed_student.first_name = request.form["first_name"]
    ed_student.last_name = request.form["last_name"]
    ed_student.email_address = request.form["email_address"]
    ed_student.major = request.form["major"]
    db.session.add(ed_student)
    db.session.commit()

    return render_template("edit_student.html", student_display=ed_student,
                           message="The student was edited successfully")


@app.route("/delete_student/<delete_ID>", methods=["GET", "POST", "DELETE"])
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
        return render_template("delete_student.html", message="Nothing to delete!")
    db.session.delete(del_student)
    db.session.commit()

    return render_template("delete_student.html", message="The student was deleted successfully")


@app.route("/create_assignment/", methods=["GET", "POST"])
@login_required
def create_assignment():
    if request.method == "GET":
        return render_template("create_assignment.html")

    # If post...
    # Check if anything has been entered.
    for i in request.form:
        if request.form[i] is None or request.form[i] == "":
            return render_template("create_assignment.html", message="The form must be filled out")

    # Check if form entries are within 45 characters
    for i in request.form:
        if len(request.form[i]) > 45:
            return render_template("create_assignment.html",
                                   message="Please enter 45 characters or fewer for each field")

    # Check if an assignment with a matching name exists
    assignment_check = Assignment.query.filter_by(assignment_name=request.form["assignment_name"]).first()
    if assignment_check is not None:
        return render_template("create_assignment.html", message="There is already an assignment with this name")

    new_assignment = Assignment()
    new_assignment.assignment_name = request.form["assignment_name"]
    db.session.add(new_assignment)
    db.session.commit()

    return render_template("create_assignment.html", message="The assignment was added successfully")


@app.route("/edit_assignment/<int:edit_ID>", methods=["GET", "POST", "PUT"])
@login_required
def edit_assignment(edit_ID=None):
    assignment_return = db.session.query(
        Assignment.assignment_ID,
        Assignment.assignment_name
    ).select_from(Assignment).filter(Assignment.assignment_ID == edit_ID).first()

    if request.method == "GET":
        if edit_ID is not None:
            return render_template("edit_assignment.html", assignment_display=assignment_return)
        else:
            return render_template("edit_assignment.html", assignment_display="")

    # If post...
    # Validate input

    # Check if anything has been entered.
    for i in request.form:
        if request.form[i] is None or request.form[i] == "":
            return render_template("edit_assignment.html", assignment_display=assignment_return,
                                   message="The form must be filled out")

    # Check if form entries are within 45 characters
    for i in request.form:
        if len(request.form[i]) > 45:
            return render_template("edit_assignment.html", assignment_display=assignment_return,
                                   message="Please enter 45 characters or fewer for each field")

    # Check if the assignment exists
    ed_assignment = Assignment.query.filter_by(assignment_ID=edit_ID).first()
    if ed_assignment is None:
        return render_template("edit_assignment.html", assignment_display=assignment_return,
                               message="Nothing to edit")

    # Check if the new assignment name is a duplicate
    assignment_check = Assignment.query.filter_by(assignment_name=request.form["assignment_name"]).first()
    if assignment_check is not None:
        return render_template("edit_assignment.html", assignment_display=assignment_return,
                               message="There is already an assignment with this name")

    ed_assignment.assignment_name = request.form["assignment_name"]
    db.session.add(ed_assignment)
    db.session.commit()

    return render_template("edit_assignment.html",
                           assignment_display=ed_assignment, message="The entry has been edited successfully")


@app.route("/delete_assignment/<delete_ID>", methods=["GET", "POST", "DELETE"])
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
        return render_template("delete_assignment.html", message="Nothing to delete")

    db.session.delete(del_assignment)
    db.session.commit()

    return render_template("delete_assignment.html", message="The assignment was deleted successfully")


@app.route("/create_grade/<assign_get_ID>/<student_get_ID>/", methods=["GET", "POST"])
def create_grade(assign_get_ID=None, student_get_ID=None):
    assign_return = db.session.query(
        Assignment.assignment_ID,
        Assignment.assignment_name,
    ).select_from(Assignment).filter(Assignment.assignment_ID == assign_get_ID).first()

    student_return = db.session.query(
        Student.student_ID,
        Student.first_name,
        Student.last_name
    ).select_from(Student).filter(Student.student_ID == student_get_ID).first()

    if request.method == "GET":
        if assign_get_ID is not None and student_get_ID is not None:
            return render_template("create_grade.html", assignment_display=assign_return,
                                   student_display=student_return)
        else:
            return render_template("create_grade.html", assignment_display="", student_display="",
                                   message="No IDs!")

    # If post...
    # Validate input
    # Check if the form has been filled out
    for i in request.form:
        if request.form[i] is None or request.form[i] == "":
            return render_template("create_grade.html", assignment_display=assign_return,
                                   student_display=student_return, message="The form must be filled out")

    # Check if the grade entry is a number:
    try:
        float(request.form["grade"])
    except ValueError:
        return render_template("create_grade.html", assignment_display=assign_return,
                               student_display=student_return, message="You must enter a number")

    # Make sure there is no whitespace
    if " " in request.form["grade"]:
        return render_template("create_grade.html", assignment_display=assign_return,
                               student_display=student_return, message="No whitespace can be entered")

    # Check if there is already a matching grade entry
    match_check = Grade.query.filter_by(assignment_ID=assign_get_ID,
                                        student_ID=student_get_ID).first()
    if match_check is not None:
        return render_template("create_grade.html", assignment_display=assign_return,
                               student_display=student_return, message="There is already a grade entry")

    new_grade = Grade()
    new_grade.grade = request.form["grade"]
    new_grade.assignment_ID = assign_get_ID
    new_grade.student_ID = student_get_ID
    db.session.add(new_grade)
    db.session.commit()

    return render_template("create_grade.html", assignment_display=assign_return,
                           student_display=student_return, message="The grade was added successfully")


@app.route("/edit_grade/<assign_get_ID>/<student_get_ID>/", methods=["GET", "POST"])
def edit_grade(assign_get_ID=None, student_get_ID=None):
    if assign_get_ID is not None and student_get_ID is not None:
        grade_return = db.session.query(
            Assignment.assignment_ID,
            Assignment.assignment_name,
            Grade.grade,
            Student.student_ID,
            Student.first_name,
            Student.last_name
        ).select_from(Assignment).filter(Assignment.assignment_ID == assign_get_ID,
                                         Grade.student_ID == student_get_ID,
                                         Grade.student_ID == Student.student_ID,
                                         Grade.assignment_ID == Assignment.assignment_ID).first()
    else:
        return render_template("edit_grade.html", grade_display="", message="No IDs")

    if request.method == "GET":
        return render_template("edit_grade.html", grade_display=grade_return)

    # If post...
    # Validate input
    # Check if the form has been filled out
    for i in request.form:
        if request.form[i] is None or request.form[i] == "":
            return render_template("edit_grade.html", grade_display=grade_return,
                                   message="The form must be filled out")

    # Check if the grade entry is a number:
    try:
        float(request.form["grade"])
    except ValueError:
        return render_template("edit_grade.html", grade_display=grade_return, message="You must enter a number")

    # Make sure there is no whitespace
    if " " in request.form["grade"]:
        return render_template("edit_grade.html", grade_display=grade_return, message="No whitespace can be included")

    # Get the grade entry, make sure it exists
    ed_grade = Grade.query.filter_by(assignment_ID=assign_get_ID, student_ID=student_get_ID).first()
    if ed_grade is None:
        return render_template("edit_grade.html", message="The grade entry could not be found")

    ed_grade.grade = request.form["grade"]
    db.session.add(ed_grade)
    db.session.commit()

    return render_template("edit_grade.html", grade_display=grade_return,
                           message="The grade was edited successfully!", new_grade=request.form["grade"])


@app.route("/delete_grade/<assign_get_ID>/<student_get_ID>/", methods=["GET", "POST", "DELETE"])
@login_required
def delete_grade(assign_get_ID=None, student_get_ID=None, message=None):
    if request.method == "GET":
        if assign_get_ID is not None and student_get_ID is not None:
            grade_return = db.session.query(
                Assignment.assignment_ID,
                Assignment.assignment_name,
                Grade.grade,
                Student.student_ID,
                Student.first_name,
                Student.last_name
                ).select_from(Assignment).filter(Assignment.assignment_ID == assign_get_ID,
                                                 Student.student_ID == student_get_ID).first()

            return render_template("delete_grade.html", grade_display=grade_return)

        else:
            return render_template("delete_grade.html", grade_display="", message="No IDs")

    # If post...

    del_grade = Grade.query.filter_by(assignment_ID=assign_get_ID, student_ID=student_get_ID).first()
    if del_grade is None:
        return render_template(
            "delete_grade.html",
            assignment_ID=assign_get_ID,
            student_ID=student_get_ID,
            message="The entry could not be found to be deleted"
        )
    db.session.delete(del_grade)
    db.session.commit()

    return render_template("delete_grade.html", grade_display=del_grade, message="The grade has been deleted")


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
