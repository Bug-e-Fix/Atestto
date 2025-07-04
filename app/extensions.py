from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail

csrf = CSRFProtect()
mail = Mail()
