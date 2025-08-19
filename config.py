import os
from cryptography.fernet import Fernet
from io import StringIO
from dotenv import load_dotenv
from load_encrypted_env import load_encrypted_env
load_encrypted_env()


# Carrega a chave
with open("secret.key", "rb") as f:
    key = f.read()

fernet = Fernet(key)

# Descriptografa o .env
with open(".env.encrypted", "rb") as f:
    encrypted_data = f.read()

# Agora suas variáveis podem ser acessadas normalmente
class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "default_salt")
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 465))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() == "true"
