from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager


csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()
