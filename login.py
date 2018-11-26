from flask import render_template, session, request, url_for, redirect, flash

from __main__ import db, app, Team, Chore, User, logger


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