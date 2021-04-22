#Not in use currently. Whole server is in gradebook.py
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
