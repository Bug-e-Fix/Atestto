from flask import Flask, render_template
from flask_apscheduler import APScheduler
from flask_wtf.csrf import CSRFError, generate_csrf
from flask_mail import Mail
from dotenv import load_dotenv
import os
from app.extensions import csrf, login_manager
from app.models.user import User  

load_dotenv()

from app.extensions import csrf
from app.routes.dashboard import dashboard_bp
from app.routes.assinatura import assinatura_bp
from app.routes.teste_email import teste_email_bp
from app.services.email_service import enviar_email
from app.models.user import apagar_usuarios_nao_confirmados
from app.routes.auth import auth_bp


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

csrf.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # rota usada para redirecionar ao login

# Registro de rotas etc
from app.routes.auth import auth_bp
app.register_blueprint(auth_bp)

mail = Mail()
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)

    # Carrega configuração padrão (ex: SECRET_KEY)
    app.config.from_object('config.Config')

    # Segurança
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise RuntimeError("Falta definir SECRET_KEY no .env")
    app.secret_key = secret_key

    # Pastas para arquivos
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['CONVERTED_FOLDER'] = 'converted'
    app.config['SIGNED_FOLDER'] = 'signed'

    # Configurações de e-mail protegidas
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    mail.init_app(app)

    # Proteção CSRF
    csrf.init_app(app)

    # Agendador
    scheduler.init_app(app)
    scheduler.start()

    def job_apagar_usuarios():
        with app.app_context():
            apagar_usuarios_nao_confirmados(expiracao_horas=24)

    scheduler.add_job(
        id='limpar_usuarios_nao_confirmados',
        func=job_apagar_usuarios,
        trigger='interval',
        hours=24
    )

    # Blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assinatura_bp)
    app.register_blueprint(teste_email_bp)
    app.register_blueprint(auth_bp)

    # Serviço de e-mail disponível em toda a app
    app.enviar_email = enviar_email

    # Rota padrão
    @app.route('/')
    def index():
        return "<h1>Bem-vinda à Atestto!</h1><p>Login e cadastro incluidos</p>"

    # Tratamento de erro CSRF
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('csrf_error.html', reason=e.description), 400

    # Injeta token CSRF nos templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5050)
