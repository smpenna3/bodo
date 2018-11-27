from __main__ import db

'''
	The database has three tables: Teams, Users, and Chores.

	The relationship between the Teams to Users is one-to-many, that is there
	can be many users per one team.  Each user only ever has one team though.

	The relationship between the Users to Chores is also one-to-many, that is
	there can be many chores per user, but each chore only ever has one user.
'''

# Class for the team table, holding the users and chores
class Team(db.Model):
	__tablename__ = 'teams'
	id = db.Column(db.Integer, primary_key=True)
	teamName = db.Column(db.String(50), unique=True)
	teamKey = db.Column(db.String(50))
	numMembers = db.Column(db.Integer)
	numChores = db.Column(db.Integer)


# Class for the user table, holding all users, passwords, and random data
class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(50))
	email = db.Column(db.String(50))
	phone = db.Column(db.String(50))
	team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
	team = db.relationship('Team', backref='users')

	def __repr__(self):
		return '<User %r, Email %r, Phone %r>' % (self.username,  self.email,  self.phone)

# Class for the chores	
class Chore(db.Model):
	__tablename__ = 'chores'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	DOW = db.Column(db.Integer)
	assignment = db.Column(db.String(50))
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user = db.relationship('User', backref='chores')