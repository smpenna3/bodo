from flask import render_template, session, request, url_for

from __main__ import db, app, Team, Chore, User, logger


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