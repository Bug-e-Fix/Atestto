# show_decrypted_env.py
from cryptography.fernet import Fernet

with open("secret.key","rb") as f:
    key = f.read()

fernet = Fernet(key)
with open(".env.encrypted","rb") as f:
    enc = f.read()

print(fernet.decrypt(enc).decode())
