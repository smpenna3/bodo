from flask import Flask, render_template, redirect, session, request, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import logging
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

# Setup logging
formatter = ('%(asctime)s - [%(levelname)7s]. - %(message)s')
logging.basicConfig(format=formatter)
logger = logging.getLogger('mainlog')
logger.setLevel(logging.DEBUG)
#handler = logging.StreamHandler()
#handler.setFormatter(formatter)
#logger.addHandler(logging.StreamHandler())

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


# Runs the chore assign algorithm
@app.route('/assign')
def assign():
	logger.info("Starting Scramble")
	for teamObject in Team.query.all():
		logger.debug("On team: " + str(teamObject.teamName))
		# Check if the team has chores
		if(teamObject.numChores == 0):
			logger.warning("No chores")
		else:
			j = 0
			flag = 0
			a = range(0, len(teamObject.chore.all()))
			shuffle(a)
			while(1):
				if(flag):
					break
				else:
					for user in teamObject.user.all():
						if(j >= len(teamObject.chore.all())):
							logger.info('Team ' + str(teamObject.teamName) + ' Assignments Scrambled')
							flag = 1
							break
						else:
							chore = teamObject.chore.all()[a[j]]
							user.chore.append(chore)
							db.session.commit()

							# Send notifications
							#insertEvent(chore.name, chore.DOW, user.email)
						j += 1
			
	return redirect(url_for('chores'))


# Catch 404 errors
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


# Main landing page for the site, has links to login and signup
@app.route('/')
def landing():
	return render_template('landing.html')


# Logout page, clear session object
@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('landing'))


# Main page once user logs in, will have all user specific info
@app.route('/home')
def home():
	user = User.query.filter_by(username = session['username']).first()
	return render_template('home.html', User=user)


# Page for users to input a username and password
@app.route('/signup')
def signup():
	return render_template('signup.html')


# Page for team "management"
@app.route('/teams')
def team_management():
	teamObject = Team.query.filter_by(teamName = session['teamName']).first()	
	user = User.query.filter_by(username = session['username']).first()	
	return render_template('teams.html', Team=teamObject, User=user)


# Page for user settings
@app.route('/settings')
def settings():
	user = User.query.filter_by(username = session['username']).first()	
	return render_template('settings.html', User=user)	

# Page for changing team in user settings
@app.route('/settings', methods=['POST'])
def settings_post():
	teamName = request.form['teamName']
	teamKey = request.form['teamKey']
	teamAction = request.form['teamAction']

	# Check if the team name already exists if the user is trying to create a team, if so quit
	q = db.session.query(Team.id).filter(Team.teamName==teamName)
	if teamAction == 'create' and db.session.query(q.exists()).scalar():
		flash('That team name is already taken, please choose a new one')
		logger.warning("Team name already exists")
		return redirect(url_for('settings'))

	# IF the team name doesn't exist, create the team and add to database
	elif teamAction == 'create':
		team = Team(teamName, teamKey)
		team.numMembers = 0
		teamObject = team
		db.session.add(team)
		db.session.commit()
		#flash('Team ' + str(teamName) + ' created :)')
		logger.info("Team added")

	# Check if the team exists if the user is trying to join
	if ((teamAction == 'join') and not (db.session.query(q.exists()).scalar())):
		flash("The team you are trying to join does not exist")
		logger.warning("Team does not exist")
		return redirect(url_for('settings'))

	# Check if the team key is correct if the user is trying to join a team, if not quit
	o = Team.query.filter_by(teamName = teamName).first()
	if ((teamAction == 'join') and (o.teamKey != teamKey)):
		flash("The team key you provided is incorrect")
		logger.warning("Team key incorrect")
		return redirect(url_for('settings'))
	
	# If key is correct, find the team object to join
	elif teamAction == 'join':
		teamObject = db.session.query(Team).filter_by(teamName=teamName).first()

	# If all above conditions are satisfied, create the user in the database
	user = User.query.filter_by(username = session['username']).first()	
	teamObject.user.append(user)
	teamObject.numMembers += 1
	db.session.commit()
	session['teamName'] = teamName 

	return redirect(url_for('settings'))

# Page for chore manipulation
@app.route('/chores')
def chores():
	user = User.query.filter_by(username = session['username']).first()	
	return render_template('chores.html', User=user)

# Page to add chores to the team list
@app.route('/chores', methods=['POST'])
def chores_post():
	user = User.query.filter_by(username = session['username']).first()	

	# Add the chore to the user's team chore list
	session['choreName'] = request.form['name']
	session['choreDOW'] = request.form['DOW']

	# Get team object from user
	teamObject = user.team

	# If not create the chore
	chore = Chore(session['choreName'], session['choreDOW'])
	teamObject.chore.append(chore)
	teamObject.numChores += 1
	db.session.add(chore)
	db.session.commit()
	#flash('Chore added :)')
	logger.info("Chore added")

	return redirect(url_for('chores'))	


