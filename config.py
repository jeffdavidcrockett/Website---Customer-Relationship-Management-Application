import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	DEBUG = True
	SECRET_KEY = '***'
	SQLALCHEMY_DATABASE_URI = '***'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	WTF_CSRF_ENABLED = True
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USERNAME = '***'
	MAIL_PASSWORD = '***'