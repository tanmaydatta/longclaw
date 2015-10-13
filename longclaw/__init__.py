from flask import Flask
from flask.ext.triangle import Triangle
from flask.ext.mail import Mail

app = Flask(__name__)
Triangle(app)
app.config.update(dict(
	DEBUG = True,
	MAIL_SERVER = 'smtp.gmail.com',
	MAIL_PORT = 465,
	MAIL_USE_TLS = False,
	MAIL_USE_SSL = True,
	MAIL_USERNAME = 'tanmaydatta@gmail.com',
	MAIL_PASSWORD = ''
	))
mail = Mail(app)

from longclaw import views