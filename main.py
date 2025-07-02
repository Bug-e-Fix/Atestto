from flask import Flask
from flask_login import LoginManager
from flask_apscheduler import APScheduler

from app.routes.auth import auth_bp
from app.routes.dashboard import dashboard_bp
from app.routes.assinatura import assinatura_bp
from app.models.user import get_user_by_id, apagar_usuarios_nao_confirmados
from app.extensions import mail

scheduler = APScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['CONVERTED_FOLDER'] = 'converted'
    app.config['SIGNED_FOLDER'] = 'signed'

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    mail.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(assinatura_bp)

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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5050)
