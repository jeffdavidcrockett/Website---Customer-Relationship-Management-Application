import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	DEBUG = True
	SECRET_KEY = os.environ.get('SECRET_KEY') or '***'
	SQLALCHEMY_DATABASE_URI = '***'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	WTF_CSRF_ENABLED = True
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USERNAME = '***'
	MAIL_PASSWORD = '***'