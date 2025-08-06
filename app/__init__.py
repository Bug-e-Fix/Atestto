from flask import Flask
from app.extensions import csrf, login_manager
from dotenv import load_dotenv
from app.extensions import mail

import os

def create_app():
    load_dotenv()  # <- Isso garante que o .env seja lido
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_PORT=int(os.getenv("MAIL_PORT")),
        MAIL_USE_TLS=os.getenv("MAIL_USE_TLS") == "True",
        MAIL_USE_SSL=os.getenv("MAIL_USE_SSL") == "True",
    )

    csrf.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # register blueprints etc
    return app
