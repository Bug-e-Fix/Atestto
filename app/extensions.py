from flask_wtf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail

csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()
