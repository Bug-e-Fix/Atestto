import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

def enviar_email(destinatario, assunto, corpo_html):
    try:
        smtp_server = os.getenv('MAIL_SERVER')
        smtp_port = int(os.getenv('MAIL_PORT', 587))
        use_tls = os.getenv('MAIL_USE_TLS', 'True') == 'True'
        use_ssl = os.getenv('MAIL_USE_SSL', 'False') == 'True'
        username = os.getenv('MAIL_USERNAME')
        password = os.getenv('MAIL_PASSWORD')

        msg = EmailMessage()
        msg['From'] = username
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg.set_content(corpo_html, subtype='html')

        if use_ssl:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(username, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                if use_tls:
                    server.starttls()
                server.login(username, password)
                server.send_message(msg)

        print(f"✅ Email enviado com sucesso para: {destinatario}")
        return True
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False
