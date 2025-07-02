from flask import Flask
from flask_mail import Mail, Message


app = Flask(__name__)
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False,
    MAIL_USERNAME='fgiovanna16@gmail.com',  
    MAIL_PASSWORD='wxiotfjtmeexmosf',      
    MAIL_DEFAULT_SENDER='fgiovanna16@gmail.com'
)

mail = Mail(app)


with app.app_context():
    print("MAIL_USERNAME:", app.config['MAIL_USERNAME'])
    print("MAIL_PASSWORD está definido:", bool(app.config['MAIL_PASSWORD']))

    msg = Message(
        subject="Teste de envio de e-mail - Atestto",
        recipients=["fgiovanna16@gmail.com"],  
        body="Se você recebeu este e-mail, o envio está funcionando com Flask-Mail e Gmail SMTP!"
    )
    mail.send(msg)
    print("✅ Email enviado com sucesso!")
