from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.secret_key = b'd080de92a45b864b287c6fa44d12d184e4d24bef4be96981686415e2256f7763'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/travel_agency_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_USERNAME'] = 'velimirbicanin@gmail.com'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

mail = Mail(app)

from agency import routes
from agency import base