import os
from load_encrypted_env import load_encrypted_env

# Carrega o .env.encrypted
load_encrypted_env()

# Testa se as variáveis estão disponíveis
print("SECRET_KEY:", os.getenv("SECRET_KEY"))
print("MAIL_USERNAME:", os.getenv("MAIL_USERNAME"))
print("MAIL_PASSWORD:", os.getenv("MAIL_PASSWORD"))
print("DB_HOST:", os.getenv("DB_HOST"))
