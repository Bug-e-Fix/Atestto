# app/services/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app, url_for
from app.services.token_service import generate_token
from email.header import Header

def send_confirmation_email(user):
    """
    Envia e-mail de confirmação usando as configs do Flask app.
    Recebe o objeto `user` com atributos `email` e `nome`.
    """
    user_email = user.email
    token = generate_token(user_email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)

    msg = MIMEMultipart()
    msg["From"] = current_app.config["MAIL_USERNAME"]
    msg["To"] = user_email

    # ⚡ Corrige Subject para UTF-8
    msg["Subject"] = str(Header("Confirme seu cadastro no Atestto", 'utf-8'))

    body = f"""
    <p>Oi, {user.nome}!</p>
    <p>Obrigado por se cadastrar no <b>Atestto</b>!</p>
    <p>Para ativar sua conta, clique no link abaixo:</p>
    <p><a href="{confirm_url}">Confirmar cadastro</a></p>
    <p>Se voce nao solicitou este cadastro, ignore este e-mail.</p>
    """

    # ⚡ Cria o corpo UTF-8 sem sobrescrever o MIMEMultipart
    body_part = MIMEText(body, 'html', 'utf-8')
    msg.attach(body_part)

    try:
        if current_app.config["MAIL_USE_SSL"]:
            with smtplib.SMTP_SSL(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"]) as server:
                server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
                server.sendmail(msg["From"], [msg["To"]], msg.as_string())
        else:
            with smtplib.SMTP(current_app.config["MAIL_SERVER"], current_app.config["MAIL_PORT"]) as server:
                server.starttls()
                server.login(current_app.config["MAIL_USERNAME"], current_app.config["MAIL_PASSWORD"])
                server.sendmail(msg["From"], [msg["To"]], msg.as_string())

        print(f"E-mail enviado com sucesso para {user_email}")
        return True
    except Exception as e:
        print(f"Erro ao enviar email para {user_email}: {e}")
        return False
