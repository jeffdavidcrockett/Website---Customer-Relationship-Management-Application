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
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	email = db.Column(db.String(120), unique=True)
	credit_score = db.Column(db.String(32))
	signup_date = db.Column(db.String(20), index=True)
	status = db.Column(db.String(50))
	loan_type = db.Column(db.String(50))
	business_name = db.Column(db.String(50))
	business_class = db.Column(db.String(50))
	business_phone = db.Column(db.String(50))
	mobile_phone = db.Column(db.String(50))
	zip_code = db.Column(db.String(50))
	business_type = db.Column(db.String(100))
	loan_option = db.Column(db.String(50))
	loan_amount = db.Column(db.String(50))
	avg_monthly_income = db.Column(db.String(50))
	retirement = db.Column(db.String(50))
	company_type = db.Column(db.String(50))
	business_length = db.Column(db.String(50))
	company_website = db.Column(db.String(50))
	physical_biz_location = db.Column(db.String(50))
	business_plan = db.Column(db.String(50))
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
	client_id = db.Column(db.Integer)
	marketer = db.Column(db.String(30))
	date = db.Column(db.String(10))
	time = db.Column(db.String(30))
	type_of = db.Column(db.String(30))
	about = db.Column(db.String(140))


class ClientNote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	client_id = db.Column(db.Integer)
	marketer = db.Column(db.String(30))
	body = db.Column(db.String(140))


@login.user_loader
def load_user(id):
	return Marketer.query.get(int(id))
 