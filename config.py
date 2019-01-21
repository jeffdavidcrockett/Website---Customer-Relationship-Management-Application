import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	DEBUG = True
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:lollipop99@localhost/JMR'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	WTF_CSRF_ENABLED = True
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USERNAME = 'jmrtestsend@gmail.com'
	MAIL_PASSWORD = 'urpwcbejqcrflfmr'