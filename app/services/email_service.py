import smtplib
from email.message import EmailMessage

smtp_server = "smtp.office365.com"
port = 587
sender_email = "conta_da_aplicacao@outlook.com"  # Conta SMTP usada para autenticar
sender_password = "senha_da_conta"

def enviar_email(destinatario, assunto, corpo):
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = destinatario
    msg['Subject'] = assunto

    # Texto alternativo simples (para clientes que não exibem HTML)
    texto_alternativo = "Por favor, visualize este email em um cliente que suporte HTML."

    msg.set_content(texto_alternativo)
    msg.add_alternative(corpo, subtype='html')  # corpo em HTML

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
