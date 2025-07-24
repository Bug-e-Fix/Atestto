import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'Jackzera456')

    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'Giovanna')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Jackzera456')
    DB_NAME = os.getenv('DB_NAME', 'Atestto')

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = 'uploads'
    CONVERTED_FOLDER = 'converted'
    SIGNED_FOLDER = 'signed'

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')

   
    try:
        MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    except ValueError:
        print("⚠️ Valor inválido para MAIL_PORT. Usando porta padrão 587")
        MAIL_PORT = 587

    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')

    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'equipe.atestto@outlook.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'sua_senha_de_app_aqui')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
