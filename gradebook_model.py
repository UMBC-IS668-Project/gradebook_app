from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import Flask, redirect, render_template, request, url_for
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from mysql import connector

db = SQLAlchemy()
class User(UserMixin, db.Model):
	
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return(self.user_name)

class Comment(db.Model):

    __tablename__ = "comment"
    commenter_ID = db.Column(db.Integer, db.ForeignKey(User.user_id))
    comment_ID = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    comment_time_stamp = db.Column(db.DateTime, default=datetime.now)
    user_constraint = db.relationship('User', foreign_keys=commenter_ID)

class Student(db.Model):

    __tablename__ = "student"
    student_ID = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email_address = db.Column(db.String(45))
    major = db.Column(db.String(45))

class School_Class(db.Model):

    __tablename__ = "school_class"
    class_ID = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(45))
    department = db.Column(db.String(45))

class School_Class_Offering(db.Model):

    __tablename__ = "school_class_offering"
    class_offering_ID = db.Column(db.Integer, primary_key = True)
    class_ID = db.Column(db.Integer)
    semester = db.Column(db.String(45))
    class_year = db.Column(db.Integer)
    class_ID_constraint = db.relationship('school_class', foreign_keys = class_ID)

class Student_School_Class_Offering(db.Model):

    __tablename__
    student_school_class_offering_id = db.Column(db.Integer, primary_key = True)
    class_offering_ID = db.Column(db.Integer)
    student_ID = db.Column(db.Integer)
    student_ID_constraint = db.relationship('student', foreign_keys = student_ID)
    class_offering_ID_constraint = db.relationship('school_class_offering', foreign_keys = class_offering_id)

class Assignment(db.Model):

    __tablename__
    assignment_ID = db.Column(db.Integer, primary_key = True)
    assignment_name = db.Column(db.String(128))
    class_offering_ID = db.Column(db.Integer)
    class_offering_ID_assignment_constraint = db.relationship('school_class_offering', foreign_keys = class_offering_ID)

class Grade(db.Model):

    __tablename__
    grade_ID = db.Column(db.Integer, primary_key = True)
    assignment_ID = db.Column(db.Integer)
    student_ID = db.Column(db.Integer)
    grade = db.Column(db.Float)
    assignment_ID_grade_constraint = db.relationship('assignment', foreign_keys = assignment_ID)
    student_ID_grade_constraint = db.relationship('student', foreign_keys = student_ID)
