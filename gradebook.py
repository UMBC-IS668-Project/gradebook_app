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

#Routes

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comment_display=db.session.query(Comment.content, Comment.commenter_ID,
                                                                                  Comment.comment_time_stamp,
                                                                                  User.user_name).select_from(
            Comment).join(User).order_by(desc(Comment.comment_time_stamp)))

    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    comment = Comment(content=request.form["contents"], commenter_ID=current_user.user_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('index'))


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
    return redirect(url_for('index'))


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
    return redirect(url_for('index'))

#Models
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return(self.user_name)


class Student(db.Model):

    __tablename__ = "student"
    student_ID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email_address = db.Column(db.String(45))
    major = db.Column(db.String(45))


class Assignment(db.Model):

    __tablename__
    assignment_ID = db.Column(db.Integer, primary_key = True)
    assignment_name = db.Column(db.String(128))


class Grade(db.Model):

    __tablename__
    grade_ID = db.Column(db.Integer, primary_key = True)
    assignment_ID = db.Column(db.Integer)
    student_ID = db.Column(db.Integer)
    grade = db.Column(db.Float)
    assignment_ID_grade_constraint = db.relationship('assignment', foreign_keys = assignment_ID)
    student_ID_grade_constraint = db.relationship('student', foreign_keys = student_ID)
    
 class Comment(db.Model):
    
    __tablename__ = "comment"
    commenter_ID = db.Column(db.Integer, db.ForeignKey(User.user_id))
    commentID = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    comment_time_stamp = db.Column(db.DateTime, default=datetime.now)
    user_constraint = db.relationship('User', foreign_keys=commenter_ID)
