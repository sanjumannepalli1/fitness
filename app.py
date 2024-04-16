import flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Column, Integer, DateTime, func
import os
from sqlalchemy import and_
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import json
import pdb
import random

from datetime import datetime
import os
import dotenv

app = flask.Flask(__name__)

if os.path.exists('.env'):
    dotenv.load_dotenv('.env')


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_SECRET'] = os.getenv('SESSION_SECRET', os.urandom(64))
app.config['SQLALCHEMY_ECHO'] = app.config['DEBUG']
app.config['SESSION_COOKIE_SAMESITE'] = "None"
app.config['SESSION_COOKIE_SECURE'] = True

app.secret_key = app.config['SESSION_SECRET']

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False)
    user_email = db.Column(db.String(120), nullable=False)
    user_password = db.Column(db.String(120), nullable=False)
    time_stamp = db.Column(DateTime, default=func.now())

    def __init__(self, user_name, user_email, user_password, time_stamp):
        self.user_name = user_name
        self.user_email = user_email
        self.user_password = user_password
        self.time_stamp = time_stamp

    def __repr__(self):
        return '<User id=%d bc_id=%s email=%s>' % (self.id, self.user_name, self.user_email)


class FeedBack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('feedbacks', lazy=True))
    time_stamp = db.Column(DateTime, default=func.now())

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the 'username' from the session
    return render_template('login.html')


@app.route('/register', methods=['GET',  'POST'])
def register():
   # pdb.set_trace()
    if request.method == 'POST':
        username = request.form['username']
        pswd = request.form['password']
        user_email = request.form['useremail']
        # check the user name in databse
        existing_user = User.query.filter_by(user_name = username).first()


        if existing_user:
            # flash('Username already exists', 'error')
            return jsonify({'exists': True})
           # return render_template('register.html', message='Username already exists. Please choose another.')
        else:

            new_user = User(user_name=username, user_email=user_email, user_password=pswd, time_stamp = datetime.now())

            # Add the user to the database
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.', 'success')
            # return redirect(url_for('login'))
            return render_template('login.html')
    else:

        return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    # pdb.set_trace()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        current_user = User.query.filter_by(user_name=username, user_password=password).first()
        if current_user:
            session['username'] = username
            flash('Login successful', 'success')

            return render_template('index.html', user = current_user)
        else:
            print("please check the creds")
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)
    else:

        return render_template('login.html')



@app.route('/submit_feedback', methods=['GET', 'POST'])
def submit_feedback():
   # pdb.set_trace()
    current_user = session['username']
    feedback = request.json.get('feedback_message')
    user_id = User.query.filter_by(user_name=current_user).first().id
    feedback = FeedBack(content=feedback, user_id=user_id, time_stamp = datetime.now())
    db.session.add(feedback)
    db.session.commit()
    # Process the review submission, store it in the database, etc.

    # Return a response (you can customize the response based on success or failure)
    return jsonify({'message': 'Feedback submitted successfully'})



@app.route('/begginer', methods=['GET'])
def begginer():
    if 'username' in session:
        return render_template('begginer.html', user=session['username'])
    else:
        return render_template('index.html', cache_timeout=0)

@app.route('/expert', methods=['GET'])
def expert():
    if 'username' in session:
        return render_template('expert.html', user=session['username'])
    else:
        return render_template('index.html', cache_timeout=0)

@app.route('/beginner_course', methods=['GET'])
def begginer_course():
   #  pdb.set_trace()
    return render_template('beginner_course.html', user=session['username'])


@app.route('/intermediate_course', methods=['GET'])
def intermediate_course():
   # pdb.set_trace()
    return render_template('intermediate_course.html', user=session['username'])

@app.route('/expert_course', methods=['GET'])
def expert_course():
   # pdb.set_trace()
    return render_template('expert_course.html', user=session['username'])


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
