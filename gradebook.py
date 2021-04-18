from flask_sqlalchemy import SQLAlchemy
#from flask_sqlalchemy import ForeignKey
from flask_migrate import Migrate
from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime
from mysql import connector


app = Flask(__name__)
app.config["DEBUG"] = True
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
    userID = db.Column(db.Integer, primary_key = True)
    userName = db.Column(db.String(128))
    passwordHash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.passwordHash, password)

    def get_id(self):
        return(self.userName)

@login_manager.user_loader
def load_user(enteredName):
    return User.query.filter_by(userName = enteredName).first()

class Comment(db.Model):

    __tablename__ = "comment"
    commenterID = db.Column(db.Integer, db.ForeignKey(User.userID))
    commentID = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    commentTimeStamp = db.Column(db.DateTime, default=datetime.now)
    userConstraint = db.relationship('User', foreign_keys=commenterID)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html",commentDisplay=db.session.query(Comment.content, Comment.commenterID, Comment.commentTimeStamp, User.userName).select_from(Comment).join(User).all())
    if not current_user.is_authenticated:
        return redirect(url_for('index'))

    comment = Comment(content=request.form["contents"], commenterID = current_user.userID)
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

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

