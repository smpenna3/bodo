from __main__ import db

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