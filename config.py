import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

class Config:
    # Segurança
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Jackzera456')

    # Banco de dados
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'Giovanna')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Jackzera456')
    DB_NAME = os.environ.get('DB_NAME', 'Atestto')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pastas de arquivos
    UPLOAD_FOLDER = 'uploads'
    CONVERTED_FOLDER = 'converted'
    SIGNED_FOLDER = 'signed'

    # E-mail (Flask-Mail)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'fgiovanna16@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'wxiotfjtmeexmosf')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
