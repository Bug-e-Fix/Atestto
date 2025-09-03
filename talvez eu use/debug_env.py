# debug_env.py
from load_encrypted_env import load_encrypted_env
import os

load_encrypted_env()

print("==== Valores lidos do env ====")
print("MAIL_USERNAME:", os.getenv("MAIL_USERNAME"))
print("MAIL_PASSWORD:", ("<presente>" if os.getenv("MAIL_PASSWORD") else "<vazio>"))
print("MAIL_SERVER:", os.getenv("MAIL_SERVER"))
print("MAIL_PORT:", os.getenv("MAIL_PORT"))
print("MAIL_USE_SSL:", os.getenv("MAIL_USE_SSL"))
print("MAIL_USE_TLS:", os.getenv("MAIL_USE_TLS"))
print("================================")
