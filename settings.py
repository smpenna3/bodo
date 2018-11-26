from flask import render_template, session, request, url_for

from __main__ import db, app, Team, Chore, User, logger


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