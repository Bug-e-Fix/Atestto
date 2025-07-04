from flask import Blueprint, current_app
from flask_mail import Message
from app.extensions import mail

teste_email_bp = Blueprint('teste_email', __name__)

@teste_email_bp.route('/teste-email')
def teste_email():
    try:
        msg = Message(
            subject='🚀 Teste com Brevo funcionando!',
            recipients=[current_app.config.get('MAIL_USERNAME')],  
            body='Oi Gio! Este e-mail foi enviado com Brevo + Flask! Tá voando!'
        )
        mail.send(msg)
        return "E-mail enviado com sucesso!"
    except Exception as e:
        return f"Erro ao enviar e-mail: {e}"
