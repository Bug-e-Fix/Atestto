from flask import Flask
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from dotenv import load_dotenv

from app.extensions import csrf  # Só importa csrf, remove mail
from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.assinatura import assinatura_bp
from app.routes.teste_email import teste_email_bp
from app.models.user import get_user_by_id, apagar_usuarios_nao_confirmados
from app.services.email_service import enviar_email

load_dotenv()

scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['CONVERTED_FOLDER'] = 'converted'
    app.config['SIGNED_FOLDER'] = 'signed'

    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    # Remove mail.init_app(app) — não usa Flask-Mail mais

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

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assinatura_bp)
    app.register_blueprint(teste_email_bp)

    app.enviar_email = enviar_email  # função do seu email_service.py

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5050)
