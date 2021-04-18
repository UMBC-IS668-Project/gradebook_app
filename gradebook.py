from flask_sqlalchemy import SQLAlchemy
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

class User(UserMixin, db.Model):
	
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return(self.user_name)

@login_manager.user_loader
def load_user(entered_name):
    return User.query.filter_by(user_name = entered_name).first()

class Comment(db.Model):

    __tablename__ = "comment"
    commenter_ID = db.Column(db.Integer, db.ForeignKey(User.user_id))
    commentID = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    comment_time_stamp = db.Column(db.DateTime, default=datetime.now)
    user_constraint = db.relationship('User', foreign_keys=commenter_ID)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html",comment_display=db.session.query(Comment.content, Comment.commenter_ID, Comment.comment_time_stamp, User.user_name).select_from(Comment).join(User).all())
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    comment = Comment(content=request.form["contents"], commenter_ID = current_user.user_id)
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

    entered_password = request.form["password"]
    new_user = User(user_name=request.form["username"], password_hash = generate_password_hash(request.form["password"]))
    db.session.add(new_user)
    db.session.commit()	

    login_user(new_user)
    return render_template("create_login.html", account_success=True)

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

