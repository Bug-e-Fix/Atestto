from flask import Blueprint
from app.services.email_service import enviar_email

teste_email_bp = Blueprint('teste_email', __name__)

@teste_email_bp.route('/teste-email')
def teste_email():
    sucesso = enviar_email(
        destinatario="smtp.gmail.com",
        assunto="Teste de envio Atestto",
        corpo_html="<h1>E-mail funcionando!</h1><p>Teste enviado via SMTP Outlook.</p>"
    )
    if sucesso:
        return "E-mail enviado com sucesso!"
    else:
        return "Erro ao enviar e-mail."
