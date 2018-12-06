import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:lollipop99@localhost/JMR'
	SQLALCHEMY_TRACK_MODIFICATIONS = False