from flask_mail import Message
from app.extensions import mail
from flask import current_app
import traceback

def enviar_email(destinatario, assunto, corpo_html):
    """
    Envia um e-mail com conteúdo HTML para o destinatário.
    """
    try:
        msg = Message(
            subject=assunto,
            recipients=[destinatario],
            html=corpo_html,
            sender=current_app.config['MAIL_USERNAME']  # Define o remetente
        )
        mail.send(msg)
        print(f"E-mail enviado com sucesso para {destinatario}")
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail para {destinatario}: {e}")
        traceback.print_exc()  # Mostra o erro completo no terminal para debug
        return False