# Route to delete the chores from the table
@app.route('/delete/<choreid>', methods=['POST'])
def delete_chore(choreid):
	chore = Chore.query.filter_by(id=choreid).first()
	teamObject = Team.query.filter_by(teamName = session['teamName']).first()
	teamObject.numChores -= 1
	db.session.delete(chore)
	db.session.commit()
	logger.info("Chore deleted")
	#flash('Chore deleted :/')
	return redirect(url_for('chores'))

# Function to receive post from signup information text boxes
# Will check if username is available and if so, add to database
@app.route('/signup', methods=['POST'])
def signup_post():
	# Grab data from post
	session['username'] = request.form['username']
	password = request.form['password']
	session['email'] = request.form['email']
	session['phone'] = request.form['phone']
	teamAction = request.form['teamAction']
	session['teamName'] = request.form['teamName']
	session['teamKey'] = request.form['teamKey']

	logger.debug('Got Data: ' + session['username'] + '  ' + session['teamName'])

	# Check if the username already exists, if so quit
	q = db.session.query(User.id).filter(User.username==session['username'])
	if db.session.query(q.exists()).scalar():
		flash('That username is already taken, please choose another')
		logger.warning("User already exists")
		return redirect(url_for('signup'))

	# Check if the team name already exists if the user is trying to create a team, if so quit
	q = db.session.query(Team.id).filter(Team.teamName==session['teamName'])
	if teamAction == 'create' and db.session.query(q.exists()).scalar():
		flash('The team name you are trying to create is taken, please choose another')
		logger.warning("Team name already exists")
		return redirect(url_for('signup'))

	# IF the team name doesn't exist, create the team and add to database
	elif teamAction == 'create':
		team = Team(session['teamName'], session['teamKey'])
		team.numMembers = 0
		teamObject = team
		db.session.add(team)
		db.session.commit()
		#flash('Team ' + str(session['teamName']) + ' created :)')
		logger.info("Team added")

	# Check if the team exists if the user is trying to join
	if ((teamAction == 'join') and not (db.session.query(q.exists()).scalar())):
		flash("The team you are trying to join does not exist")
		logger.warning("Team does not exist")
		return redirect(url_for('signup'))

	# Check if the team key is correct if the user is trying to join a team, if not quit
	o = Team.query.filter_by(teamName = session['teamName']).first()
	if ((teamAction == 'join') and (o.teamKey != session['teamKey'])):
		flash("The team key you provided is incorrect")
		logger.warning("Team key incorrect")
		return redirect(url_for('signup'))
	
	# If key is correct, find the team object to join
	elif teamAction == 'join':
		teamObject = db.session.query(Team).filter_by(teamName=session['teamName']).first()

	# If all above conditions are satisfied, create the user in the database
	user = User(session['username'], password, session['email'], session['phone'])
	teamObject.user.append(user)
	teamObject.numMembers += 1
	db.session.add(user)
	db.session.commit()
	#flash('User ' + str(session['username']) + ' added :)')
	logger.info("User added")
	return redirect(url_for('home'))


# Login page, asking for username and password
@app.route('/login')
def login():
	return render_template('login.html')


# Function to receive info from login text boxes
# Checks to see if password is correct for that username, if so go to home
@app.route('/login', methods=['POST'])
def login_post():
	session['username'] = request.form['username']
	session['password'] = request.form['password']

	user = db.session.query(User).filter_by(username=session['username']).first()
	

	q = db.session.query(User.id).filter(User.username==session['username'])
	if not db.session.query(q.exists()).scalar():
		# If user does not exist
		flash("That username does not exist, if you are signing up please us the signup link")
		logger.warning("Username does not exist")
		return redirect(url_for('login'))
	
	# If user exists check for password
	user = User.query.filter_by(username = session['username']).first()
	if user.password == session['password']:
		# IF password is correct
		logger.info("User " + str(session['username']) + ' logged on')
		session['teamName'] = user.team.teamName
		return redirect(url_for('home'))
	
	# If password is wrong
	flash('Incorrect password')
	logger.warning('Incorrect password')
	return redirect(url_for('login'))


# Run app
if __name__ == '__main__':
	scheduler.add_job(assign, 'cron', day_of_week='sat', hour='1')
	logger.debug("Cron job added to update jobs every saturday at 1am")
	app.run(host='0.0.0.0', debug=True, use_reloader=False)