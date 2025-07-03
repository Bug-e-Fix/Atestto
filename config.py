import os

class Config:
    # Segurança
    SECRET_KEY = os.getenv('SECRET_KEY', 'Jackzera456')

    # Banco de dados
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'Giovanna')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Jackzera456')
    DB_NAME = os.getenv('DB_NAME', 'Atestto')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pastas de arquivos
    UPLOAD_FOLDER = 'uploads'
    CONVERTED_FOLDER = 'converted'
    SIGNED_FOLDER = 'signed'

    # E-mail (Flask-Mail com Outlook)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.office365.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'seu-email@outlook.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'sua-senha-ou-senha-de-app')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
