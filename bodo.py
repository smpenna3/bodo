from flask import Flask, render_template, redirect, session, request, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import logging, logging.handlers
from random import shuffle
import random as random
import time
from apscheduler.schedulers.background import BackgroundScheduler
from calendarGmail import *


# Get random seed
random.seed(time.time())

# Setup scheduler
scheduler = BackgroundScheduler()
scheduler.start()

### Setup logging
applogs_directory = './app_logs/'
logFile = os.path.join(applogs_directory, 'debug.log')
errorLogFile = os.path.join(applogs_directory, 'error.log')

if not os.path.exists(applogs_directory):
	# If not, create it
	os.makedirs(applogs_directory)

logger = logging.getLogger('mainLog')
logger.setLevel(logging.DEBUG)

# Setup a formatter for the normal logging and error logging 
# (error has filename and line, standard doesn't for space considerations)
sformatter = logging.Formatter('%(asctime)-23s - %(name)-9s - [%(levelname)-8s] - %(message)s')
eformatter = logging.Formatter('%(asctime)-23s - %(filename)-20s - %(lineno)-4s ' \
								+ '- [%(levelname)-8s] - %(message)s')

# Setup handlers for the regular file handler
rfh = logging.handlers.RotatingFileHandler(logFile, \
			maxBytes=(5*1024*1024), backupCount=5)
rfh.setLevel(logging.DEBUG)
# Setup handlers for the error file handler
err = logging.handlers.RotatingFileHandler(errorLogFile, \
			maxBytes=(5*1024*1024), backupCount=5)

err.setLevel(logging.WARNING)
# Setup handler for stream
stream = logging.StreamHandler()

# Add the formatters
rfh.setFormatter(sformatter)
err.setFormatter(eformatter)
stream.setFormatter(sformatter)

# Add the handlers to the logger
logger.addHandler(rfh)
logger.addHandler(err)
logger.addHandler(stream)


# Setup flask and database
app = Flask(__name__)
basedir = os.path.join(os.path.dirname(__file__), 'bodo.db')
db_uri = 'sqlite:///{}'.format(basedir)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'bodo 420'

# Setup database object
db = SQLAlchemy(app)
logger.info('Database setup')


# Class for the user table, holding all users, passwords, and random data
class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(50))
	email = db.Column(db.String(50))
	phone = db.Column(db.String(50))
	teamNameId = db.Column(db.Integer, db.ForeignKey('team.id'))
	chore = db.relationship('Chore', backref='user', lazy='dynamic')

	def __init__(self, username, password, email, phone, **kwargs):
		super(User, self).__init__(**kwargs)
		self.username = username
		self.password = password
		self.email = email
		self.phone = phone
		

	def __repr__(self):
		return '<User %r, Email %r, Phone %r>' % (self.username,  self.email,  self.phone)


# Class for the team table, holding the users and chores
class Team(db.Model):
	__tablename__ = 'team'
	id = db.Column(db.Integer, primary_key=True)
	teamName = db.Column(db.String(50), unique=True)
	teamKey = db.Column(db.String(50))
	numMembers = db.Column(db.Integer)
	numChores = db.Column(db.Integer)
	user = db.relationship('User', backref='team', lazy='dynamic')
	chore = db.relationship('Chore', backref='team', lazy='dynamic')

	def __init__(self, teamName, teamKey, **kwargs):
		super(Team, self).__init__(**kwargs)
		self.teamName = teamName
		self.teamKey = teamKey
		self.numChores = 0


# Class for the chores	
class Chore(db.Model):
	__tablename__ = 'chore'
	id = db.Column(db.Integer, primary_key=True)
	teamNameId = db.Column(db.Integer, db.ForeignKey('team.id'))
	name = db.Column(db.String(50))
	DOW = db.Column(db.Integer)
	assignment = db.Column(db.String(50))
	userID = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(self, name, DOW, **kwargs):
		super(Chore, self).__init__(**kwargs)
		self.name = name
		self.DOW = DOW
		self.assignment = ''


# Run app
if __name__ == '__main__':
	from login import *  # Import the login and signup routes
	from chores import *  # Import the chores routes
	from settings import *  # Import the settings routes
	from routes import *  # Import other routes

	scheduler.add_job(assign, 'cron', day_of_week='sat', hour='1')
	logger.debug("Cron job added to update jobs every saturday at 1am")
	app.run(host='0.0.0.0', debug=True, use_reloader=False)