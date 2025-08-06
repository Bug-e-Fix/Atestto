# config.py
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    # Chave secreta para sessões e segurança
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_super_secret_key')

    # --- Configurações de e-mail ---
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)
    # --- FIM Configurações de e-mail ---

    # --- Configurações do Banco de Dados ---
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')
    # --- FIM Banco de Dados ---

    # --- Outras configurações ---
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    CONVERTED_FOLDER = os.getenv('CONVERTED_FOLDER', 'converted')
    SIGNED_FOLDER = os.getenv('SIGNED_FOLDER', 'signed')
    # --- FIM Outras configurações ---
