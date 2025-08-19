# app/extensions.py
from flask_login import LoginManager
from flask_mail import Mail

mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
