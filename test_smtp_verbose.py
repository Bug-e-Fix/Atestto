# test_smtp_verbose.py
from load_encrypted_env import load_encrypted_env
import os, sys, smtplib
from email.message import EmailMessage

# carrega .env.encrypted (uso da sua função existente)
load_encrypted_env()

SMTP_SERVER = os.getenv("MAIL_SERVER")
SMTP_PORT = int(os.getenv("MAIL_PORT") or 0)
USERNAME = os.getenv("MAIL_USERNAME")
PASSWORD = os.getenv("MAIL_PASSWORD")
USE_SSL = (os.getenv("MAIL_USE_SSL", "False").lower() == "true")
USE_TLS = (os.getenv("MAIL_USE_TLS", "False").lower() == "true")

print("Conexão:", SMTP_SERVER, SMTP_PORT, "SSL:", USE_SSL, "TLS:", USE_TLS)
print("Usuário:", USERNAME)
if not all([SMTP_SERVER, SMTP_PORT, USERNAME, PASSWORD]):
    print("Falta configuração. Verifique seu .env.encrypted.")
    sys.exit(1)

msg = EmailMessage()
msg["Subject"] = "Teste SMTP verbose"
msg["From"] = USERNAME
msg["To"] = USERNAME  # envia pra você mesmo
msg.set_content("Corpo do teste SMTP - ignore")

try:
    if USE_SSL:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10)
    else:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
    server.set_debuglevel(1)
    server.ehlo()
    if USE_TLS and not USE_SSL:
        server.starttls()
        server.ehlo()

    print("Tentando login...")
    server.login(USERNAME, PASSWORD)
    print("Login OK, enviando e-mail...")
    server.send_message(msg)
    print("E-mail enviado com sucesso")
    server.quit()
except Exception as e:
    print("ERRO:", type(e), e)
