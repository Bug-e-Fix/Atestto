from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager


csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()

import pymysql
import os

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )
