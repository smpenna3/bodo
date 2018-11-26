from flask import render_template, session, request, redirect

from __main__ import db, app, User, Chore, Team, logger


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