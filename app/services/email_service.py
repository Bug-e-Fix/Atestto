from flask_mail import Message
from app.extensions import mail

def enviar_email(destinatario, assunto, corpo):
    msg = Message(
        subject=assunto,
        recipients=[destinatario],
        html=corpo
    )
    mail.send(msg)

