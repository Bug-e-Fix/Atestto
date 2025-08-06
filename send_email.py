from flask import Flask
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configura o Flask-Mail com variáveis de ambiente
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't']
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

mail = Mail(app)

def enviar_email(destinatario, assunto, corpo_html):
    """Função para enviar um e-mail com Flask-Mail."""
    try:
        msg = Message(
            subject=assunto,
            recipients=[destinatario],
            html=corpo_html,
            sender=app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

# Bloco principal para executar o envio
if __name__ == '__main__':
    with app.app_context():
        print("Tentando enviar e-mail...")
        enviado = enviar_email(
            destinatario='fgiovanna16@gmail.com',  # <-- Mude aqui!
            assunto='Teste de envio - Atestto',
            corpo_html='<p>Olá! Este é um teste de envio de e-mail com Flask-Mail 🎉</p>'
        )
        print("Resultado:", "Sucesso" if enviado else "Falhou")