# main.py

from flask import Flask, redirect, url_for, render_template
from flask_apscheduler import APScheduler
from flask_wtf.csrf import CSRFError, generate_csrf
from dotenv import load_dotenv
from app.models.user import apagar_usuarios_nao_confirmados
import os

# Carrega .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

from app.extensions import csrf, login_manager, mail   # removido oauth
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise RuntimeError("SECRET_KEY not defined in .env file.")
    app.secret_key = secret_key

    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['CONVERTED_FOLDER'] = 'converted'
    app.config['SIGNED_FOLDER'] = 'signed'

    # E-mail
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

    if not app.config['MAIL_USERNAME'] or not app.config['MAIL_PASSWORD']:
        raise RuntimeError("MAIL_USERNAME or MAIL_PASSWORD not configured in .env.")

    # Inicialização das extensões
    mail.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Scheduler
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
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.assinatura import assinatura_bp
    from app.routes.public import public_bp
    from app.routes.google_auth import google_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assinatura_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(google_bp, url_prefix="/login/google")

    # Email service
    from app.services.email_service import enviar_email
    app.enviar_email = enviar_email

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('csrf_error.html', reason=e.description), 400

    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5050)
