import smtplib
from email.message import EmailMessage
import os

def enviar_email(destinatario, assunto, corpo):
    msg = EmailMessage()
    msg['From'] = os.getenv('MAIL_USERNAME')  # pega do .env
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.set_content(corpo, subtype='html')  # se quiser mandar html

    try:
        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.starttls()
            server.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
            server.send_message(msg)
        print("Email enviado com sucesso")
    except Exception as e:
        print("Erro ao enviar email:", e)
