from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime 


class Marketer(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	appointments = db.relationship('Appointment', backref='creator', lazy='dynamic')

	def __repr__(self):
		return self.username

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


class Client(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(64), index=True)
	last_name = db.Column(db.String(64), index=True)
	phone = db.Column(db.String(32))
	email = db.Column(db.String(120), index=True, unique=True)
	credit_score = db.Column(db.String(32), index=True)
	desired_funding = db.Column(db.String(20))
	signup_date = db.Column(db.String(20), index=True)
	appointments = db.relationship('Appointment', backref='client', lazy='dynamic')


class Appointment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	client_first = db.Column(db.String(120), index=True)
	client_last = db.Column(db.String(120), index=True)
	date = db.Column(db.Date, index=True)
	time = db.Column(db.String(30), index=True)
	notes = db.Column(db.String(120))
	marketer_id = db.Column(db.Integer, db.ForeignKey('marketer.id'))
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'))


class Memo(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(30), index=True)
	body = db.Column(db.String(140))
	date = db.Column(db.String(10), index=True)


class Note(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(30), index=True)
	body = db.Column(db.String(140))
	date = db.Column(db.String(10), index=True)


class Interaction(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	client_id = db.Column(db.Integer, index=True)
	marketer = db.Column(db.String(30), index=True)
	date = db.Column(db.String(10), index=True)
	time = db.Column(db.String(30), index=True)
	type_of = db.Column(db.String(30), index=True)
	about = db.Column(db.String(140), index=True)


@login.user_loader
def load_user(id):
	return Marketer.query.get(int(id))

